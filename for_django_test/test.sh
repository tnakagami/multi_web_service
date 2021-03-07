#!/bin/bash

# Waiting for MySQL database to be ready ...
db_cmd="mysql -h ${DB_HOST} -u ${MYSQL_USER} "-p${MYSQL_PASSWORD}""
counter=1

while ! ${db_cmd} -e "show databases;" > /dev/null 2>&1; do
    sleep 1
    counter=$(expr ${counter} + 1)
done
echo "[Django]" $(date "+%Y/%m/%d-%H:%M:%S") MySQL database ready! "(${counter}sec)"

current_time=$(date "+%Y%m%d_%H%M%S")
output_dir=/result_test
rm -f ${output_dir}/*
coverage run --source='.' --omit='manage.py','*/migrations/*','*/tests/*' manage.py test
coverage html -d ${output_dir} --title=result_${current_time} --skip-empty
rm -f .coverage
chmod 777 -R ${output_dir}

trap_TERM() {
    echo "["$(date "+%Y/%m/%d-%H:%M:%S")"]" SIGTERM ACCEPTED
    exit 0
}

trap 'trap_TERM' TERM

while :
do
    sleep 3
done
