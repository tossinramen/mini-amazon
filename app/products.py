from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from werkzeug.exceptions import abort

from .models.product import Product
from flask import current_app as app


from flask import Blueprint
bp = Blueprint('products', __name__)

PER_PAGE = 10

def get_search_keywords():
    if request.method == 'POST':
        search = request.form.get('keywords')
        if not search:
            abort(400, "Search keywords required")
        return search
    elif request.method == 'GET':
        return request.args.get('keywords', '')

@bp.route('/get_products', methods=['GET', 'POST'])
def get_products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all') 
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    offset = (page - 1) * PER_PAGE

    search = get_search_keywords()
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
    main_query = 'SELECT id, name, price, description, available, category, image_url, \
                (SELECT AVG(stars) FROM product_rating WHERE product_rating.pid = products.id GROUP BY pid) AS avg_stars' + base_query
    if sort_by:
        main_query += f' ORDER BY {sort_by}'
        if sort_order:
            main_query += f' {sort_order}'
    main_query += ' LIMIT :limit OFFSET :offset;'
    products = app.db.execute(main_query, limit=PER_PAGE, offset=offset, category=category)

    return render_template('products.html', products=products, 
                                            keywords=keywords, 
                                            total=total, 
                                            per_page=PER_PAGE, 
                                            page=page, 
                                            category=category)

@bp.route('/product_details', methods=['GET', 'POST'])
def product_details(pid):
    # product info from products table
    product_query = '''
    SELECT id, name, price, description, available, category, image_url, \
    (SELECT AVG(stars) FROM product_rating WHERE pid = :pid GROUP BY pid) AS avg_stars
    FROM products
    WHERE id = :pid
    '''
    product_result = app.db.execute(product_query, pid=pid).fetchone()

    if result:
        name = result['name']
        price = result['price']
        description = result['description']
        available = result['available']
        category = result['category']
        image_url = result['image_url']
        avg_stars = result['avg_stars']

    # list each seller and their current quantities
    seller_query = '''
    SELECT uid, quantity
    FROM seller_inventory
    WHERE pid = :pid
    '''

    seller_info = app.db.execute(seller_query)

    return render_template('detailed_product.html', name=name, 
                                                    price=price, 
                                                    description=description, 
                                                    available=available, 
                                                    category=category,
                                                    image_url=image_url,
                                                    avg_stars=avg_stars,
                                                    seller_info=seller_info)
