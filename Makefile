# ==========================================================
SHELL := /bin/bash -l
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
PY_FILES := *.py whoisdomain/

# LINE_LENGTH := 160

MYPY_INSTALL := \
	types-requests \
	types-python-dateutil redis tld

COMMON_VENV := rm -rf $(VENV); \
	$(MIN_PYTHON_VERSION) -m venv $(VENV); \
	source ./$(VENV)/bin/activate;

# --------------------------------------------------
# reformat, lint and verify basics
# --------------------------------------------------
prep: clean format check mypy

clean:
	rm -rf tmp/* 1 2 out *.out *.1 *.2
	rm -rf $(VENV)
	rm -f ./rl-secure-list-*.txt
	rm -f ./rl-secure-status-*.txt

format:
	ruff format $(PY_FILES)

check:
	ruff check --fix $(PY_FILES)

mypy:
	$(COMMON_VENV) \
	$(PIP_INSTALL) mypy $(MYPY_INSTALL); \
	mypy \
		--strict \
		--no-incremental \
		$(PY_FILES) | tee $@.out

# this step creates or updates the toml file
build:
	./bin/build.sh
	./bin/testLocalWhl.sh 2>tmp/$@.22 | tee tmp/$@.1
	./bin/test.sh 2>tmp/$@.2 | tee -a tmp/$@.1

test:
	make -f Makefile.tests
