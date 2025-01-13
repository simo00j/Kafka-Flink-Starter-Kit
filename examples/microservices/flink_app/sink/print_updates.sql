CREATE TABLE print_updates (
    event_id STRING,
    product_id STRING,
    new_price DECIMAL(10, 2),
    new_description STRING,
    event_time TIMESTAMP(3)  -- Keep as STRING to avoid parsing issues
) WITH (
    'connector' = 'print'
);
