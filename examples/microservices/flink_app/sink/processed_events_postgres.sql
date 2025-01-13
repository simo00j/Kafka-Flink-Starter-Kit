CREATE TABLE processed_events_postgres (
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
    'url' = '{{ url }}',
    'table-name' = '{{ table_name }}',
    'username' = '{{ username }}',
    'password' = '{{ password }}',
    'driver' = '{{ driver }}',
    'sink.buffer-flush.max-rows' = '1',
    'sink.buffer-flush.interval' = '1s'
);
