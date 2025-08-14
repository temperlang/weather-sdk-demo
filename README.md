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

## Demo Script

slide 0

> Temper translates into all the other programming languages.
> A team using it can produce libraries for every language community.
>
> This makes it perfect for Web SDKs.
>
> First, What is a Web SDK?  An SDK, a software development kit, is just a
> library that lets a program use some service.
>
> A Web SDK is an SDK that connects to a micro-service.

slide 1

> This is the core problem with SDKS: to support clients using one more
> programming language you need a lot of effort.  This leads to lost partnerships
> poorly integrated systems, and high maintenance costs.

> Temper reduces development and maintenance costs for SDKs and,
> strangely, cloud billing costs.

slide 2

> I'm going to explain here:
>
> - How SDKs suffer from language multiplicity, the problem Temper solves.
> - Demo features that enable SDKs: namely async & HTTP support, and auto-encoding.
> - Show how a single source of truth for SDKs makes them easier to
>   write, evolve, deprecate, and maintain.
> - Explain how representing your endpoints in terms of bog standard classes
>   makes it easier for partners and clients to integrate.
> - How sharing types and logic between services and clients reduces
>   cloud billing, and extends type guardrails across network gaps.

VSCode: show sdk.temper.md

> Here's Temper code in VSCode.
> It defines an SDK for a Weather Service.
>
> Clients can call *getWeather* to get the weather.
>
> It takes the location and a locale which determines whether
> to show the user expects Celsius or Fahrenheit.

VSCode: show display.temper.md

> Over here, we've got some display logic that uses the locale.
> DisplayInfo is a bundle of data about how to display weather.
>
> We look at the country code and pick the display preferences.
>
> And there's also logic that handles other display tasks:
>
> Formatting numeric temperatures without too many digits.
> Numbers are represented as binary, so conversion to decimal
> can go wrong.  Here, we do carefully round the precise
> temperature to get numbers that render nicely across devices.
>
> And farther down are icons: emojis that give quick pictorial
> representations of weather conditions: snowflakes, clouds, sun emojis.
> And whether it's shorts weather or you need a brollie.
>
> This is simple demo code, but you can imagine that a weather
> service might need quite a bit of logic to capture how to present
> weather conditions in a way that fits their culture.
>
> Every client shouldn't have to reimplement this display logic.
> That's the whole point of providing a service and an SDK.

VSCode: show v1/weather.temper.md

> Here, we define two types: *WeatherRequest* and *WeatherResponse*.
>
> The service decodes requests, creates a response and then sends
> that back to the client.  The Web SDK's getWeather function
> takes care of encoding a request for the client and decoding the
> response.
>
> These classes have an `@json` decoration.
> Temper generates code that converts them to and from JSON.
> So you get JSON interop without having to do a lot of work.
>
> The response type has that bundle of display information I showed you.
>
> It's rather large though.
> But Temper translates to all the languages, so what if we skip
> sending it, and instead compute it on the client side.
> Once we can share logic, we can move running it from one place to another.
>
> Up here, we've tagged our request with a version number.
> Let's look at version 2 which trims down the JSON.

VSCode: show v2/weather.temper.md

> Here's version 2.
> The main difference: the *WeatherResponse* does not include the display
> information.  Instead the class definition defines the *displayInfo*
> property as a getter.  The display info is not computed on the
> server and sent to the client.  Instead it's just computed on the
> client, as needed.
>
> Let's see how that changes things.

Shell.  Tab with server running.

> I've got a server running here.

Back to VSCode, server.py

> It's a simple python server.  Let me show you the code.
> Up at the top it imports the python translation of the Temper.
>
> Farther down is all the GET/POST unpacking.
>
> It uses the auto-derived JSON adapters to decode requests and encode responses.
>
> I'll come back and show how it processes requests, but first let's just
> see it in action.

Shell.  Fresh tab.

`$ curl -X POST http://localhost:10003/weather -H 'Content-Type: application/json' -d '{"version":1,"location":"08540","locale":"en_US"}'`

> I'm asking for the weather in central New Jersey.  With a US English locale.
>
> And I get back a long response.  The display info, as you can see, is the bulk of it.

Edit `en_US` to `fr_FR`.

> If I switch to french, I get Fahrenheit.  Our display logic determines temperature presentation, but it is very long.

Edit version to 2.

> If I flip that version number to 2 though, we get something much shorter.
>
> That saves bytes on the wire.  The server also does less work.
> We're paying less in cloud bills and both the server and client are
> spending less on bandwidth and less time packing and unpacking
> bytes.

VSCode: src/v3/weather.temper.md

> That one server was able to both handle v1 and v2 requests because
> it's actually a v3 server.
>
> Its weather request is a `sealed interface`.  A discriminated union.
>
> That's a bit of programming language jargon.
> A discriminated union is a type that works with case based reasoning.
> It's one of this small number of variants, so if
> your code covers all the cases, it won't be surprised.
>
> And here are the two variants: OldWeatherRequest and NewWeatherRequest.
>
> And these `@jsonExtra` notations mean that the JSON representations of
> them differ by the version numbers.
>
> WeatherRequest is an abstract type, but its JSON adapter is smart
> enough to know that if the version number is 1, it should delegate
> JSON decoding to OldWeatherRequest's JSON adapter.
>
> Let's see what the server does with that.

VSCode: src/v3/py/serve.py line 100

> Here in our python server, we ask whether we got a new or old style
> request.
>
> `isinstance` is the Python way of asking if a value is in a class.
>
> We used the WeatherRequest interface's JSON adapter to decode
> the JSON, and Temper classes translate to Python classes.
>
> So this Python type check works to figure out which version of the
> SDK the request came from.
>
> If it's a version 1 request, we compute the display info,
> using the shared Temper display logic.
> If it's a version 2 request, we don't compute it. The client
> has the getter that computes it as needed.

