# Stantech-AI
 Assignment

To run the python code follow below steps.

1. Start the Flask Application
Run the Flask App: python main.py
This should start your Flask development server. You should see output indicating that the server is running, such as: Running on http://127.0.0.1:5000.

2. Verify Table Creation
Check if Tables are Created: You can use a database browser tool (like DB Browser for SQLite) to open ecommerce.db and verify that the products and users tables have been created.

3. Test API Endpoints
You can use tools like Postman to test the API endpoints. Here’s how to test each endpoint:

a. /signup Endpoint
Send a POST Request to /signup:
URL: http://127.0.0.1:5000/signup
Method: POST
Headers - Content-Type:application/json 
Body (JSON): {
                "username": "testuser",
                "password": "testpassword"
             }

Expected Response: {
                        "msg": "User registered successfully"
                   }

b. /login Endpoint
Send a POST Request to /login:

URL: http://127.0.0.1:5000/login
Method: POST
Headers - Content-Type:application/json 
Body (JSON):{
                "username": "testuser",
                "password": "testpassword"
            }

Expected Response:  {
                        "access_token": "<your_access_token>"
                    }

Verify the Access Token:
Save the access token returned from the /login endpoint for use in authenticated requests.

c. /generate_report Endpoint
Send a GET Request to /generate_report:
URL: http://127.0.0.1:5000/generate_report
Method: GET
Headers:
Authorization: Bearer <your_access_token>
Expected Response: A CSV file download containing the summary report.