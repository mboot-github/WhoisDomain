# ==========================================================
# ==========================================================
# https://docs.secure.software/cli

SHELL 		:= /bin/bash -l

RLSECURE 	:= ~/tmp/rl-secure/rl-secure
RLSTORE 	:= ~/

WHAT 		:= whoisdomain
DOCKER_WHO	:= mbootgithub

SIMPLEDOMAINS = $(shell ls testdata)

TEST_OPTIONS_ALL = --withPublicSuffix --extractServers --stripHttpStatus

# PHONY targets: make will run its recipe regardless of whether a file with that name exists or what its last modification time is.
.PHONY: TestSimple TestSimple2 TestAll clean

first: reformat mypy pylint testP39

testP39:
	./test1.py # now tests with python 3.9

#testP36:
#	docker build -t df36 -f Df-36 .
#	docker run -v .:/context df36 -d google.com

second: first test2 test3 test

test:
	LOGLEVEL=DEBUG ./test2.py $(TEST_OPTIONS_ALL) -t 2>2 | tee 1

test-all:
	LOGLEVEL=DEBUG ./test2.py $(TEST_OPTIONS_ALL) -a 2>2 | tee 1

t4:
	./t4.py 2>22 | tee out

# ==========================================================
# run a test sequence local only, no docker ,no upload to pypi
LocalTestSimple: reformat mypy test2

# ==========================================================
LocalTestWhl: build
	./bin/testLocalWhl.sh 2>tmp/$@-2 | tee tmp/$@-1

# this step creates or updates the toml file
build: first
	./bin/build.sh
	./bin/testLocalWhl.sh 2>2 | tee 1
	./bin/test.sh 2>2 | tee 1

# ==========================================================
# scan the most recent build and fail if the status fails
rlsecure: rlsecure-scan rlsecure-list rlsecure-status rlsecure-report rlsecure-version

rlsecure-scan:
	@export VERSION=$(shell cat work/version) && \
	$(RLSECURE) scan \
	--rl-store $(RLSTORE) \
	--purl mboot-github/$(WHAT)@$${VERSION} \
	--file-path dist/$(WHAT)-$${VERSION}*.whl \
	--replace \
	--no-tracking

rlsecure-list:
	@export VERSION=$(shell cat work/version) && \
	$(RLSECURE) list \
	--rl-store $(RLSTORE) \
	--show-all \
	--purl mboot-github/$(WHAT)@$${VERSION} \
	--no-color | tee rlsecure/list-$${VERSION}.txt

rlsecure-status:
	@export VERSION=$(shell cat work/version) && \
	$(RLSECURE) status \
	--rl-store $(RLSTORE) \
	--purl mboot-github/$(WHAT)@$${VERSION} \
	--show-all \
	--return-status \
	--no-color | tee rlsecure/status-$${VERSION}.txt

rlsecure-report:
	@export VERSION=$(shell cat work/version) && \
	$(RLSECURE) report \
	--rl-store $(RLSTORE) \
	--purl mboot-github/$(WHAT)@$${VERSION} \
	--format=all \
	--bundle=report-$(WHAT)-$${VERSION}.zip \
	--output-path ./rlsecure

rlsecure-version:
	@$(RLSECURE) --version

# ==========================================================
# build a docker images with the latest python and run a test -a
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

releaseTest: build rlsecure pypiTestUpload testTestPypi

# this is for pypi owners after all tests have finished
pypi:
	./bin/upload_to_pypi.sh

release: pypi

# ====================================================
# full test runs with all supported tld's

# test2 has the data type in the output
test2: reformat mypy
	./test2.py -f testdata/DOMAINS.txt 2> tmp/$@-2 | tee tmp/$@-1

# test3 simulates the whoisdomain command and has no data type in the output
test3: reformat mypy
	./test3.py -f testdata/DOMAINS.txt 2> tmp/$@-2 | tee tmp/$@-1

# ====================================================
# update the sqlite db with the latest tld info and psl info and suggest missing tld's we can add with a simple fix
suggest:
	( cd analizer; make ) | tee suggest.out

# black pylama and mypy on the source directory
format:
	./bin/reformat-code.sh

# black pylama and mypy on the source directory
reformat:
	./bin/reformat-code.sh

# only verify --strict all python code
mypy:
	mypy --strict *.py bin/*.py $(WHAT)

pylint:
	python -m pylint --recursive=y whoisdomain/ >pylint.txt

clean:
	rm -rf tmp/*
	rm -f ./rl-secure-list-*.txt
	rm -f ./rl-secure-status-*.txt
	docker container prune -f
	docker image prune --all --force
	docker image ls -a

cleanDist:
	rm -rf dist/*
	# rm -f work/version

zz:
	docker build -t df36 -f Df-36 .
	docker run -v .:/context df36 -d google.com

with: withPublicSuffix withExtractServers stripHttpStatus

withPublicSuffix:
	./test2.py -d  www.dublin.airport.aero --withPublicSuffix

withExtractServers:
	./test2.py -d google.com --extractServers

stripHttpStatus:
	./test2.py -d nic.aarp --stripHttpStatus
	./test2.py -d nic.abudhabi --stripHttpStatus
	./test2.py -d META.AU --stripHttpStatus
	./test2.py -d google.AU --stripHttpStatus
