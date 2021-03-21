#!/bin/bash

# Waiting for MySQL database to be ready ...
db_cmd="mysql -h ${DB_HOST} -u ${MYSQL_USER} "-p${MYSQL_PASSWORD}""
counter=1

while ! ${db_cmd} -e "show databases;" > /dev/null 2>&1; do
    sleep 1
    counter=$(expr ${counter} + 1)
done
echo "[Django]" $(date "+%Y/%m/%d-%H:%M:%S") MySQL database ready! "(${counter}sec)"

# execute test
echo "[Django] execute tests"
/execute_tests.sh
echo "[Django] finished"

trap_TERM() {
    echo "["$(date "+%Y/%m/%d-%H:%M:%S")"]" SIGTERM ACCEPTED
    exit 0
}

trap 'trap_TERM' TERM

while :
do
    sleep 3
done
