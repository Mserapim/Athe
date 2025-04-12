#!/bin/sh

echo "Dropando o banco $1"
psql -U $DB_USER -h $DB_HOST -p $DB_PORT template1 <<EOF
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname='$1';
DROP DATABASE IF EXISTS $1;
EOF
