from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from celery import Celery
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

app.config['broker_url'] = 'sqla+sqlite:///celerydb.sqlite'
app.config['result_backend'] = 'db+sqlite:///celerydb.sqlite'


# bind the extension with app
db.init_app(app)
jwt.init_app(app)

celery = Celery(app.name, broker=app.config['broker_url'])
celery.conf.update(app.config)


class ContextTask(celery.Task):
    def __call__(self,*args,**kwargs):
        with app.app_context():
            return self.run(*args,**kwargs)
celery.Task  = ContextTask


from app.models.user import User,Document,Requirement
from app.routes import routes


with app.app_context():
    db.create_all()