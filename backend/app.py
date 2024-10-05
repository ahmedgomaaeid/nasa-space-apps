from flask import Flask
from routes import init_routes
from flask_cors import CORS

# Create the Flask app instance
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["https://map.amartil.com", "http://127.0.0.1:5500"]}})

# Initialize Routes
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
