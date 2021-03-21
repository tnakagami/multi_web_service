#!/bin/bash

pushd ${SRC_ROOT_PATH}

current_time=$(date "+%Y%m%d_%H%M%S")
output_dir=/result_test
rm -f ${output_dir}/*
coverage run --source='.' --omit='manage.py','*/migrations/*','*/tests/*' manage.py test -v 3
coverage html -d ${output_dir} --title=result_${current_time} --skip-empty
rm -f .coverage
chmod 777 -R ${output_dir}

popd
