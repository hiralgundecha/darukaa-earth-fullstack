import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .auth import auth_bp
from .config import Config
from .models import db
from .routes import api_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    JWTManager(app)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","))

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
