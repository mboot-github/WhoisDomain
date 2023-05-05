FROM python:alpine

ARG VERSION

LABEL version="$VERSION"

RUN apk update --no-cache
RUN apk add --no-cache whois
RUN pip install --no-cache-dir -i https://pypi.org/simple/ whoisdomain==$VERSION

ENTRYPOINT ["whoisdomain"]

# in the absense of a command we execute --help
CMD ["--help"]
