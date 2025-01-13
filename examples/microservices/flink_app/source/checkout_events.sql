CREATE TABLE checkout_events (
    checkout_id STRING,
    user_id STRING,
    product_id STRING,
    payment_method STRING,
    total_amount DECIMAL(10, 2),
    shipping_address STRING,
    billing_address STRING,
    event_time TIMESTAMP(3),
    proctime AS PROCTIME(),
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = '{{ connector }}',
    'topic' = '{{ topic }}',
    'properties.bootstrap.servers' = '{{ bootstrap_servers }}',
    'properties.group.id' = '{{ consumer_group_id }}',
    'scan.startup.mode' = '{{ scan_startup_mode }}',
    'format' = '{{ format }}'
);
