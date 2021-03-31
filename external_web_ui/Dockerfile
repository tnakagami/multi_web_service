FROM alpine:3.12.3

ENV APP_MODE=production
ENV APP_PORT=9000
ENV GOPATH=/go

RUN    apk --no-cache update \
    && apk add --no-cache ca-certificates go bash \
    && apk add --no-cache --virtual build-dependencies gcc musl-dev openssl git \
    \
    # Compile docker-webui
    \
    && go get -u github.com/pottava/docker-webui \
    && mv /go/bin/docker-webui /usr/bin \
    \
    # Clean up
    \
    && apk del --purge -r build-dependencies \
    && rm -rf /root/.cache /var/cache/apk/* /tmp/* \
    && rm -rf /go/bin \
              /go/src/golang.org \
              /go/src/github.com/[^p]* \
              /go/src/github.com/pottava/docker-webui/.git* \
              /go/src/github.com/pottava/docker-webui/[^a]* \
              /go/src/github.com/pottava/docker-webui/app/[^av]* \
              /go/src/github.com/pottava/docker-webui/app/assets/scss \
              /go/src/github.com/pottava/docker-webui/app/assets/js/clients \
              /go/src/github.com/pottava/docker-webui/app/assets/js/containers \
              /go/src/github.com/pottava/docker-webui/app/assets/js/images

VOLUME ["/var/run/docker.sock"]
EXPOSE 9000

ENTRYPOINT ["docker-webui"]
