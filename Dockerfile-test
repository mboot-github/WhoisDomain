FROM python:alpine
ARG VERSION
RUN apk update && apk add whois && pip install -i https://test.pypi.org/simple/ whoisdomain==$VERSION

ENTRYPOINT ["whoisdomain"]
CMD ["--help"]
