FROM arm64v8/python:3.6-alpine3.7

WORKDIR /pb
ADD . /build

RUN apk add --no-cache --virtual .build-deps git \
    && pip install /build \
    && apk del .build-deps

CMD ["python", "-m", "pb"]
