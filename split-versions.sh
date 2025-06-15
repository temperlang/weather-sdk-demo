#!/bin/bash

set -e
# We use ** below to iterate over all files under a directory.
shopt -s globstar

export VERSIONS="1 2 3"

pushd "$(dirname "$0")" >& /dev/null
export PROJECT_DIR="$PWD"
popd >& /dev/null

if ! [ -d "$PROJECT_DIR/src/merged" ]; then
    echo Cannot find project directory.
    echo Directory "'$PROJECT_DIR'" does not have a merged/ or v1/ sub-directory.
    exit -1
fi

pushd "$PROJECT_DIR/src/merged" >& /dev/null
# Operate from within src/merged.
# That way we don't have to strip off any path prefix.
for F in **/*; do
    if ! [ -f "$F" ]; then
        continue
    fi
    # Make sure the output directories exist
    export DIR="$(dirname "$F")"
    for V in $VERSIONS; do
        mkdir -p "$PROJECT_DIR/src/v$V/$DIR"
    done
    if ! (echo "$F" | egrep -q '[.]ppme$'); then
            # Just copy it into each version output directory
        for V in $VERSIONS; do
            cp "$F" "$PROJECT_DIR/src/v$V/$F"
        done
    else
        # $F ends with .ppme so preprocess it into each version output directory
        export F_NOSUFFIX="$(dirname "$F")/$(basename "$F" .ppme)"
        export OUT_FILE="$PROJECT_DIR/src/v$V/$F_NOSUFFIX"
        for V in $VERSIONS; do
            mcpp -e utf8 -N -P -Q \
                 -D SDK_VERSION="$V" \
                 -D 'LITERAL_HASH=#' -D 'PYCOMMENT(...)=LITERAL_HASH __VA_ARGS__' \
                 "$F" -o "$OUT_FILE"
            # Collapse adjacent blank lines into 1.
            # mcpp leaves a lot of them for #else blocks.
            perl -i -e '
                  my $blank = "";
                  my $seenNonEmpty = !1; # No blanks before first non-empty
                  while (<>) {
                    if ($_ =~ /[^\r\n]/) {
                      print "$blank$_";
                      $blank = "";
                      $seenNonEmpty = 1;
                    } elsif ($seenNonEmpty) {
                      $blank = $_; # Clobber blanks until we see a non-empty
                    }
                  }
                ' "$OUT_FILE"
            if ! [ -s "$OUT_FILE" ]; then
                # Make sure empty files get recognized as deleted
                git rm -f "$OUT_FILE"
            fi
        done
    fi
done
popd >& /dev/null
