from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_admin import Admin

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login = LoginManager()
admin = Admin(name='Blog', template_mode='bootstrap3')



def create_app(config_app=Config):
    from .models import User, Post
    app = Flask(__name__)
    app.config.from_object(config_app)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login.init_app(app)
    login.login_view = 'user_bp.login'
    login.login_message_category = 'info'
    login.session_protection = "strong"


    from .models import User, Post, Post_API
    from app.adminstrations.forms import UserAdminView, PostAdminView,HelloView, ModelView

    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(PostAdminView(Post, db.session))
    admin.add_view(HelloView(name='Exit'))
    admin.add_view(ModelView(Post_API, db.session))

    create_blueprints(app)
    return  app

def create_blueprints(app):
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
