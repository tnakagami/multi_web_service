#!/bin/bash

readonly CURRENT_DIR=$(cd $(dirname $0) && pwd)
service_name=test_django
yaml_file=test_django-docker-compose.yml

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
            docker-compose -f ${yaml_file} build
            docker images | grep '<none>' | awk '{print $3;}' | xargs -I{} docker rmi {}
            shift
            ;;

        start )
            docker-compose -f ${yaml_file} up -d
            shift
            ;;

        restart )
            docker-compose -f ${yaml_file} restart ${service_name}
            shift
            ;;

        stop )
            docker-compose -f ${yaml_file} stop
            shift
            ;;

        down )
            docker-compose -f ${yaml_file} down -v
            shift
            ;;

        logs )
            docker-compose -f ${yaml_file} logs ${service_name}
            shift
            ;;

        zip )
            zip result_test.zip -j for_django_test/result_test/*
            shift
            ;;

        -h | --help | --usage )
            echo "Usage: $0 [build|start|stop|restart|down|ps|logs|zip]"
            shift
            ;;

        * )
            shift
            ;;
    esac
done
