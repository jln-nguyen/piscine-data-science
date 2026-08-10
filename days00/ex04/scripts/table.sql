CREATE TABLE items  (
    product_id      int NOT NULL,
    category_id     bigint,
    category_code   varchar(100),
    brand           varchar(50)
);

\copy items FROM '/data_item/item.csv' DELIMITER ',' CSV HEADER;