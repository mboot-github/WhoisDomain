FROM python:alpine

RUN apk update && apk add whois && pip install whoisdomain

ENTRYPOINT ["whoisdomain"]
CMD ["--help"]
