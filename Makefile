WHAT = whoisdomain

simple: prepareTest

all: prepareTest dockerTests36 dockerTests

reformat:
	./bin/reformat-code.sh

mypy:
	mypy bin/*.py $(WHAT)

test2:
	./test2.py -a 2> tmp/$@-2 | tee tmp/$@-1

test3:
	./test3.py -a 2> tmp/$@-2 | tee tmp/$@-1

build:
	./bin/build.sh

# using the lowest py version we support 3.6 currently
docker36:
	export VERSION=$(shell cat work/version) && \
	docker build --build-arg VERSION --tag $(WHAT)36-$(shell cat work/version) --tag $(WHAT)36 -f Dockerfile-py36 .

dockerRun36:
	docker run whoisdomain36-$(shell cat work/version) -d google.com

dockerTest36:
	docker run whoisdomain36-$(shell cat work/version) -a 2>tmp/$@-2 | tee tmp/$@-1

dockerTests36: pypi-test docker36 dockerRun36 dockerTest36

# using the latest py version
docker:
	export VERSION=$(shell cat work/version) && \
	docker build --build-arg VERSION --tag $(WHAT)-$(shell cat work/version) --tag $(WHAT) -f Dockerfile .

dockerRun:
	docker run $(WHAT)-$(shell cat work/version) -d google.com

dockerTest:
	docker run $(WHAT)-$(shell cat work/version) -a 2>tmp/$@-2 | tee tmp/$@-1

dockerTests: pypi-test docker dockerRun dockerTest

# test the module as downloaded from the test.pypi.org; there is a delay between upload and availability:
# TODO verify that the latest version is the version we need
testTestPypiUpload:
	./bin/testTestPyPiUpload.sh 2>tmp/$@-2 | tee tmp/$@-1

testLocalWhl:
	./bin/testLocalWhl.sh 2>tmp/$@-2 | tee tmp/$@-1

# this is only for pypi builders
pypi-test:
	./bin/pypi-test.sh

# this is for pypi owners after all tests have finished
pypi:
	./bin/pypi.sh

# this builds a new test pypi and installs it in a venv for a full test run
prepareTest: reformat mypy build testLocalWhl
