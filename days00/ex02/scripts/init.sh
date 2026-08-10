#!/bin/bash
set -e

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOF
CREATE TABLE IF NOT EXISTS data_2022_oct (
    event_time timestamp,
    event_type varchar(20),
    product_id integer,
    price double precision,
    user_id bigint,
    user_session uuid
);

\copy data_2022_oct FROM '/data/data_2022_oct.csv' DELIMITER ',' CSV HEADER;
EOF
done