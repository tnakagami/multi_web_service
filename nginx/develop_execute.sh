#!/bin/bash

# ==============
# initialization
# ==============
# setup cron
{
    cat /data/original.root
} > /var/spool/cron/crontabs/root

# start supervisor
/usr/bin/supervisord -c /data/supervisord/supervisord.conf
echo "[supervisord]" $(date "+%Y/%m/%d-%H:%M:%S") start



trap_TERM() {
    echo "["$(date "+%Y/%m/%d-%H:%M:%S")"]" SIGTERM ACCEPTED
    exit 0
}

trap 'trap_TERM' TERM

while :
do
    sleep 3
done
