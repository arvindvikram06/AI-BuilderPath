# Gemini Flash Responses

Here is the complete, self-contained PostgreSQL script that sets up the database schema, seeds the sample data, and runs the requested analytical sales report.

```sql
-- ==========================================
-- 1. TABLE CREATION
-- ==========================================

-- Clean up existing tables if they exist (ordered to respect Foreign Key constraints)
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Customers;

-- Create the Customers table
CREATE TABLE Customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

-- Create the Orders table with a Foreign Key relationship
CREATE TABLE Orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(id) ON DELETE CASCADE,
    order_date DATE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0)
);

-- ==========================================
-- 2. DATA INSERTION
-- ==========================================

-- Insert 5 sample customers
INSERT INTO Customers (id, name, email) VALUES
(1, 'Alice Smith', 'alice@example.com'),
(2, 'Bob Jones', 'bob@example.com'),
(3, 'Charlie Brown', 'charlie@example.com'),
(4, 'Diana Prince', 'diana@example.com'),
(5, 'Evan Wright', 'evan@example.com');

-- Reset the serial sequence for Customers since explicit IDs were passed
ALTER SEQUENCE Customers_id_seq RESTART WITH 6;

-- Insert 15 sample orders spread across customers
-- Note: Alice Smith (ID: 1) has 5 orders (MORE than 3)
-- Note: Charlie Brown (ID: 3) has 4 orders (MORE than 3)
INSERT INTO Orders (customer_id, order_date, total_amount) VALUES
(1, '2026-01-10', 150.00), -- Alice Order 1
(1, '2026-01-15', 45.50),  -- Alice Order 2
(1, '2026-02-01', 200.00), -- Alice Order 3
(1, '2026-02-18', 85.00),  -- Alice Order 4
(1, '2026-03-05', 120.00), -- Alice Order 5 (Total = 5 orders, $600.50)

(2, '2026-01-12', 300.00), -- Bob Order 1
(2, '2026-02-20', 150.00), -- Bob Order 2

(3, '2026-01-05', 50.00),  -- Charlie Order 1
(3, '2026-01-22', 95.00),  -- Charlie Order 2
(3, '2026-02-14', 410.00), -- Charlie Order 3
(3, '2026-03-01', 125.00), -- Charlie Order 4 (Total = 4 orders, $680.00)

(4, '2026-02-28', 75.00),  -- Diana Order 1
(4, '2026-03-10', 115.00), -- Diana Order 2
(4, '2026-03-22', 50.00),  -- Diana Order 3

(5, '2026-03-15', 99.99);  -- Evan Order 1


-- ==========================================
-- 3. SALES REPORTING QUERY
-- ==========================================

SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    c.email AS customer_email,
    COUNT(o.id) AS total_orders,
    SUM(o.total_amount) AS total_sales_amount
FROM Customers c
INNER JOIN Orders o ON c.id = o.customer_id
GROUP BY 
    c.id, 
    c.name, 
    c.email
HAVING COUNT(o.id) > 3
ORDER BY total_sales_amount DESC;

```
