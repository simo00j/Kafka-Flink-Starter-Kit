CREATE TABLE processed_events_kafka (
    event_id STRING,
    user_id STRING,
    username STRING,
    email STRING,
    event_type STRING,
    action_type STRING,
    product_id STRING,
    total_amount DECIMAL(10, 2),
    event_time TIMESTAMP(3)
) WITH (
    'connector' = '{{ connector }}',
    'topic' = '{{ topic }}',
    'properties.bootstrap.servers' = '{{ bootstrap_servers }}',
    'format' = '{{ format }}'
);
