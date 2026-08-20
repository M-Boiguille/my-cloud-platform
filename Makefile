.PHONY: lint test check install

lint:
	@bash scripts/lint.sh

test:
	@bash scripts/test.sh

check: lint test

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e ".[dev]"
