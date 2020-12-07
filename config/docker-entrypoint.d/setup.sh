#!/bin/bash

# Grant the db user access to create databases (so that tests can be run, etc.)
db_user=$POSTGRES_USER
# echo "Granting $db_user permission to create databases..."
# psql postgres -c "ALTER USER $db_user CREATEDB" &>/dev/null

# Check if default db exists
db_name=$POSTGRES_DB

# echo "Importing $sql_file..."
# psql "$db_name" <"$sql_file" &>/dev/null || error "Failed to import $sql_file."

# Set db permissions correctly
psql "$db_name" -c "alter database $db_name owner to $db_user" &>/dev/null
psql "$db_name" -c "alter schema public owner to $db_user" &>/dev/null
# Set permissions for db tables
tables=$(psql "$db_name" -qAt -c "select tablename from pg_tables where schemaname = 'public';")
for table in $tables; do
  psql "$db_name" -c "alter table \"$table\" owner to $db_user" &>/dev/null
done
# Set permissions for db sequences
seqs=$(psql "$db_name" -qAt -c "select sequence_name from information_schema.sequences where sequence_schema = 'public';")
for seq in $seqs; do
  psql "$db_name" -c "alter table \"$seq\" owner to $db_user" &>/dev/null
done
# Set permissions for db views
views=$(psql "$db_name" -qAt -c "select table_name from information_schema.views where table_schema = 'public';")
for view in $views; do
  psql "$db_name" -c "alter table \"$view\" owner to $db_user" &>/dev/null
done
