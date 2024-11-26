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

publish:
	-rm -rf dist
	python -m build
	twine upload dist/*

#bump:
#	python scripts/update_version.py -- type

release: test coverage build upload
