#!/bin/bash
set -e

for file in /data/*.csv; do
    table=$(basename "$file" .csv)

    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOF
CREATE TABLE IF NOT EXISTS "$table" (
    event_time timestamp,
    event_type varchar(20),
    product_id integer,
    price double precision,
    user_id bigint,
    user_session uuid
);

TRUNCATE "$table";

\copy "$table" FROM '$file' CSV HEADER;
EOF
done

QUERY=""

for file in /data/*.csv; do
    table=$(basename "$file" .csv)

    if [ -z "$QUERY" ]; then
        QUERY="SELECT * FROM \"$table\""
    else
        QUERY="$QUERY UNION ALL SELECT * FROM \"$table\""
    fi
done

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOF
CREATE TABLE customers AS
$QUERY;
EOF