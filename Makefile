# House System: the repository's own commands. See README.md.

.PHONY: help check test clean

help:
	@echo "make check   run the scrub gate and the usage tool tests"
	@echo "make test    same as make check"
	@echo "No build or install target: nothing here compiles or installs."

check test:
	sh tests/scrub.sh
	python3 -m unittest tests/test_house_usage.py

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
