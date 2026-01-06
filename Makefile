# ==========================================================
# ==========================================================
# https://docs.secure.software/cli

SHELL 		:= /bin/bash -l
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
PY_FILES := *.py bin/*.py whoisdomain/

LINE_LENGTH := 160
PL_LINTERS := eradicate,mccabe,pycodestyle,pyflakes,pylint

# C0114 Missing module docstring [pylint]
# C0115 Missing class docstring [pylint]
# C0116 Missing function or method docstring [pylint]
# E203 whitespace before ':' [pycodestyle]

PL_IGNORE := C0114,C0115,C0116,E203

MYPY_INSTALL := \
	types-requests \
	types-python-dateutil redis tld

COMMON_VENV := rm -rf $(VENV); \
	$(MIN_PYTHON_VERSION) -m venv $(VENV); \
	source ./$(VENV)/bin/activate;

WHAT 		:= whoisdomain
DOCKER_WHO	:= mbootgithub

TEST_OPTIONS_ALL = \
	--withPublicSuffix \
	--extractServers \
	--stripHttpStatus

.PHONY: TestSimple TestSimple2 TestAll clean

first: prep test1 test2 test3 # test4

# --------------------------------------------------
# reformat, lint and verify basics
# --------------------------------------------------
prep: clean black pylama mypy

clean:
	rm -rf tmp/* 1 2 out *.out *.1 *.2
	rm -rf $(VENV)
	rm -f ./rl-secure-list-*.txt
	rm -f ./rl-secure-status-*.txt
	# docker container prune -f
	# docker image prune --all --force
	# docker image ls -a

black:
	$(COMMON_VENV) \
	$(PIP_INSTALL) black; \
	black \
		--line-length $(LINE_LENGTH) \
		$(PY_FILES)

pylama:
	$(COMMON_VENV) \
	$(PIP_INSTALL) setuptools pylama; \
	pylama \
		--max-line-length $(LINE_LENGTH) \
		--linters "${PL_LINTERS}" \
		--ignore "${PL_IGNORE}" \
		$(PY_FILES) || exit 0

mypy:
	$(COMMON_VENV) \
	$(PIP_INSTALL) mypy $(MYPY_INSTALL); \
	mypy \
		--strict \
		--no-incremental \
		$(PY_FILES)

# --------------------------------------------------
# Tests
# --------------------------------------------------

test1:
	./test1.py | tee tmp/$@.1

# test2 has the data type in the output
test2:
	./test2.py -f testdata/DOMAINS.txt 2>tmp/$@.2 | tee tmp/$@.1

# test3 simulates the whoisdomain command and has no data type in the output
test3:
	./test3.py -f testdata/DOMAINS.txt 2>tmp/$@.2 | tee tmp/$@.1

test4:
	LOGLEVEL=DEBUG ./test2.py $(TEST_OPTIONS_ALL) -t 2>tmp/$@.2 | tee tmp/$@.1

test_with: withPublicSuffix withExtractServers stripHttpStatus

withPublicSuffix:
	./test2.py -d  www.dublin.airport.aero --withPublicSuffix

withExtractServers:
	./test2.py -d google.com --extractServers

stripHttpStatus:
	./test2.py -d nic.aarp --stripHttpStatus
	./test2.py -d nic.abudhabi --stripHttpStatus
	./test2.py -d META.AU --stripHttpStatus
	./test2.py -d google.AU --stripHttpStatus

# test using python 3.6
zz:
	docker build -t df36 -f Df-36 .
	docker run -v .:/context df36 -d google.com

# --------------------------------------------------
# build related
# --------------------------------------------------

# this step creates or updates the toml file
build: first
	./bin/build.sh
	./bin/testLocalWhl.sh 2>tmp/$@.22 | tee tmp/$@.1
	./bin/test.sh 2>tmp/$@.2 | tee -a tmp/$@.1

# ==========================================================
# build docker images with the latest python and run a test -a
dockerTests: docker dockerRunLocal dockerTestdata

testdocker:
	export VERSION=$(shell cat work/version) && \
	docker build \
		--build-arg VERSION \
		--tag $(DOCKER_WHO)/$(WHAT)-test \
		--tag $(DOCKER_WHO)/$(WHAT)-$${VERSION}-test \
		--tag $(WHAT)-$${VERSION}-test \
		--tag $(WHAT)-test \
		-f Dockerfile-test .
	docker image ls
	docker container ls
	docker run whoisdomain-test -t $(TEST_OPTIONS_ALL)

testdockerTestdata:
	@export VERSION=$(shell cat work/version) && \
	docker run \
		-v ./testdata:/testdata \
		$(WHAT)-$${VERSION}-test \
		-f /testdata/DOMAINS.txt $(TEST_OPTIONS_ALL) 2>tmp/$@-2 | \
		tee tmp/$@-1

docker:
	export VERSION=$(shell cat work/version) && \
	docker build \
		--build-arg VERSION \
		--tag $(DOCKER_WHO)/$(WHAT) \
		--tag $(DOCKER_WHO)/$(WHAT)-$${VERSION} \
		--tag $(WHAT)-$${VERSION} \
		--tag $(WHAT) \
		-f Dockerfile .

dockerRunLocal:
	export VERSION=$(shell cat work/version) && \
	docker run \
		-v ./testdata:/testdata \
		$(WHAT)-$${VERSION} \
		-d google.com -j | jq -r .

dockerTestdata:
	@export VERSION=$(shell cat work/version) && \
	docker run \
		-v ./testdata:/testdata \
		$(WHAT)-$${VERSION} \
		-f /testdata/DOMAINS.txt $(TEST_OPTIONS_ALL) 2>tmp/$@-2 | \
		tee tmp/$@-1

dockerPush:
	export VERSION=$(shell cat work/version) && \
	docker image push \
		--all-tags $(DOCKER_WHO)/$(WHAT)
	docker run mbootgithub/whoisdomain -d google.com -j | jq -r .

# ====================================================
# uploading to pypi an pypiTestUpload
# build a test-mypi and download the image in a venv ane run a test
pypiTest: pypiTestUpload testTestPypi testdocker testdockerTestdata

# this is only the upload now for pypi builders
pypiTestUpload:
	./bin/upload_to_pypiTest.sh

testTestPypi:
	./bin/testTestPyPiUpload.sh 2>tmp/$@-2 | tee tmp/$@-1

releaseTest: build pypiTestUpload testTestPypi

release: pypi

# this is for pypi owners after all tests have finished
pypi:
	./bin/upload_to_pypi.sh
