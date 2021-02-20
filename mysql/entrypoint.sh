#!/bin/bash

if [ -d "/run/mysqld" ]; then
    echo "[info] mysqld already present, skipping creation"
    chown -R mysql:mysql /run/mysqld
else
    echo "[info] mysqld not found, creating...."
    mkdir -p /run/mysqld
    chown -R mysql:mysql /run/mysqld
fi

if [ -d /var/lib/mysql/mysql ]; then
    echo "[info] MySQL directory already present, skipping creation"
    chown -R mysql:mysql /var/lib/mysql
else
    # execute pre-init scripts in initialization
    for file in /scripts/pre-init.d/*.sh; do
        if [ -e "${file}" ]; then
            echo "[info] pre-init.d - processing ${file}"
            . "${file}"
        fi
    done
    echo "[info] MySQL data directory not found, creating initial DBs"

    chown -R mysql:mysql /var/lib/mysql

    mysql_install_db --user=mysql --ldata=/var/lib/mysql > /dev/null

    if [ "${MYSQL_ROOT_PASSWORD}" = "" ]; then
        MYSQL_ROOT_PASSWORD=`pwgen 16 1`
        echo "[info] MySQL root Password: ${MYSQL_ROOT_PASSWORD}"
    fi

    MYSQL_DATABASE=${MYSQL_DATABASE:-""}
    MYSQL_USER=${MYSQL_USER:-""}
    MYSQL_PASSWORD=${MYSQL_PASSWORD:-""}

    tfile=`mktemp`
    if [ ! -f "${tfile}" ]; then
        return 1
    fi

    cat << _EOF_ > ${tfile}
USE mysql ;
FLUSH PRIVILEGES ;
GRANT ALL ON *.* TO 'root'@'%' identified by '${MYSQL_ROOT_PASSWORD}' WITH GRANT OPTION ;
GRANT ALL ON *.* TO 'root'@'localhost' identified by '${MYSQL_ROOT_PASSWORD}' WITH GRANT OPTION ;
SET PASSWORD FOR 'root'@'localhost'=PASSWORD('${MYSQL_ROOT_PASSWORD}') ;
DROP USER IF EXISTS ''@'localhost' ;
DROP DATABASE IF EXISTS test ;
FLUSH PRIVILEGES ;
_EOF_

    if [ "${MYSQL_DATABASE}" != "" ]; then
        echo "[info] Creating database: ${MYSQL_DATABASE}"
            if [ "${MYSQL_CHARSET}" != "" ] && [ "${MYSQL_COLLATION}" != "" ]; then
                    echo "[info] with character set [${MYSQL_CHARSET}] and collation [${MYSQL_COLLATION}]"
                    echo "CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET ${MYSQL_CHARSET} COLLATE ${MYSQL_COLLATION};" >> ${tfile}
            else
                    echo "[info] with character set: 'utf8' and collation: 'utf8_general_ci'"
                    echo "CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8 COLLATE utf8_general_ci;" >> ${tfile}
            fi

     if [ "${MYSQL_USER}" != "" ]; then
            echo "[info] Creating user: ${MYSQL_USER} with password ${MYSQL_PASSWORD}"
            echo "GRANT ALL ON \`${MYSQL_DATABASE}\`.* to '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';" >> ${tfile}
        fi
    fi

    mysqld_cmd="/usr/bin/mysqld --user=mysql --bootstrap --verbose=0 --skip-name-resolve --skip-networking=0"
    cat ${tfile} | ${mysqld_cmd}
    rm -f ${tfile}

    echo "$0: running sql in /docker-entrypoint-initdb.d"
    target_dir=/docker-entrypoint-initdb.d
    ls -v ${target_dir} | while read file; do
        file_path=${target_dir}/${file}

        case "${file}" in
            *.sql)
                echo "=== ${file_path} ==="
                cat "${file_path}" | ${mysqld_cmd}
                echo "===================="
                ;;

            *.sql.gz)
                echo "=== ${file_path} ==="
                gunzip -c "${file_path}" | ${mysqld_cmd}
                echo "===================="
                ;;
            *)
                echo "$0: ignoring or entrypoint initdb empty ${file_path}"
                ;;
        esac
    done

    echo
    echo 'MySQL init process done. Ready for start up.'
    echo

    echo "exec /usr/bin/mysqld --user=mysql --console --skip-name-resolve --skip-networking=0" "$@"
fi

# execute any pre-exec scripts
for file in /scripts/pre-exec.d/*sh; do
    if [ -e "${file}" ]; then
        echo "[info] pre-exec.d - processing ${file}"
        . ${file}
    fi
done

exec /usr/bin/mysqld --user=mysql --console --skip-name-resolve --skip-networking=0 $@
