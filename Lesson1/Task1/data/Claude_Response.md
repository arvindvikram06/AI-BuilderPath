# Claude Sonnet Responses

```sql
-- ============================================================
-- 1. TABLE CREATION
-- ============================================================

DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Customers;

CREATE TABLE Customers (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE Orders (
    id           SERIAL PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES Customers(id) ON DELETE CASCADE,
    order_date   DATE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0)
);

-- Helpful for the aggregation query below on larger datasets
CREATE INDEX idx_orders_customer_id ON Orders(customer_id);


-- ============================================================
-- 2. SAMPLE DATA
-- ============================================================

INSERT INTO Customers (name, email) VALUES
    ('Alice Johnson', 'alice.johnson@example.com'),
    ('Bob Smith',      'bob.smith@example.com'),
    ('Carla Diaz',     'carla.diaz@example.com'),
    ('David Lee',      'david.lee@example.com'),
    ('Emma Wilson',    'emma.wilson@example.com');

-- Customer 1 (Alice) has 5 orders -> qualifies for the >3 orders filter
-- Customer 2 (Bob) has 4 orders   -> qualifies
-- Customer 3 (Carla) has 3 orders -> does NOT qualify (exactly 3, not >3)
-- Customer 4 (David) has 2 orders -> does NOT qualify
-- Customer 5 (Emma) has 1 order   -> does NOT qualify
INSERT INTO Orders (customer_id, order_date, total_amount) VALUES
    -- Alice Johnson (5 orders)
    (1, '2025-01-05', 120.50),
    (1, '2025-02-14', 75.00),
    (1, '2025-03-10', 200.25),
    (1, '2025-04-22', 50.00),
    (1, '2025-05-30', 310.75),

    -- Bob Smith (4 orders)
    (2, '2025-01-18', 89.99),
    (2, '2025-02-25', 150.00),
    (2, '2025-03-15', 60.40),
    (2, '2025-06-02', 220.00),

    -- Carla Diaz (3 orders)
    (3, '2025-01-09', 45.00),
    (3, '2025-03-21', 99.99),
    (3, '2025-05-11', 130.00),

    -- David Lee (2 orders)
    (4, '2025-02-02', 75.50),
    (4, '2025-04-17', 210.00),

    -- Emma Wilson (1 order)
    (5, '2025-03-30', 60.00);


-- ============================================================
-- 3. SALES REPORTING QUERY
--    Total orders + total sales per customer,
--    filtered to customers with MORE than 3 orders,
--    sorted by total sales descending.
-- ============================================================

SELECT
    c.id                          AS customer_id,
    c.name                        AS customer_name,
    c.email                       AS customer_email,
    COUNT(o.id)                   AS total_orders,
    SUM(o.total_amount)           AS total_sales_amount
FROM Customers c
JOIN Orders o ON o.customer_id = c.id
GROUP BY c.id, c.name, c.email
HAVING COUNT(o.id) > 3
ORDER BY total_sales_amount DESC;
```

Notes on a couple of choices: `JOIN` (not `LEFT JOIN`) is used since customers with zero orders can never satisfy `COUNT(o.id) > 3` anyway, so there's no need to carry them through the aggregation. The `HAVING` clause filters on the aggregated count rather than `WHERE`, since `WHERE` runs before grouping and can't reference an aggregate like `COUNT()`. The sample data is seeded so Carla sits right at the boundary (exactly 3 orders) to verify the "more than 3," not "3 or more," requirement is actually enforced — running this against the seed data should return only Alice (5 orders) and Bob (4 orders), with Alice's $756.50 total ranked above Bob's $520.39.
