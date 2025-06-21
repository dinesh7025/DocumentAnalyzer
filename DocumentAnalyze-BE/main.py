import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, g
from flask_cors import CORS
import jwt
from dotenv import load_dotenv

from endpoints.auth_endpoint import auth_bp
from endpoints.upload_endpoint import upload_bp

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

app = Flask(__name__)
CORS(app)

# Before request: decode token and set user info to flask.g
@app.before_request
def load_user_from_token():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.user_id = payload.get("user_id")
            g.username = payload.get("username")
            g.role = payload.get("role")
        except jwt.ExpiredSignatureError:
            g.user_id = None
            g.username = None
            g.role = None
        except jwt.InvalidTokenError:
            g.user_id = None
            g.username = None
            g.role = None
    else:
        g.user_id = None
        g.username = None
        g.role = None

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)

if __name__ == "__main__":
    app.run(debug=True)
