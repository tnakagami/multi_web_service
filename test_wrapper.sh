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

        build )
            docker-compose -f test_django-docker-compose.yml build
            docker images | grep '<none>' | awk '{print $3;}' | xargs -I{} docker rmi {}
            shift
            ;;

        start )
            docker-compose -f test_django-docker-compose.yml up -d
            shift
            ;;

        stop | down )
            exe_opt="$1"
            docker-compose -f test_django-docker-compose.yml ${exe_opt}
            shift
            ;;

        logs )
            docker-compose -f test_django-docker-compose.yml logs test_django
            shift
            ;;

        -h | --help | --usage )
            echo "Usage: $0 [build|start|stop|down|ps|logs]"
            shift
            ;;

        * )
            shift
            ;;
    esac
done
