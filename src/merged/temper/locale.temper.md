# Locales

A locale bundles up information about how to display preferences.

    @json
    export class Locale(
      public language: String,
      public country: String,
      public variant: String | Null,
    ) {
      public toString(): String {
        let variant = this.variant;
        if (variant != null) {
          "${language}-{country}-{variant}"
        } else {
          "${language}-{country}"
        }
      }


*fromBcp47String* takes a [BCP 47 string](https://en.wikipedia.org/wiki/IETF_language_tag) and
returns a locale.
It's tolerant to differences between '-' and '_' as delimiters.
If there are two delimiters, the variant will be non null.

      public static fromBcp47String(s: String): Locale {
        let start = String.begin;
        var afterLanguage = start;
        let end = s.end;
        while (s.hasIndex(afterLanguage)) {
          let c = s[afterLanguage];
          if (c == char'-' || c == char'_') { break }
          afterLanguage = s.next(afterLanguage);
        }
        var beforeCountry = afterLanguage;
        if (s.hasIndex(beforeCountry)) {
          beforeCountry = s.next(beforeCountry);
        }
        var afterCountry = beforeCountry;
        while (s.hasIndex(afterCountry)) {
          let c = s[afterCountry];
          if (c == char'-' || c == char'_') { break }
          afterCountry = s.next(afterCountry);
        }
        var beforeVariant = afterCountry;
        if (s.hasIndex(beforeVariant)) {
          beforeVariant = s.next(beforeVariant);
        }

        let language = s.slice(start, afterLanguage);
        let country = s.slice(beforeCountry, afterCountry);
        let variant = if (afterCountry < beforeVariant) {
          s.slice(beforeVariant, end)
        } else {
          null
        };

        new Locale(language, country, variant)
      }

      public encodeToJson(p: JsonProducer): Void {
        p.stringValue(toString());
      }

      public static decodeFromJson(
        t: JsonSyntaxTree,
        ic: InterchangeContext,
      ): Locale | Bubble {
        Locale.fromBcp47String(t.as<JsonString>().content)
      }
    }

Here are some tests for Locale parsing and stringification.

    test("parsing and unparsing locales") {
      let enUs = Locale.fromIsoString("en-US");
      assert(enUs.language == "en");
      assert(enUs.country == "US");
      assert(enUs.variant == null);
      assert(enUs.toString() == "en-US");

      let enUs = Locale.fromIsoString("nan_Hant_TW");
      assert(enUs.language == "nan");
      assert(enUs.country == "Hant");
      assert(enUs.variant == "Tw");
      assert(enUs.toString() == "nan-Hant-Tw");
    }

For JSON interop:

    let {
      InterchangeContext,
      JsonProducer,
      JsonString,
      JsonSyntaxTree
    } = import("../json");
