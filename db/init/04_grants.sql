-- Grant access to the public schema
GRANT USAGE ON SCHEMA public TO mcp_ro;

-- Allow mcp_ro to read only non-sensitive columns
GRANT SELECT (
    order_id,
    customer_id,
    order_date,
    category,
    amount
)
ON TABLE public.big_orders
TO mcp_ro;