#!/bin/bash

# Setup limiting log size
readonly LIMIT_SIZE=$(perl -le 'print (1024 * 1024)')
execute_type="--run"

while [ -n "$1" ]; do
    case "$1" in
        -f | --force )
            execute_type="--force"
            shift
            ;;

        -d | --dry-run )
            execute_type="--dry-run"
            shift
            ;;

        -r | --run )
            execute_type="--run"
            shift
            ;;

        * )
            shift
            ;;
    esac
done

{
    echo logfiles link access.log error.log django.log json_django.log
} | while read target_path data_type log_files; do
    # Create log directory if not exist
    [ ! -e ${target_path} ] && mkdir -p ${target_path}

    # Change command for data type
    if [ "${data_type}" = "link" ]; then
        use_command="readlink -f"
    else
        use_command="echo"
    fi

    # Sequencial process of log files
    echo ${log_files} | tr ' ' '\n' | xargs -I{} ${use_command} ${target_path}/{} | while read file_path; do
        touch ${file_path}
        file_size=$(wc -c < ${file_path})

        # Compare log file size to limit size
        case "${execute_type}" in
            --run )
                if [ ${file_size} -gt ${LIMIT_SIZE} ]; then
                    # clean log file
                    echo erase log file "(${file_path##*/})"
                    echo -n > ${file_path}
                fi
                ;;

            --force )
                echo "[force option] ${file_path##*/}, size: ${file_size}[byte] (limit: ${LIMIT_SIZE}[byte])"
                # clean log file
                echo -n > ${file_path}
                ;;

            --dry-run )
                echo '[dry-run] echo -n >' ${file_path}
                ;;

            * )
                ;;
        esac
    done
done
