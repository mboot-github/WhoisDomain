
reformat:
	./reformat-code.sh

mypy:
	mypy *.py whoisdomain

docker:
	docker build --tag whoisdomain .

dockerRun:
	docker run whoisdomain -d google.com

dockerTest:
	docker run whoisdomain -a 2>2 | tee 1

pypi-test:
	./pypi-test.sh

testTestPypiUpload:
	./testTestPyPiUpload.sh

pypi:
	./pypi.sh

prepare: reformat mypy pypi-test testTestPypiUpload
