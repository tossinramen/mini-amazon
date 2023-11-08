from flask import render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user

from .models.product import Product
from flask import current_app as app


from flask import Blueprint
bp = Blueprint('products', __name__)

@bp.route('/get_top_k_products', methods=['POST'])
def get_top_k_products():
    k = request.form.get('k')  # Get the value of 'k' from the form


    # Convert 'k' to an integer
    try:
        k = int(k)
    except ValueError:
        return "Invalid input for 'k'. Please enter a valid number."

    category = 'all'
    # if request.method == 'POST':
    #     try:
    #         category = request.form.get('category')
    #     except:
    #         category = all
    if request.method == 'POST':
        category = request.form.get('category', 'all')

    if category == 'all':
        query = '''
        SELECT id, name, price, description, available, category, image_url
        FROM products
        WHERE available = true
        ORDER BY price DESC
        LIMIT :limit;
        '''
    else:
        query = '''
        SELECT id, name, price, description, available, category, image_url
        FROM products
        WHERE available = true AND category = :category
        ORDER BY price DESC
        LIMIT :limit;
        '''
    top_k_products = app.db.execute(query, limit=k)

    # Pass the top_k_products data to a new template for displaying the results
    return render_template('products.html', top_k_products=top_k_products)
    
