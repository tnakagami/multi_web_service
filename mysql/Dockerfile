ARG TZ=Asia/Tokyo
FROM alpine:3.12.3

LABEL maintainer="user"
LABEL description="build mariadb"

# Install
RUN    apk --no-cache update \
    && apk --no-cache add bash tzdata \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && apk add --no-cache mariadb mariadb-client mariadb-server-utils pwgen \
    && mkdir /scripts \
    && mkdir /docker-entrypoint-initdb.d \
    && rm -f /var/cache/apk/*

# Add shell script
COPY ./entrypoint.sh /scripts/entrypoint.sh
RUN    mkdir -p /scripts/pre-init.d \
    && mkdir -p /scripts/pre-exec.d \
    && chmod -R 755 /scripts

VOLUME ["/var/lib/mysql"]

EXPOSE 3306

ENTRYPOINT ["/scripts/entrypoint.sh"]

CMD ["--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci"]
