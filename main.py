from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pandas as pd
import numpy as np
import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'my-32-character-ultra-secure-and-ultra-long-secret'  # Secure key

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define database models
class Product(db.Model):
    """Model for storing product data."""
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)

class User(db.Model):
    """Model for storing user data."""
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String, nullable=False)

# Database initialization
def create_tables():
    """Creates the database tables if they do not already exist."""
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except SQLAlchemyError as e:
            print(f"Error creating tables: {e}")

# Data upload and cleaning
def upload_data(csv_file):
    """Loads data from CSV and uploads it to the database."""
    with app.app_context():
        try:
            if not os.path.exists(csv_file):
                print(f"File {csv_file} does not exist.")
                return

            # Load data into DataFrame
            df = pd.read_csv(csv_file)

            # Data Cleaning
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

            # Handle missing values
            df['price'] = df['price'].fillna(df['price'].median())
            df['quantity_sold'] = df['quantity_sold'].fillna(df['quantity_sold'].median())
            df['rating'] = df.groupby('category')['rating'].transform(lambda x: x.fillna(x.mean()))

            # Upload data to the database
            for _, row in df.iterrows():
                existing_product = db.session.get(Product, row['product_id'])
                if existing_product:
                    # Update existing record
                    existing_product.product_name = row['product_name']
                    existing_product.category = row['category']
                    existing_product.price = row['price']
                    existing_product.quantity_sold = row['quantity_sold']
                    existing_product.rating = row['rating']
                    existing_product.review_count = row['review_count']
                else:
                    # Add new record
                    product = Product(
                        product_id=row['product_id'],
                        product_name=row['product_name'],
                        category=row['category'],
                        price=row['price'],
                        quantity_sold=row['quantity_sold'],
                        rating=row['rating'],
                        review_count=row['review_count']
                    )
                    db.session.add(product)
            db.session.commit()
            print("Data uploaded successfully.")

        except pd.errors.EmptyDataError:
            print("CSV file is empty.")
        except pd.errors.ParserError:
            print("Error parsing CSV file.")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Authentication
@app.route('/signup', methods=['POST'])
def signup():
    """Endpoint for user sign-up."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        user = User(username=username, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User registered successfully"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": f"Database error: {e}"}), 500

@app.route('/login', methods=['POST'])
def login():
    """Endpoint for user login."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# Generate summary report
@app.route('/generate_report', methods=['GET'])
@jwt_required()
def generate_report():
    """Endpoint to generate a summary report."""
    current_user = get_jwt_identity()

    try:
        df = pd.read_sql_table('products', db.engine)

        # Calculate total revenue and top product per category
        summary = df.groupby('category').agg(
            total_revenue=pd.NamedAgg(column='price', aggfunc=lambda x: (x * df.loc[x.index, 'quantity_sold']).sum()),
            top_product=pd.NamedAgg(column='product_name', aggfunc=lambda x: df.loc[x.index, 'quantity_sold'].idxmax()),
            top_product_quantity_sold=pd.NamedAgg(column='quantity_sold', aggfunc='max')
        ).reset_index()

        report_file = 'summary_report.csv'
        summary.to_csv(report_file, index=False)

        return send_file(report_file, as_attachment=True)
    except SQLAlchemyError as e:
        return jsonify({"msg": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"msg": f"An unexpected error occurred: {e}"}), 500

if __name__ == "__main__":
    create_tables()  # Create tables if they do not exist
    upload_data('products.csv')  
    app.run(debug=True)
