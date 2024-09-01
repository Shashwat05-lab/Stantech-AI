WITH TotalSpending AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.email,
        SUM(oi.quantity * oi.price_per_unit) AS total_spent
    FROM Customers c
    JOIN Orders o ON c.customer_id = o.customer_id
    JOIN Order_Items oi ON o.order_id = oi.order_id
    WHERE o.order_date >= DATE('now', '-1 year')
    GROUP BY c.customer_id, c.customer_name, c.email
),
CustomerCategorySpending AS (
    SELECT 
        c.customer_id,
        p.category,
        SUM(oi.quantity * oi.price_per_unit) AS category_spent
    FROM Customers c
    JOIN Orders o ON c.customer_id = o.customer_id
    JOIN Order_Items oi ON o.order_id = oi.order_id
    JOIN Products p ON oi.product_id = p.product_id
    WHERE o.order_date >= DATE('now', '-1 year')
    GROUP BY c.customer_id, p.category
),
MostPurchasedCategory AS (
    SELECT 
        ccs.customer_id,
        ccs.category,
        ccs.category_spent,
        ROW_NUMBER() OVER (PARTITION BY ccs.customer_id ORDER BY ccs.category_spent DESC) AS rn
    FROM CustomerCategorySpending ccs
)
SELECT 
    ts.customer_id,
    ts.customer_name,
    ts.email,
    ts.total_spent,
    mpc.category AS most_purchased_category
FROM TotalSpending ts
JOIN MostPurchasedCategory mpc ON ts.customer_id = mpc.customer_id
WHERE mpc.rn = 1
ORDER BY ts.total_spent DESC
LIMIT 5;
