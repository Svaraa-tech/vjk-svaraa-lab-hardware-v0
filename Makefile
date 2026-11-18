.PHONY: doctor setup test dev stop wokwi-build

doctor:
	@bash scripts/doctor.sh

setup:
	@bash scripts/setup.sh

test:
	@bash scripts/test.sh

dev:
	@bash scripts/dev.sh

stop:
	@bash scripts/stop.sh

wokwi-build:
	@bash scripts/wokwi_build.sh
