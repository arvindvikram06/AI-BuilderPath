# ChatGPT Responses

```sql
-- ==========================================================
-- PostgreSQL SQL Script
-- Database Setup and Sales Reporting
-- ==========================================================

-- Drop tables if they already exist
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Customers;

-- ==========================================================
-- Create Customers Table
-- ==========================================================

CREATE TABLE Customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

-- ==========================================================
-- Create Orders Table
-- ==========================================================

CREATE TABLE Orders (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES Customers(id)
        ON DELETE CASCADE
);

-- ==========================================================
-- Insert Sample Customers
-- ==========================================================

INSERT INTO Customers (name, email) VALUES
('Alice Johnson', 'alice@example.com'),
('Bob Smith', 'bob@example.com'),
('Charlie Brown', 'charlie@example.com'),
('David Wilson', 'david@example.com'),
('Eva Green', 'eva@example.com');

-- ==========================================================
-- Insert Sample Orders (15 Orders)
-- Alice has 5 orders (>3 orders)
-- ==========================================================

INSERT INTO Orders (customer_id, order_date, total_amount) VALUES
-- Alice (5 Orders)
(1, '2026-01-05', 120.50),
(1, '2026-01-10', 250.00),
(1, '2026-02-01', 175.25),
(1, '2026-02-15', 320.75),
(1, '2026-03-01', 90.00),

-- Bob (3 Orders)
(2, '2026-01-08', 450.00),
(2, '2026-01-20', 180.00),
(2, '2026-02-18', 220.00),

-- Charlie (2 Orders)
(3, '2026-01-12', 75.50),
(3, '2026-02-20', 140.00),

-- David (4 Orders)
(4, '2026-01-07', 310.00),
(4, '2026-01-25', 280.00),
(4, '2026-02-10', 150.00),
(4, '2026-03-05', 410.00),

-- Eva (1 Order)
(5, '2026-03-15', 500.00);

-- ==========================================================
-- Sales Reporting Query
-- Total Orders and Total Sales Per Customer
-- Only Customers with More Than 3 Orders
-- ==========================================================

SELECT
    c.id AS customer_id,
    c.name,
    c.email,
    COUNT(o.id) AS total_orders,
    SUM(o.total_amount) AS total_sales
FROM Customers c
JOIN Orders o
    ON c.id = o.customer_id
GROUP BY
    c.id,
    c.name,
    c.email
HAVING COUNT(o.id) > 3
ORDER BY
    total_sales DESC;
```
