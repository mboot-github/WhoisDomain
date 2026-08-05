FROM ghcr.io/home-assistant/base-python:3.14-alpine3.24

RUN apk add --no-cache whois procps

RUN python3 -m pip install --no-cache-dir \
    "whoisdomain==2.20260709.1" \
    "whodap>=0.1.16" \
    "tld>=0.13.2" \
    "psutil-home-assistant==0.0.1"

WORKDIR /app
COPY soak_test.py /app/soak_test.py

ENV PYTHONUNBUFFERED=1 \
    OUTPUT_DIR=/results \
    QUERY_INTERVAL_SECONDS=60 \
    MAX_DOMAINS=100 \
    MODE=default \
    FORCE_GC_EVERY=0

ENTRYPOINT ["python3", "/app/soak_test.py"]
