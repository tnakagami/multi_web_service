#!/bin/bash

readonly CURRENT_DIR=$(cd $(dirname $0) && pwd)

# ================
# = main routine =
# ================
while [ -n "$1" ]; do
    case "$1" in
        ps )
            docker ps -a --format 'table {{ .ID }} \t {{ .Names }} \t {{ .Ports }} \t {{ .Status }}'
            shift
            ;;

        logs )
            docker-compose logs -t | sort -t "|" -k 1,+2d
            shift
            ;;

        stop | restart | down )
            exe_opt="$1"
            docker-compose ${exe_opt}
            shift
            ;;

        start )
            docker-compose up -d
            shift
            ;;

        build )
            docker-compose build
            # delete image of none
            docker images | grep '<none>' | awk '{print $3;}' | xargs -I{} docker rmi {}
            shift
            ;;

        -h | --help | --usage )
            echo "Usage: $0 [build|start|stop|restart|down|ps|logs]"
            shift
            ;;

        * )
            shift
            ;;
    esac
done
