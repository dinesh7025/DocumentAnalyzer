import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS

from endpoints.auth_endpoint import auth_bp
from endpoints.upload_endpoint import upload_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)

if __name__ == "__main__":
    app.run(debug=True)
