FROM alpine:3.12.3
ARG TZ=Asia/Tokyo

LABEL maintainer="user"
LABEL description="build nginx"

# Install
RUN    apk --no-cache update \
    && apk --no-cache add bash tzdata shadow gettext \
    && useradd -s /sbin/nologin -M -d /dev/null nginx \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && apk add --no-cache php php-mbstring php-openssl certbot supervisor syslog-ng \
    && apk add --no-cache nginx \
    && mkdir -p /static \
    && mkdir -p /etc/letsencrypt \
    && mkdir -p /etc/nginx/template \
    && mkdir -p /data \
    && apk del shadow \
    && rm -rf /var/cache/apk/*

# Set environment
ENV MYDNSJP_MASTER_ID masterid
ENV MYDNSJP_PASSWORD password
ENV MYDNS_EMAIL_ADDR user@example.com
ENV BASE_DOMAIN_NAME example.com
ENV VHOST_NAME www.example.com
ENV SSL_CERT_PATH /etc/nginx/default_certs/default.crt
ENV SSL_CERTKEY_PATH /etc/nginx/default_certs/default.key
ENV SSL_STAPLING_VERIFY off
ENV SSL_TRUSTED_CERTIFICATE_PATH /etc/nginx/default_certs/default.crt

VOLUME ["/etc/letsencrypt"]

# add supervisor
COPY ./supervisord /data/supervisord
# add dns-01 script
COPY ./direct_edit /data/direct_edit
# copy certs to default_certs
COPY ./local_certs /etc/nginx/default_certs

COPY ./execute.sh /execute.sh
RUN    chmod 755 /execute.sh \
    && chmod 600 /data/direct_edit/*.conf \
    && chmod 700 /data/direct_edit/*.php \
    && cp -f /var/spool/cron/crontabs/root /data/original.root

EXPOSE 443

CMD ["/execute.sh"]
