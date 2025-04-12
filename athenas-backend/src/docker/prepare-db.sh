#!/bin/sh

psql -U $DB_USER -h $DB_HOST template1 <<EOF
CREATE DATABASE ${1}_swap WITH TEMPLATE $2;
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname='$1';
DROP DATABASE IF EXISTS $1;
ALTER DATABASE ${1}_swap RENAME TO ${1};
EOF