Back to shell curls

> You can see here why we got different request bodies here when
> all we did was change the version number.
>
> We've sucessfully migrated our wire format while remaining backwards
> compatible.  This'll save bytes on the wire and in cloud fees,
> and we didn't have to write a bunch of custom logic.
>
> It's just bog standard classes and interfaces and idiomatic Python
> type predicates.

----

> We've seen how the server works.
> Now, let's look at it from the clients point of view.

Tab with `temper repl -b java -w src/v2`

> I ran `temper repl -b java`.
> "R E P L", read eval print loop, allows interactively exploring
> Temper libraries.
>
> The "dash-b java" means specifically the Java 17 backend.
> We've got deep toolchain integration so the Java backend knows how
> to fire up a Java REPL.
>
> Here you can see it's fired up `jshell` with the Temper translations
> of the SDK library pre-loaded.
>
> I'm going to use the SDK from Java.
> I need a location and a locale
>
> Let's stick with central New Jersey, and US english.

var location = "08540"
var locale = new weather_sdk.Locale("en", "US", null)

> And I'll invoke the SDK, giving it those two inputs, and, since

var promise = weather_sdk.WeatherSdkGlobal.getWeather(location, locale)
promise.get()

> Ack. Live demos suck. I'm running the service locally, but it's trying
> to go to some default location.

Add to end ` , "http://localhost:10003" `

> The getWeather method does some logging to make the demo easier.
> So it looks like it worked this time.  Here's the JSON I got back.
> No displayInfo because this is a version 2 client.
> Web APIs are asynchronous, so the SDK gives back a promise.

promise.get()

> In Java, they're called futures or CompletableFutures. Temper types
> connect to the native language type where possible.

> And if I unwrap the promise I get a WeatherResponse.
> An instance of the Java translation of the Temper type.

var response = promise.get()
var displayInfo = promise.get().getDisplayInfo()
displayInfo.getTemperatureString()

> Even though the precise temperature formats badly in decimal,
> we've got a nice string representation with locale-appropriate units
> nicely formatted thanks to the display logic that we wrote once
> in Temper and didn't need to write in Java.

displayInfo.getWeatherIcon()

> And the other display features work too.

> The SDK is nice, and type safe.  The Python server created a
> WeatherResponse class instance, and the Java gets a WeatherResponse
> class instance backed by the same logic.
>
> We've extended type guardrails across the network gap between the
> Python and the Java.

> And since it's a rich class, we can add more bells and whistles to
> our SDK and only pay, in bytes, for the ones that require intrinsically
> new data.
> We've avoided the JSON god-record problem.

> And Temper also supports other languages: C#, Lua, Rust, and
> JavaScript, and more coming.

slide 4

> Your clients and partners might need to connect to you from many
> languages, and when your service description is just defined based
> on plain old classes and interfaces, you can provide a nice programming
> experience, migrate services to be efficient on the wire, and flexibly
> deprecate and migrate.

> Oh, lets look at documentation.

Tab in weather_sdk

`cd src/v2/temper.out/java/weather-sdk`
`mvn install`

> I'm cd-ing into the Temper output directory for the Java translation.

`mvn install`

> Now, I'm building the weather sdk.  Temper produces not just translated
> source files, but we also produce all the build metadata files you need.
> So there's a POM here.

Point to "T E S T S"

> Oh, you can see it ran tests.  We translate Temper tests into junit tests.
> So you get confidence in the translation, and your CI/CD system will just
> pick up the test roots and surface the test results in your test dashboard.

Point to "Installing ...-javadoc.jar"

> That's the one we want.  I'm goint to unpack that and show you the docs
> you could give to users of the Java version of your SDK.

`mkdir /tmp/jdoc; cd /tmp/jdoc`

Copy the jar path and `jar xf ...` it.

`open index.html`

> And here it is in my browser.
> Let me navigate to DisplayInfo

> You can see that the fields here are documented. "Cloudy is true when"
> Let's compare that to the Temper definition of DisplayInfo.

VSCode: display.temper.md

> You can see that that documentation comes from the commentary here.
> We focus on deep toolchain integration.

> Temper understands languages.
> Our backends know the target language, but also how to package libraries,
> run tests, and represent ancillary content like doc comments.

slide 3

> I showed Python and Java exchanging JSON without writing any
> packing or unpacking code: just the same type definitions on
> both sides of a pipe.
>
> I just showed you how that lets us evolve a web service.

> I showed using Java's shell to call the SDK, a simple Java function
> to get a response object from the Python server.
> It's a rich class, so it has state and behaviour the way a good
> library should.

> And I showed that our toolchain integration is deep.
> When I built the java to get at the documentation JAR, the documentation
> has the commentary from the Temper code in a form that Java developers
> are used to.
> And our Java translation included test code that run as junit tests.

> Temper lets a small team write a library, in this case, an SDK, once
> and then that SDK can support many language communities.

> Most of the Python server code, except for fetching conditions from
> the weather database, was actually also translated from Temper, so
> it gives you a leg up on building your web service too.

> Temper makes developers much more productive.
> To write an SDK with N features for M client languages, you'd need
> N TIMES M developer effort, but with Temper you just need N.
> Temper makes everyone more productive.
>
> So SDKs are just one use case for Temper, but more broadly, Temper
> helps anywhere a library would be useful in more than one language.

> Thanks for listening, and hit me up if you're interested in this.

