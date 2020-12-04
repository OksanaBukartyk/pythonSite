from app import db
from datetime import datetime as dt

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    count = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    def __repr__(self):
        return f'{self.name}, {self.count}'


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(64))
    product = db.relationship('Product', backref='company', lazy='dynamic')

    def __repr__(self):
        return f'{self.company}'
