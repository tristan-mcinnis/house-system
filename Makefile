# House System — the repository's own commands. See README.md.
PYTHON ?= python3

.PHONY: help check validate map test status clean

help:
	@echo "make status     Git state of every House child; exit 1 if work is only on this machine"
	@echo "make validate   validate catalog/catalog.yaml"
	@echo "make map        regenerate docs/system-map.md from the catalog"
	@echo "make test       run the unit tests and the scrub gate"
	@echo "make check      validate + map freshness + tests (the gate)"

validate:
	$(PYTHON) tools/validate_catalog.py

map:
	$(PYTHON) tools/build_system_map.py

test:
	$(PYTHON) -m unittest discover -s tests -t . -v
	sh tests/scrub.sh

status:
	$(PYTHON) tools/house_status.py

check: validate
	$(PYTHON) tools/build_system_map.py --check
	$(PYTHON) -m unittest discover -s tests -t .
	sh tests/scrub.sh

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
