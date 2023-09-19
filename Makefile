# This file is part of Reus, see <https://github.com/MestreLion/reus>
# Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
# -----------------------------------------------------------------------------

# For customizing defaults, such as PYTHON
-include .env

## SLUG: Short project name
SLUG     ?= reus
## EXEC: Basename of the main project executable, most likely $(SLUG)
EXEC     ?= reus-fish-calculator
## PYTHON: System python, used to create the virtual environment
PYTHON   ?= python3
## ENV_DIR: Path to the virtual environment, absolute or relative to current dir
ENV_DIR  ?= venv

# Derived vars:
# path to virtual environment bin dir
venv    := $(ENV_DIR)/bin
# path to virtual environment python executable
python  := $(venv)/python
# path to virtual environment pip executable
pip     := $(venv)/pip
# path to the project executable
exec    := $(venv)/$(EXEC)
# -----------------------------------------------------------------------------

## - default: format and check
default: format check

## - run: run project
# alternative: exec $(python) -m $(SLUG)
run: venv
	exec $(exec)

## - style: apply `black` formatter
format: venv
	$(venv)/black .

## - check: invoke `mypy` static type checker
check: venv
	$(venv)/mypy

## - build: build sdist and wheel packages using PyPA's `build` module
build: venv default
	$(python) -m build

## - upload: upload built packages to PyPI using `twine`
# Must add project to ~/.pypirc
upload: venv build
	$(venv)/twine upload --repository $(SLUG) -- dist/*

$(ENV_DIR)/done: pyproject.toml
	$(PYTHON) -m venv $(ENV_DIR)
	$(python) -m pip --disable-pip-version-check install --upgrade pip
	$(pip) install --upgrade -e .[dev,publish]
	touch -- $@

.PHONY: default run format check build upload
# -----------------------------------------------------------------------------

## - venv: create a virtual environment in $ENV_DIR, by default `./venv`
venv: $(ENV_DIR)/done

## - venv-clean: remove the virtual environment
venv-clean:
	rm -rf $(ENV_DIR)

## - python: run Python interactive interpreter
python: venv
	exec $(python)

## - ipython: run IPython interactive interpreter
ipython: $(venv)/ipython
	exec $(venv)/ipython

## - bash: run bash subshell in the virtual environment
bash: venv
	. $(venv)/activate && exec bash

## - clean: remove build artifacts
clean:
	rm -rf *.egg-info

## - clean-all: remove build artifacts and the virtual environment
clean-all: clean venv-clean

## - help: display this message
help:
	@echo "Available env vars and targets:"
	@sed -n 's/^.*##[ ]//p' Makefile

$(venv)/%: | venv
	$(pip) install --upgrade $*
	touch -- $@

.PHONY: venv venv-clean python ipython bash clean clean-all help
