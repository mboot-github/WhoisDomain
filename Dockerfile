FROM python:alpine

ARG VERSION

RUN apk update && apk add whois && pip install -i https://pypi.org/simple/ whoisdomain==$VERSION

ENTRYPOINT ["whoisdomain"]

# in the absense of a command we execute --help
CMD ["--help"]
