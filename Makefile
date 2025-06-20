help:
	@echo 'The TEMPER environment variable should point to the temper cli'
	@echo '`make build-all` builds all the Temper translations'
	@echo '`make serve-v1` starts the v1 server.'

build-all: v1 v2 v3

v1: split src/v1/tstamp
v2: split src/v2/tstamp
v3: split src/v3/tstamp

split: .split.tstamp

.split.tstamp: src/merged/temper/* src/merged/py/*
	./split-versions.py
	touch .split.tstamp

src/v1/tstamp: src/v1/temper/*.temper.md src/v1/py/*.py
	[ -n "$$TEMPER" ]
	"$$TEMPER" build -w src/v1 -ign /dev/null
	touch src/v1/tstamp

src/v2/tstamp: src/v2/temper/*.temper.md
	[ -n "$$TEMPER" ]
	"$$TEMPER" build -w src/v2 -ign /dev/null
	touch src/v2/tstamp

src/v3/tstamp: src/v3/temper/*.temper.md
	[ -n "$$TEMPER" ]
	"$$TEMPER" build -w src/v3 -ign /dev/null
	touch src/v3/tstamp

serve-v1: v1
	PYTHONPATH="src/v1/temper.out/py/std:src/v1/temper.out/py/std/temper_std:src/v1/temper.out/py/temper-core/temper_core:src/v1/temper.out/py/weather-sdk/weather_sdk:$$PYTHONPATH" python3 src/v1/py/serve.py

serve-v2: v2
	PYTHONPATH="src/v2/temper.out/py/std:src/v2/temper.out/py/std/temper_std:src/v2/temper.out/py/temper-core/temper_core:src/v2/temper.out/py/weather-sdk/weather_sdk:$$PYTHONPATH" python3 src/v2/py/serve.py

serve-v3: v3
	PYTHONPATH="src/v3/temper.out/py/std:src/v3/temper.out/py/std/temper_std:src/v3/temper.out/py/temper-core/temper_core:src/v3/temper.out/py/weather-sdk/weather_sdk:$$PYTHONPATH" python3 src/v3/py/serve.py
