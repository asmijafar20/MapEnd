import os
from flask import Flask
from journal.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import datetime
from flask_login import UserMixin
from flaskext.markdown import Markdown

app = Flask(__name__)
app.config.from_object(Config)

# using config here for testing only 
app.config['SECRET_KEY'] = '64529050a317171fa534714b75b55b03'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# otherwise use config.from_object to get environment vars

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
bcrypt = Bcrypt(app)
markdown = Markdown(app)


# registering blueprints
from journal.auth.routes import auth
from journal.main.routes import main


app.register_blueprint(auth)
app.register_blueprint(main)
