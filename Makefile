# ==========================================================
# ==========================================================

WHAT = whoisdomain
SIMPLEDOMAINS = $(shell  ls testdata)

# ==========================================================
# ==========================================================

# build a new whl file are run a test local only, no docker no upload
TestSimple: prepareTest

TestSimple2: TestSimple mypyTest

TestAll: TestSimple mypyTest dockerTests36 dockerTests

# build a test-mypi and download the image in a venv ane run a test
mypyTest: pypi-test testTestPypiUpload

# build a docker images with python 3.6.x and run a test -a
dockerTests36: docker36 dockerRun36 dockerTest36

# build a docker images with the latest python and run a test -a
dockerTests: docker dockerRun dockerTest

# ==========================================================
# ==========================================================

reformat:
	./bin/reformat-code.sh

mypy:
	mypy bin/*.py $(WHAT)

build:
	./bin/build.sh

testLocalWhl:
	./bin/testLocalWhl.sh 2>tmp/$@-2 | tee tmp/$@-1

prepareTest: reformat mypy build testLocalWhl

# using the lowest py version we support 3.6 currently
docker36:
	export VERSION=$(shell cat work/version) && \
	docker build --build-arg VERSION --tag $(WHAT)36-$(shell cat work/version) --tag $(WHAT)36 -f Dockerfile-py36 .

dockerRun36:
	docker run -v ./testdata:/testdata whoisdomain36-$(shell cat work/version) -d google.com

dockerTest36:
	docker run -v ./testdata:/testdata whoisdomain36-$(shell cat work/version) -f /testdata/DOMAINS.txt  2>tmp/$@-2 | tee tmp/$@-1

# using the latest py version
docker:
	export VERSION=$(shell cat work/version) && \
	docker build --build-arg VERSION --tag $(WHAT)-$(shell cat work/version) --tag $(WHAT) -f Dockerfile .

dockerRun:
	docker run -v ./testdata:/testdata $(WHAT)-$(shell cat work/version) -d google.com

dockerTest:
	docker run -v ./testdata:/testdata $(WHAT)-$(shell cat work/version) -f /testdata/DOMAINS.txt 2>tmp/$@-2 | tee tmp/$@-1

# this builds a new test pypi and installs it in a venv for a full test run
dockerTests: pypi-test testTestPypiUpload docker dockerRun dockerTest

# test the module as downloaded from the test.pypi.org; there is a delay between upload and availability:
# TODO verify that the latest version is the version we need
testTestPypiUpload:
	./bin/testTestPyPiUpload.sh 2>tmp/$@-2 | tee tmp/$@-1

# this is only the upload now for pypi builders
pypi-test:
	./bin/pypi-test.sh

# this is for pypi owners after all tests have finished
pypi:
	./bin/pypi.sh

# test2 has the data type in the output
test2:
	./test2.py -f testdata/DOMAINS.txt 2> tmp/$@-2 | tee tmp/$@-1

# test3 simulates the whoisdomain command and has no data type in the output
test3:
	./test3.py -f testdata/DOMAINS.txt 2> tmp/$@-2 | tee tmp/$@-1

