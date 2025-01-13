INSERT INTO processed_events_kafka
SELECT
    ue.event_id,
    ue.user_id,
    up.username,
    up.email,
    ue.event_type,
    ue.action_type,
    ue.product_id,
    ce.total_amount,
    ue.event_time
FROM
    user_events AS ue
    LEFT JOIN user_profiles FOR SYSTEM_TIME AS OF ue.proctime AS up
        ON ue.user_id = up.id
    LEFT JOIN checkout_events AS ce
        ON ue.user_id = ce.user_id
        AND ue.product_id = ce.product_id
        AND ce.event_time BETWEEN ue.event_time AND ue.event_time + INTERVAL '1' HOUR
WHERE
    ue.event_type = 'action';
