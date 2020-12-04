from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import CreateProductForm, UpdateProductForm
from .models import Product, Company
import os


@app.route('/add', methods=['GET', 'POST'])
def add_product():
    cat = Company.query.all()
    companies = [(i.id, i.company) for i in cat]
    form = CreateProductForm()
    form.company.choices = companies
    if form.validate_on_submit():
        product = Product(name=form.name.data,
                          count=form.count.data, price=form.price.data,
                          type=form.type.data, company_id=form.company.data)
        db.session.add(product)
        db.session.commit()
        flash("Product was created", category="info")
        return redirect(url_for('products'))

    return render_template('add.html', form=form)


@app.route('/products', methods=['GET', 'POST'])
def products():
    q = request.args.get('q')
    if q:
        products = Product.query.filter(Product.name.contains(q) )
    else:
        products = Product.query.order_by(Product.timestamp.desc())

    return render_template('products.html', products=products)


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product(product_id):
    cat = Company.query.all()
    companies = [(i.id, i.company) for i in cat]
    form = UpdateProductForm()
    form.company.choices = companies
    product = Product.query.filter_by(id=product_id).first()
    if form.validate_on_submit():

        product.name = form.name.data
        product.count = form.count.data
        product.price = form.price.data
        product.type = form.type.data
        product.company_id = form.company.data
        db.session.commit()
        flash("Product was updated", category="info")
        return redirect(url_for('product', product_id=product.id))

    return render_template('product.html', product=product, form=form)


@app.route('/products/<int:product_id>/delete', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product was deleted", category="info")
    return redirect(url_for('products'))