CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL
);

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    order_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    amount NUMERIC(12, 2) NOT NULL
);

INSERT INTO customers (name, email, city)
VALUES
    ('Aarav Sharma', 'aarav@example.com', 'Delhi'),
    ('Priya Mehta', 'priya@example.com', 'Jaipur'),
    ('Rahul Verma', 'rahul@example.com', 'Mumbai'),
    ('Neha Singh', 'neha@example.com', 'Bengaluru'),
    ('Karan Gupta', 'karan@example.com', 'Pune');

INSERT INTO products (name, category, price)
VALUES
    ('Laptop', 'Electronics', 75000.00),
    ('Wireless Mouse', 'Accessories', 1200.00),
    ('Keyboard', 'Accessories', 2500.00),
    ('Monitor', 'Electronics', 18000.00),
    ('Headphones', 'Audio', 5000.00);

INSERT INTO orders (customer_id, product_id, quantity, amount)
VALUES
    (1, 1, 1, 75000.00),
    (1, 2, 2, 2400.00),
    (2, 4, 1, 18000.00),
    (3, 3, 1, 2500.00),
    (4, 5, 2, 10000.00),
    (5, 1, 1, 75000.00);