from flask_script import Manager, prompt_bool, Command

from app import db
from app.models import User, Post

manager = Manager(usage="Perform database operations")


@manager.command
def createdb():
    db.create_all()


@manager.command
def drop():
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def recreate():
    if prompt_bool(
            "Are you sure you want to rebuild your database"):
        db.drop_all()


@manager.command
def init_data():
    u = User(username="Test", email="test@mail.com", password_hash="password")
    db.session.add(u)
    p = Post(body="test post", author=u)
    db.session.add(p)
    db.session.commit()
    print("Initialization completed")