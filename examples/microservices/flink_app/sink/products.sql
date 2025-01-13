CREATE TABLE products (
    id STRING,
    name STRING,
    description STRING,
    price DECIMAL(10, 2),
    PRIMARY KEY (id) NOT ENFORCED
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
