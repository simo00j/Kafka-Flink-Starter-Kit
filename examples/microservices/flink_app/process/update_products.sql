INSERT INTO products
SELECT
    u.product_id AS id,
    p.name,
    COALESCE(u.new_description, p.description) AS description,
    COALESCE(u.new_price, p.price) AS price
FROM
    updates AS u
    LEFT JOIN products FOR SYSTEM_TIME AS OF u.proctime AS p
        ON u.product_id = p.id;
