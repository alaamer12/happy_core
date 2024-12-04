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

clean:
	-Remove-Item -Recurse -Force docs\build



build-docs:
	cd docs && sphinx-build -b html source build/html

