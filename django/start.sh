#!/bin/bash

# Waiting for MySQL database to be ready ...
db_cmd="mysql -h ${DB_HOST} -u ${MYSQL_USER} "-p${MYSQL_PASSWORD}""
counter=1

while ! ${db_cmd} -e "show databases;" > /dev/null 2>&1; do
    sleep 1
    counter=$(expr ${counter} + 1)
done
echo "[Django]" $(date "+%Y/%m/%d-%H:%M:%S") MySQL database ready! "(${counter}sec)"

# check migration
if [ ! -e ${APP_DIRNAME}/migrations/0001_initial.py ]; then
    not_exist_superuser=1
else
    not_exist_superuser=0
fi

# migration
python manage.py makemigrations
python manage.py migrate

# initialize
if [ ${not_exist_superuser} -eq 1 ]; then
    echo "[start]" $(date "+%Y/%m/%d-%H:%M:%S")
    echo create superuser
    python manage.py custom_createsuperuser \
                     --username ${DJANGO_SUPERUSER_NAME} \
                     --email ${DJANGO_SUPERUSER_EMAIL} \
                     --password ${DJANGO_SUPERUSER_PASSWORD}
    echo complete
    echo "[ end ]" $(date "+%Y/%m/%d-%H:%M:%S")
fi

# start django
echo "[start]" $(date "+%Y/%m/%d-%H:%M:%S") Django server
python manage.py runserver 0.0.0.0:${PORT_NUM}
