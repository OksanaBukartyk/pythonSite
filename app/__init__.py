
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView



app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'info'
login.session_protection = 'strong'

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

from app import views, models

admin = Admin(app, 'Admin Panel', index_view=views.MyAdminIndexView())

from .models import User, Post
from .forms import UserAdminView, PostAdminView
admin.add_view(UserAdminView(User, db.session))
admin.add_view(PostAdminView(Post, db.session))

admin.add_view(views.HelloView(name='Exit'))