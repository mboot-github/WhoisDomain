simple: prepareTest

all: prepareTest dockerTests36 dockerTests

reformat:
	./reformat-code.sh

mypy:
	mypy *.py whoisdomain

# using the lowest py version we support 3.6 currently
docker36:
	export VERSION=$(shell cat work/version) && \
	docker build --build-arg VERSION --tag whoisdomain36-$(shell cat work/version) --tag whoisdomain36 -f Dockerfile-py36 .

dockerRun36:
	docker run whoisdomain36-$(shell cat work/version) -d google.com

dockerTest36:
	docker run whoisdomain36-$(shell cat work/version) -a 2>tmp/$@-2 | tee tmp/$@-1

dockerTests36: docker36 dockerRun36 dockerTest36

# using the latest py version
docker:
	export VERSION=$(shell cat work/version) && \
	docker build --build-arg VERSION --tag whoisdomain-$(shell cat work/version) --tag whoisdomain -f Dockerfile .

dockerRun:
	docker run whoisdomain-$(shell cat work/version) -d google.com

dockerTest:
	docker run whoisdomain-$(shell cat work/version) -a 2>tmp/$@-2 | tee tmp/$@-1

dockerTests: docker dockerRun dockerTest

# this is only for pypi builders
pypi-test:
	./pypi-test.sh

# test the module as downloaded from the test.pypi.org; there is a delay between upload and availability:
# TODO verify that the latest version is the version we need
testTestPypiUpload:
	./testTestPyPiUpload.sh 2>tmp/$@-2 | tee tmp/$@-1

# this is for pypi owners after all tests have finished
pypi:
	./pypi.sh

# this builds a new test pypi and installs ot in a venv for a full test run
prepareTest: reformat mypy pypi-test testTestPypiUpload
