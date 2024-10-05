# Makefile

.PHONY: install test coverage build upload

install:
	pip install -e .[dev]

test:
	pytest

coverage:
	pytest --cov={{ package_name }} --cov-report=term-missing

build:
	python -m build

upload:
	twine upload dist/*

release: test coverage build upload
