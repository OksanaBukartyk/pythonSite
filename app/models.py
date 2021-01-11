from datetime import datetime as dt
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
from flask_bcrypt import check_password_hash
from app import db, login


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    count = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'{self.name}, {self.count}'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64))
    product = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'{self.category}'

