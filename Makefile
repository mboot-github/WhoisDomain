# ==========================================================
# ==========================================================
# https://docs.secure.software/cli

SHELL 		:= /bin/bash -l

RLSECURE 	:= ~/tmp/rl-secure/rl-secure
RLSTORE 	:= ~/

WHAT 		:= whoisdomain
DOCKER_WHO	:= mbootgithub

SIMPLEDOMAINS = $(shell ls testdata)

# PHONY targets: make will run its recipe regardless of whether a file with that name exists or what its last modification time is.
.PHONY: TestSimple TestSimple2 TestAll clean

# ==========================================================
# run a test sequence local only, no docker ,no upload to pypi
LocalTestSimple: reformat mypy test2

# ==========================================================
LocalTestWhl: build
	./bin/testLocalWhl.sh 2>tmp/$@-2 | tee tmp/$@-1

# this step creates or updates the toml file
build:
	./bin/build.sh

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
		-f /testdata/DOMAINS.txt 2>tmp/$@-2 | \
		tee tmp/$@-1

dockerPush:
	export VERSION=$(shell cat work/version) && \
	docker image push \
		--all-tags $(DOCKER_WHO)/$(WHAT)

# ====================================================
# uploading to pypi an pypi-test
# build a test-mypi and download the image in a venv ane run a test
pypiTest: pypi-test testTestPypi

# this is only the upload now for pypi builders
pypi-test:
	./bin/upload_to_pypiTest.sh

testTestPypi:
	./bin/testTestPyPiUpload.sh 2>tmp/$@-2 | tee tmp/$@-1

releaseTest: build rlsecure pypi-test testTestPypi

# this is for pypi owners after all tests have finished
pypi: rlsecure
	./bin/upload_to_pypi.sh

release: build rlsecure pypi

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
	( cd analizer; ./analizeIanaTld.py )
	( cd analizer; ./investigateTld.py ) | tee out

# black pylama and mypy on the source directory
reformat:
	./bin/reformat-code.sh

# only verify --strict all python code
mypy:
	mypy --strict *.py bin/*.py $(WHAT)

clean:
	rm -rf tmp/*
	rm -f ./rl-secure-list-*.txt
	rm -f ./rl-secure-status-*.txt
	rm -f pyproject.toml
	docker image prune --all --force

cleanDist:
	rm -rf dist/*
	# rm -f work/version
