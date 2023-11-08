from flask import render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user

from .models.product import Product
from flask import current_app as app


from flask import Blueprint
bp = Blueprint('products', __name__)

@bp.route('/get_products', methods=['POST'])
def get_products():
    k = request.form.get('k')  # Get the value of 'k' from the form

    # Convert 'k' to an integer
    try:
        k = int(k)
    except ValueError:
        return "Invalid input for 'k'. Please enter a valid number."
    query = '''
    SELECT id, name, price, description, available, category, image_url
    FROM products
    WHERE available = true;
    '''
    products = app.db.execute(query)

    # Pass the top_k_products data to a new template for displaying the results
    return render_template('products.html', products=products)

@bp.route('/category_filter', methods=['GET', 'POST'])
def category_filter():
    category = request.args.get('category')
    
    if category == '--':
        query = '''
        SELECT id, name, price, description, available, category, image_url
        FROM products
        WHERE available = true;
        '''
    else: 
        query = '''
        SELECT id, name, price, description, available, category, image_url
        FROM products
        WHERE available = true AND category = :category;
        '''

    category_filter = app.db.execute(query, category=category) 
    
    return render_template('products.html', products=category_filter)   
    
