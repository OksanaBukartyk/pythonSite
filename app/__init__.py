from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_admin import Admin

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

from app.adminstrations.forms import UserAdminView, PostAdminView,MyAdminIndexView,HelloView
admin = Admin(app, 'Admin Panel', index_view=MyAdminIndexView())

from .models import User, Post

admin.add_view(UserAdminView(User, db.session))
admin.add_view(PostAdminView(Post, db.session))
admin.add_view(HelloView(name='Exit'))

from app.main.views import main
from app.posts.views import posts
from app.account.views import account
from app.auth.views import auth
from app.adminstrations.views import administrations

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(posts, url_prefix='/posts')
app.register_blueprint(account,url_prefix='/account')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(administrations, url_prefix='/administrations')

