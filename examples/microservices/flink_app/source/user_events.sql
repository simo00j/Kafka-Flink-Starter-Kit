CREATE TABLE user_events (
    event_id STRING,
    user_id STRING,
    event_type STRING,
    action_type STRING,
    product_id STRING,
    user_agent STRING,
    ip_address STRING,
    url STRING,
    new_email STRING,
    new_username STRING,
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
