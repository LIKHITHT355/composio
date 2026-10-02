.PHONY: all preflight check clean test run-baseline run-verify report help

PYTHON ?= python

help:
	@echo Available commands:
	@echo   make check        - Run preflight and schema validations
	@echo   make run-baseline - Run baseline pass extraction
	@echo   make run-verify   - Run verification and arbiter pass
	@echo   make report       - Generate final analytics and HTML case study
	@echo   make test         - Run pytest suite

check:
	$(PYTHON) tests/test_preflight.py

test:
	$(PYTHON) -m pytest tests/

clean:
	@echo Cleaning temporary files...
