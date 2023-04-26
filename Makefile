
simple: prepareTest

all: prepareTest dockerTests36 dockerTests

reformat:
	./reformat-code.sh

mypy:
	mypy *.py whoisdomain

# using the lowest py version we support 3.6 currently
docker36:
	docker build --tag whoisdomain36 Dockerfile-py36

dockerRun36:
	docker run whoisdomain36 -d google.com

dockerTest36:
	docker run whoisdomain36 -a 2>tmp/dockerTest36-2 | tee tmp/dockerTest36-1

dockerTests36: docker36 dockerRun36 dockerTest36

# using the latest py version
docker:
	docker build --tag whoisdomain .

dockerRun:
	docker run whoisdomain -d google.com

dockerTest:
	docker run whoisdomain -a 2>tmp/dockerTest-2 | tee tmp/dockerTest-1

dockerTests: docker dockerRun dockerTest

# this is only for pypi builders
pypi-test:
	./pypi-test.sh

# test the module as downloaded from the test.pypi.org; there is a delay between upload and availability:
# TODO verify that the latest version is the version we need
testTestPypiUpload:
	./testTestPyPiUpload.sh 2>tmp/testTestPypiUpload-2 | tee tmp/testTestPypiUpload-1

# this is for pypi owners after all tests have finished
pypi:
	./pypi.sh

prepareTest: reformat mypy pypi-test testTestPypiUpload
