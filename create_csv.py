import pandas as pd

# Sample data for the CSV file
data = {
    'product_id': [1, 2, 3, 4, 5],
    'product_name': ['Laptop', 'Smartphone', 'Headphones', 'Monitor', 'Keyboard'],
    'category': ['Electronics', 'Electronics', 'Accessories', 'Electronics', 'Accessories'],
    'price': [1000.00, 500.00, 50.00, 200.00, 30.00],
    'quantity_sold': [10, 20, 30, 15, 25],
    'rating': [4.5, 4.7, 4.2, 4.3, 4.1],
    'review_count': [100, 150, 60, 80, 40]
}

# Create a DataFrame using the sample data
df = pd.DataFrame(data)

# Save DataFrame to a CSV file
df.to_csv('products.csv', index=False)

print("CSV file 'products.csv' created successfully.")
