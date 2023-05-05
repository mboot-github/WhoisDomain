# ==========================================================
# ==========================================================
# https://docs.secure.software/cli

SHELL 		:= /bin/bash -l

RLSECURE 	:= ~/tmp/rl-secure/rl-secure
RLSTORE 	:= ~/

WHAT 		:= whoisdomain
DOCKER_WHO	:= mbootgithub

SIMPLEDOMAINS = $(shell  ls testdata)

# PHONY targets: make will run its recipe regardless of whether a file with that name exists or what its last modification time is.
.PHONY: TestSimple TestSimple2 TestAll clean

# ==========================================================
# ==========================================================

# build a new whl file are run a test local only, no docker ,no upload to pypi
TestSimple: reformat mypy test2 test3 build

# build a test-mypi and download the image in a venv ane run a test
mypyTest: pypi-test testTestPypi

# build a docker images with the latest python and run a test -a
dockerTests: docker dockerRun dockerTestdata

# ==========================================================
# ==========================================================

# black pylama and mypy on the source directory
reformat:
	./bin/reformat-code.sh

# only verify --strict all python code
mypy:
	mypy *.py bin/*.py $(WHAT)

# this step creates or updates the toml file
build:
	./bin/build.sh

# ==========================================================
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

# scan the most recent build and fail if the status fails
rlsecure: build rlsecure-scan rlsecure-list rlsecure-status rlsecure-report rlsecure-version

# ==========================================================
testLocalWhl:
	./bin/testLocalWhl.sh 2>tmp/$@-2 | tee tmp/$@-1


# using the latest py version
# note this uses the test.pypi.org for now
docker:
	export VERSION=$(shell cat work/version) && \
	docker build \
		--build-arg VERSION \
		--tag $(DOCKER_WHO)/$(WHAT) \
		--tag $(DOCKER_WHO)/$(WHAT)-$${VERSION} \
		--tag $(WHAT)-$${VERSION} \
		--tag $(WHAT) \
		-f Dockerfile-test .

dockerRun:
	export VERSION=$(shell cat work/version) && \
	docker run \
		-v ./testdata:/testdata \
		$(WHAT)-$$(VERSION) \
		-d google.com -j | jq -r .

dockerTestdata:
	@export VERSION=$(shell cat work/version) && \
	docker run \
		-v ./testdata:/testdata \
		$(WHAT)-$$(VERSION) \
		-f /testdata/DOMAINS.txt 2>tmp/$@-2 | \
		tee tmp/$@-1

dockerPush:
	export VERSION=$(shell cat work/version) && \
	docker image push \
		--all-tags $(DOCKER_WHO)/$(WHAT)

dockerTests: docker dockerRun dockerTestdata

testTestPypi:
	./bin/testTestPyPiUpload.sh 2>tmp/$@-2 | tee tmp/$@-1

# this is only the upload now for pypi builders
pypi-test:
	./bin/pypi-test.sh

# this is for pypi owners after all tests have finished
pypi: rlsecure
	./bin/pypi.sh

# test2 has the data type in the output
test2: reformat mypy
	./test2.py -f testdata/DOMAINS.txt 2> tmp/$@-2 | tee tmp/$@-1

# test3 simulates the whoisdomain command and has no data type in the output
test3: reformat mypy
	./test3.py -f testdata/DOMAINS.txt 2> tmp/$@-2 | tee tmp/$@-1

release: build rlsecure pypi-test testTestPypi

clean:
	rm -rf dist/*
	rm -f work/version
	rm -rf tmp/*
	rm -f ./rl-secure-list-*.txt
	rm -f ./rl-secure-status-*.txt
	rm -f pyproject.toml
	docker image prune --all --force
