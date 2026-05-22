SHELL := /bin/bash -l
export SHELL

VENV := ./vtmp/
export VENV

MIN_PYTHON_VERSION := $(shell basename $$( ls /usr/bin/python3.[0-9][0-9] | awk '{print $0; exit}' ) )
export MIN_PYTHON_VERSION

COMMON_VENV := rm -rf $(VENV); \
	$(MIN_PYTHON_VERSION) -m venv $(VENV); \
	source ./$(VENV)/bin/activate;

PIP_INSTALL := pip3 -q \
	--require-virtualenv \
	--disable-pip-version-check \
	--no-color install --no-cache-dir

# ==========================================
# Code formatting and checks
PY_FILES := *.py whoisdomain/
