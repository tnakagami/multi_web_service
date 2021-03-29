#!/bin/bash

# ==============
# initialization
# ==============
# setup cron
{
#    cat /data/original.root
    echo ""
} > /var/spool/cron/crontabs/root

# start supervisor
echo "[supervisord]" $(date "+%Y/%m/%d-%H:%M:%S") start
exec /usr/bin/supervisord -c /data/supervisord/supervisord.conf
