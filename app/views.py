import datetime

from flask import render_template, flash, redirect, url_for, request, jsonify,abort
from app import app, db
from app.forms import CreateProductForm, UpdateProductForm
from .models import Product, Category
import os


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products/add', methods=['PUT'])
def add_product():
    req = request.json
    if not req:
        abort(400)

    product = Product( name=req.get('name'),
                       price=req.get('price'),
                       count=req.get('count'),
                       company_id=req.get('company_id'))
    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'The post has been created!'})


@app.route('/products', methods=['GET', 'POST'])
def products():
    cat = Category.query.all()
    categories = [(i.id, i.category) for i in cat]
    products =Product.query.all()
    output = []
    for post in products:
        post_data = {}
        post_data['id'] = post.id
        post_data['name'] = post.name
        post_data['count'] = post.count
        post_data['price'] = post.price
        post_data['company_id'] = product.company_id
        post_data['timestamp'] = post.timestamp


        output.append(post_data)
    return jsonify({'posts': output})





@app.route('/products/<int:product_id>', methods=['GET', 'POST'])
def product(product_id):
    post = Product.query.filter_by(id=product_id).first()
    if not post:
        return jsonify({'message': 'No user found!'})

    post_data = {}

    post_data['id'] = post.id
    post_data['name'] = post.name
    post_data['count'] = post.count
    post_data['price'] = post.price
    post_data['company_id'] = product.company_id
    post_data['timestamp'] = post.timestamp

    return jsonify({'post': post_data})


@app.route('/products/<int:product_id>/delete', methods=['GET', 'POST'])
def delete_product(product_id):
    post = Product.query.get(product_id)
    if not post:
        return jsonify({'message': 'No post found!'})
    db.session.delete(post)
    db.session.commit()
    flash("Product was deleted", category="info")

    return jsonify({'message': 'The post has been deleted!'})


@app.route('/products/<int:product_id>/update', methods=[ 'PATCH'])
def update_post(product_id):
    post = Product.query.get(product_id)
    req = request.json
    if not req:
        abort(400)
    if not post:
        return jsonify({'message': 'No post found!'})

    post.name = req.get('name')
    post.count = req.get('count')
    post.price=req.get('price')
    post.company_id=req.get('company')

    db.session.commit()

    return jsonify({'message': 'The post has been updated!'})