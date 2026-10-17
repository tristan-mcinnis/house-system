# House System: the repository's own commands. See README.md.

.PHONY: help check test clean

help:
	@echo "make check   run the scrub gate (the gate)"

check test:
	sh tests/scrub.sh

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
