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

COUNT_QUERY=""
for file in /data/*.csv; do
table=$(basename "$file" .csv)

if [ -z "$COUNT_QUERY" ]; then
COUNT_QUERY="(SELECT COUNT(*) FROM \"$table\")"
else
COUNT_QUERY="$COUNT_QUERY + (SELECT COUNT(*) FROM \"$table\")"
fi
done

echo ">>> Merge check: sum of source tables VS customers (should be equal):"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT
  $COUNT_QUERY AS source_tables_sum,
  (SELECT COUNT(*) FROM customers) AS customers_total,
  ($COUNT_QUERY) = (SELECT COUNT(*) FROM customers) AS merge_ok;
"

echo ">>> Row count in customers BEFORE deduplication:"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*) FROM customers;"

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOF
CREATE TABLE customers_clean AS
WITH duplicates AS (
    SELECT *,
           LAG(event_time) OVER (
               PARTITION BY event_type,
                            product_id,
                            price,
                            user_id,
                            user_session
               ORDER BY event_time
           ) AS previous_time
    FROM customers
)
SELECT event_time,
       event_type,
       product_id,
       price,
       user_id,
       user_session
FROM duplicates
WHERE previous_time IS NULL
   OR event_time - previous_time > INTERVAL '1 second';

DROP TABLE customers;
ALTER TABLE customers_clean RENAME TO customers;
EOF

echo ">>> Row count in customers AFTER deduplication:"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*) FROM customers;"

echo ">>> Check: remaining duplicates (should be 0):"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT COUNT(*) AS remaining_duplicates FROM (
    SELECT event_time,
           LAG(event_time) OVER (
               PARTITION BY event_type, product_id, price, user_id, user_session
               ORDER BY event_time
           ) AS previous_time
    FROM customers
) sub
WHERE previous_time IS NOT NULL
  AND event_time - previous_time <= INTERVAL '1 second';
"
