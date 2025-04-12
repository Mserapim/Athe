#!/bin/bash

for rootdir in $(find /app/root/ -iname static -a -type d)
do
    ns=$(echo $rootdir | awk -F '/' '{print $4}')

    if [ $ns == "static" ]; then
        ns=""
    fi

    cp -rv $rootdir/* /app/var/www/static/$ns
done
