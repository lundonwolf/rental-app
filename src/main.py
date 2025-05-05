#!/usr/bin/env python
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.database import db # Import db instance

# Import Blueprints
from src.routes.tenants import tenants_bp
from src.routes.payments import payments_bp
from src.routes.utilities import utilities_bp
from src.routes.settings import settings_bp
from src.routes.ai import ai_bp
from src.routes.reports import reports_bp

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'), # Add template folder
            instance_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance'),
            instance_relative_config=False)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key') # Use environment variable or default

# Configure SQLite database
# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Register Blueprints
app.register_blueprint(tenants_bp, url_prefix='/api/tenants')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(utilities_bp, url_prefix='/api/utilities')
app.register_blueprint(settings_bp, url_prefix='/api/settings')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # If index.html doesn't exist, maybe return a simple message or API status
            return "Welcome to Rent Tracker API. Frontend not found.", 200

# Function to create tables and default settings (used by Docker entrypoint)
def initialize_app():
     with app.app_context():
        print("Initializing database...")
        db.create_all()
        from src.routes.settings import get_all_settings
        get_all_settings() # Ensure default settings exist
        print("Database initialization complete.")

if __name__ == '__main__':
    initialize_app() # Initialize on direct run
    # Use Gunicorn or Waitress in production instead of Flask dev server
    app.run(host='0.0.0.0', port=5000, debug=False) # Set debug=False for production/Docker

