#!/usr/bin/env python3

import os.path
import pathlib
import shutil
import sys

VERSIONS = [1, 2, 3]
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = pathlib.Path(PROJECT_DIR, 'src')
SRC_MERGED_DIR = pathlib.Path(os.path.join(SRC_DIR, 'merged'))
PPME_EXT = '.ppme'

def preprocess(in_file, out_file, env):
    """
    Read in_file and process it to out_file by looking for a subset of C preprocessor directives:

    #if CONDITION
    #elif CONDITION
    #else
    #endif

    It coalesces blank lines around the directives.

    CONDITIONs are passed to eval with env as the set of locals.
    """

    class ConditionStackFrame:
        def __init__(self, line_no, emit = False, seen_pass = False):
            self.line_no = line_no
            # True if we're emitting lines
            self.emit = emit
            # Helps ignore all elif/elses once we've seen a condition that passes.
            self.seen_pass = seen_pass

    # Pairs of line numbers and True to emit non pre-processor directive lines or false to drop.
    if_stack = [ConditionStackFrame(0, emit = True, seen_pass = True)]
    blank = '' # Hold onto blank lines so that we can coalesce them around directives
    seen_non_blank = False

    line_no = 0
    with open(in_file, 'r', encoding='utf-8') as file_handle:
        with open(out_file, 'w', encoding='utf-8') as out_handle:
            for line in file_handle:
                line_no += 1

                stripped_line = line.strip()

                # How to handle any pre-processor directives
                pop = False # True to pop the if_stack
                expr = None # Any condition expression

                if line.startswith('#if '):
                    # Push a new stack frame.
                    # The elif/else branches reuse the top frame from their #if.
                    if_stack.append(ConditionStackFrame(line_no))
                    expr = line[4:].strip()
                elif line.startswith('#elif '):
                    expr = line[6:].strip()
                elif line.startswith('#else'):
                    expr = 'True'
                elif line.startswith('#endif'):
                    if len(if_stack) <= 1:
                        raise Exception(f'No open #if at {in_file}:{line_no}: {stripped_line}!')
                    if_stack.pop()
                    continue
                elif if_stack[-1].emit: # Not excluded by #if
                    if stripped_line == '':
                        blank = line
                    else:
                        # If we delayed an empty line above,
                        # output it.
                        # Ignore blanks at the start.
                        if seen_non_blank:
                            out_handle.write(blank)
                        # Output the non-blank line.
                        out_handle.write(line)
                        blank = ''
                        seen_non_blank = True
                popped_true = False
                if expr is not None:
                    if len(if_stack) <= 1:
                        raise Exception(f'No open #if at {in_file}:{line_no}: {stripped_line}!')
                    # The frame that the top inherits from and the top frame for which we're
                    # evaluating the condition.
                    (inh_frame, top_frame) = if_stack[-2:]
                    try:
                        result = (
                            # If the current line is ignored because of an inherited condition,
                            # don't bother evaluating the condition
                            inh_frame.emit and
                            # If we already had a passing condition, don't bother with else conditions
                            not top_frame.seen_pass and
                            eval(expr, locals=env)
                        )
                    except SyntaxError:
                        print(f'Error at {in_file}:{line_no}: {stripped_line}!')
                        raise
                    if not isinstance(result, bool):
                        print(f'Error at {in_file}:{line_no}: {stripped_line}!')
                        raise TypeError(result, bool)
                    top_frame.emit = result
                    if result:
                        top_frame.seen_pass = True
            # Check that all #if directives were closed
            if len(if_stack) > 1:
                raise Exception(
                    f'Unclosed #if at {in_file}:{[frame.line_no for frame in if_stack[1:]]}'
                )

def process_one_file(f):
    """
    Process one file from src/merged into the version directories under src.
    """

    rel_f = f.relative_to(SRC_MERGED_DIR)
    rel_dir = os.path.dirname(rel_f)
    had_ext = False
    if f.name.endswith(PPME_EXT):
        rel_f = pathlib.Path(os.path.join(rel_dir, f.name[:-len(PPME_EXT)]))
        had_ext = True

    # Make sure the output directories exist
    for v in VERSIONS:
        pathlib.Path(os.path.join(SRC_DIR, f'v{v}', rel_dir)).mkdir(parents=True, exist_ok=True)

    out_files = [(v, os.path.join(SRC_DIR, f'v{v}', rel_f)) for v in VERSIONS]

    if not had_ext:
        # Just copy it into each version output directory
        for (_, out_file) in out_files:
            shutil.copy(f, out_file)
    else:
        # f ends with .ppme so preprocess it into each version output directory
        for (v, out_file) in out_files:
            env = {
                'SDK_VERSION': v
            }
            preprocess(f, out_file, env = env)
            if os.path.getsize(out_file) == 0:
                # Make sure empty files get recognized as deleted
                subprocess.run(['git', 'rm', '-f', out_file], check = true)

if __name__ == '__main__':
    for f in pathlib.Path(os.path.join(PROJECT_DIR, 'src', 'merged')).rglob('**/*'):
        if f.is_file() and not f.name.endswith('~'):
            process_one_file(f)
