# weather-sdk-demo

This demo outlines an SDK for a micro-service that answers questions about the weather.

## Goals

It's meant to demonstrate:

- how Temper translating to many programming languages makes it easier to craft SDKs
  for clients written in many programming languages, and
- how having rich classes lets us make the SDKs easier to use and more feature rich, and
- how having the ability to run code, before a request is sent and after the response is
  received, makes it easier to deprecate features and evolve the wire representation.

## File layout for multiple SDK versions

To that end, there are multiple versions of the source files.
The directory structure looks like

    ┃
    ┣━split-versions.py
    ┃
    ┗━src/
      ┃
      ┣━merged/
      ┃
      ┣━v1/
      ┃
      ┣━v2/
      ┃
      ┗━v3/

Do not edit code under the version directories manually.
The version directories, `v1/` etc. are regenerated from `merged` by `./split-versions.py`.

## What split-versions does

For each file under merged that ends with `.ppme` (pre-process me),
the `./split-versions.sh` script runs it through a pass that recognizes C-preprocessor
style `#if`/`#elif`/`#endif` directives.
It does this once for each version, putting the output under the appropriate `v`{number} directory.

It's roughly equivalent to the below.

```sh
mcpp -e utf8 -D SDK_VERSION=1 src/merged/<path>.ppme src/v1/<path>.ppme
```

Since *SDK_VERSION* is a counting number, you can use preprocessor directives like

```c
#if SDK_VERSION == 1
...
#elif SDK_VERSION == 2
...
#endif
```

You can also use range checks.

```c
#if SDK_VERSION >= 2
...
#endif
```

If a file, after pre-processing is empty, it is deleted and `./split-versions.py` removes
it from that versions file tree.  It also runs `git rm -f` on any empty files so that
committing newly empty version files will recognize the change.

## Differences between versions

### v1

**v1** is the most basic SDK.  It has a *WeatherRequest* class in Temper and a
*WeatherResponse* class.
Neither has much logic but both use `@json` to allow sending across the wire.

The service, written in Python, computes all the details the client could need,
so *WeatherResponse* is fairly large.

There are three clients:

- A JavaScript client that uses Web *fetch* APIs to connect to the server.
  It displays information about the temperature, the emoji representation,
  and whether its tshirt or jacket weather.
- A Java web server that provides the same information using server side
  rendering.
- A Rust command line app that does the same.

### v2

**v2** has those same request/response types, but most of the logic has
moved out of the service.  Now, presentation logic is in those types, and
so doesn't need to be on the wire.

The wire format is much simplified.
Extra features can be added just by library updates.

### v3

**v3** has a service that reacts with either an old or new style response
based on a version in the request allowing interop between old and new clients.

It shows how centralizing the presentation logic simplifies copying values into
the old style, verbose response.
