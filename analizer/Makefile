
all: format
	./analizeIanaTld.py
	./investigateTld.py 2>2 | tee 1

format:
	black --line-length 160 *.py
	-pylama -m 160 *.py

clean:
	rm IanaDb.sqlite
	rm -rf .iana_cache/ .psl_cache/
