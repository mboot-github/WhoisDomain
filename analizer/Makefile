# Makefile tab=tab,ts=4
# ==========================================

SHELL := /bin/bash
export SHELL

VENV := ./vtmp/
export VENV

# tested on 3.10-3.14
MIN_PYTHON_VERSION := $(shell basename $$( ls /usr/bin/python3.[0-9][0-9] | awk '{print $0; exit}' ) )
export MIN_PYTHON_VERSION

PIP_INSTALL := pip3 -q \
	--require-virtualenv \
	--disable-pip-version-check \
	--no-color install --no-cache-dir

# ==========================================
# Code formatting and checks
PY_FILES := *.py

MYPY_INSTALL := \
	types-requests \
	types-python-dateutil \
	spectra-assure-sdk

COMMON_VENV := rm -rf $(VENV); \
	$(MIN_PYTHON_VERSION) -m venv $(VENV); \
	source ./$(VENV)/bin/activate;

.PHONEY: clean prep

# ==========================================

all: clean prep test

# ---------------------------
clean: cleanupVenv
	rm -f *.1 *.2 *.log *.tmp  1 2
	rm -rf .mypy_cache
	# rm -f IanaDb.sqlite # dont remove during testing
	rm -rf .iana_cache/ .psl_cache/

realclean: clean
	rm -f *.sqlite

# cleanup the virtual env
cleanupVenv:
	rm -rf $(VENV)

# ---------------------------
prep: format check

format:
	ruff format $(PY_FILES)

check:
	ruff check --fix $(PY_FILES)

# ---------------------------
test: IanaDb.sqlite
	$(COMMON_VENV) \
	$(PIP_INSTALL) -r requirements.txt ;\
		./investigateTld.py 2>2 | tee 1
		cat 2

IanaDb.sqlite:
	$(COMMON_VENV) \
	$(PIP_INSTALL) -r requirements.txt ;\
		./analizeIanaTld.py
