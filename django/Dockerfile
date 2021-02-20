ARG TZ=Asia/Tokyo
FROM alpine:3.12.3

LABEL maintainer="user"
LABEL description="build django"

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf-8
ENV SRC_ROOT_PATH /code

# copy python libraries to root directory
COPY ./requirements.txt /

# Install
RUN    apk --no-cache update \
    && apk add --no-cache bash tzdata pcre-dev mysql-client bind-tools \
                          mariadb-dev mariadb-connector-c-dev libsodium libxml2-dev \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    \
    # install temporary libraries
    \
    && apk add --no-cache --virtual .build-deps \
               gcc musl-dev libffi-dev g++ libgcc libstdc++ libxslt-dev \
               python3-dev libc-dev linux-headers openssl-dev curl shadow \
    && apk add --no-cache --virtual --update-cache jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
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
    # delete temporary libraries
    \
    && apk del .build-deps \
    && mkdir -p ${SRC_ROOT_PATH} \
    && mkdir /static \
    && echo -n > /var/log/django.log \
    && echo -n > /var/log/json_django_log.json \
    && rm -rf /root/.cache /var/cache/apk/* /tmp/*

# setup nginx
EXPOSE 8081
# setup start.sh and Pure-FTPD
COPY ./start.sh /start.sh
RUN chmod 755 /start.sh
# change work directory
WORKDIR ${SRC_ROOT_PATH}

CMD ["/start.sh"]
