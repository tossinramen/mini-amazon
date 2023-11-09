from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from werkzeug.exceptions import abort

from .models.product import Product
from flask import current_app as app


from flask import Blueprint
bp = Blueprint('products', __name__)

PER_PAGE = 10

@bp.route('/get_products', methods=['GET', 'POST'])
def get_products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all') 
    offset = (page - 1) * PER_PAGE
    search = ''

    if request.method == 'POST':
        search = request.form.get('keywords')  # Get the value from the form
        if not search:
            abort(400, "Search keywords required")
        return redirect(url_for('products.get_products', page=1, keywords=search, category=category))

    elif request.method == 'GET':
        search = request.args.get('keywords', '')  # Get the value from the URL query parameter

    keywords = search.split() if search else []

    # Start building the base query
    base_query = '''
    FROM products
    WHERE (available = true OR available = false)
    '''

    # Add category filter if applicable
    if category != 'all':
        base_query += f' AND category = :category '

    # Append search criteria to the base query
    for keyword in keywords:
        base_query += f" AND (name ~* '\\m{keyword}\\M' OR description ~* '\\m{keyword}\\M')"

    # Execute the count query with search criteria
    total_query = 'SELECT COUNT(*) ' + base_query
    total_result = app.db.execute(total_query, category=category)
    total = total_result[0][0] if total_result else 0

    # Execute the main query with search criteria and pagination
    main_query = 'SELECT id, name, price, description, available, category, image_url ' + base_query
    main_query += ' LIMIT :limit OFFSET :offset;'
    products = app.db.execute(main_query, limit=PER_PAGE, offset=offset, category=category)

    return render_template('products.html', products=products, keywords=keywords, total=total, per_page=PER_PAGE, page=page, category=category)
