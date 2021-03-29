FROM alpine:3.12.3
ARG TZ=Asia/Tokyo

LABEL maintainer="user"
LABEL description="build django"

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf-8
ENV SRC_ROOT_PATH /code

# copy python libraries to root directory
COPY ./requirements.txt /

# Install
RUN    apk --no-cache update \
    && apk add --no-cache bash tzdata gettext pcre-dev mysql-client bind-tools libuuid syslog-ng \
                          mariadb-dev mariadb-connector-c-dev libsodium libxml2-dev supervisor \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    \
    # install temporary libraries
    \
    && apk add --no-cache --virtual .build-deps \
               gcc musl-dev libffi-dev g++ libgcc libstdc++ libxslt-dev python3-dev \
               libc-dev linux-headers openssl-dev curl shadow cargo rust \
               jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    \
    # install python3
    \
    && apk add --no-cache python3 \
    \
    # install pip
    \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    \
    # create symbolic link
    \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip \
    \
    # install python libraries
    \
    && pip install -r /requirements.txt \
    \
    # create user
    \
    && useradd -s /sbin/nologin -M -d /dev/null nginx \
    \
    # delete temporary libraries
    \
    && apk --purge del .build-deps \
    && mkdir -p ${SRC_ROOT_PATH} \
    && mkdir -p /data \
    && echo -n > /var/log/uwsgi.log \
    && echo -n > /var/log/daphne.log \
    && rm -rf /root/.cache /var/cache/apk/* /tmp/*

EXPOSE 8081
# change work directory
WORKDIR ${SRC_ROOT_PATH}
# add supervisor configuration
COPY ./supervisord /data/supervisord
# add shell script
COPY ./start.sh /start.sh
RUN chmod 777 /start.sh

CMD ["/start.sh"]
