CREATE TABLE big_orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    category TEXT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    customer_email TEXT
);

INSERT INTO big_orders (
    customer_id,
    order_date,
    category,
    amount,
    customer_email
)
SELECT
    (random() * 99999 + 1)::BIGINT,
    CURRENT_DATE - (random() * 730)::INTEGER,
    CASE
        WHEN random() < 0.25 THEN 'Electronics'
        WHEN random() < 0.50 THEN 'Accessories'
        WHEN random() < 0.75 THEN 'Home'
        ELSE 'Other'
    END,
    round((random() * 100000)::numeric, 2),
    'customer' || (random() * 99999 + 1)::INTEGER || '@example.com'
FROM generate_series(1, 5000000);

ANALYZE big_orders;