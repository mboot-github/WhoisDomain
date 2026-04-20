# ==========================================================
include Makefile.inc
# ==========================================================

MYPY_INSTALL := \
	types-requests \
	types-python-dateutil

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
	$(PIP_INSTALL) -r requirements.txt mypy $(MYPY_INSTALL); \
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

t2:
	$(COMMON_VENV) \
	$(PIP_INSTALL) -r requirements.txt; \
	$(MIN_PYTHON_VERSION) t2.py 2>$@.2 | tee $@.1
