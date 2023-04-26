FROM python:alpine

RUN apk update && apk add whois && pip install -i https://test.pypi.org/simple/ whoisdomain==$VERSION

ENTRYPOINT ["whoisdomain"]
CMD ["--help"]
