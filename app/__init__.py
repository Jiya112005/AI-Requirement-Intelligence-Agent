from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
load_dotenv()

# instances created
db = SQLAlchemy()
jwt = JWTManager()

# app binding extensions
app = Flask(__name__)

# configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# bind the extension with app
db.init_app(app)
jwt.init_app(app)

from app.models.user import User,Document,Requirement
from app.routes import routes


with app.app_context():
    db.create_all()