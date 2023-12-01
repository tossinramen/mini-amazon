from flask import Blueprint, render_template, request, abort
from flask import current_app as app

bp = Blueprint('products', __name__)

PER_PAGE = 10

tag_subtag_mapping = {
    'Electronics': {
        'Smartphones': ('iPhone', 'Samsung Galaxy', 'Google Pixel', 'OnePlus'),
        'Laptops': ('MacBook', 'Dell XPS', 'HP Spectre', 'Lenovo ThinkPad'),
        'Headphones': ('Over-ear', 'In-ear', 'Wireless', 'Noise-canceling'),
        'Smartwatches': ('Apple Watch', 'Samsung Galaxy Watch', 'Fitbit', 'Garmin'),
        'Cameras': ('DSLR', 'Mirrorless', 'Point-and-Shoot', 'Action Cameras'),
        'Gaming Consoles': ('PlayStation', 'Xbox', 'Nintendo Switch'),
        'Smart Home': ('Smart Speakers', 'Smart Lights', 'Smart Thermostats', 'Smart Security Cameras')
    },
    'Fashion and Apparel': {
        'Clothing': ('T-Shirts', 'Dresses', 'Jeans', 'Sweaters'),
        'Footwear': ('Sneakers', 'Boots', 'Sandals', 'Heels'),
        'Accessories': ('Hats', 'Scarves', 'Bags', 'Watches')
    },
    'Home and Garden': {
        'Furniture': ('Sofas', 'Chairs', 'Tables', 'Beds'),
        'Decor': ('Lamps', 'Candles', 'Mirrors', 'Wall Art'),
        'Appliances': ('Refrigerators', 'Microwaves', 'Washing Machines', 'Coffee Makers')
    },
    'Books and Media': {
        'Books': ('Fiction', 'Non-fiction', 'Mystery', 'Science Fiction'),
        'Movies': ('Action', 'Comedy', 'Drama', 'Science Fiction'),
        'Music': ('Rock', 'Pop', 'Hip Hop', 'Electronic')
    },
    'Health and Beauty': {
        'Skincare': ('Cleansers', 'Moisturizers', 'Serums', 'Sunscreen'),
        'Makeup': ('Lipstick', 'Eyeshadow', 'Foundation', 'Mascara'),
        'Fitness': ('Yoga Mats', 'Dumbbells', 'Resistance Bands', 'Treadmills')
    }
}

def get_search_keywords():
    if request.method == 'POST':
        search = request.form.get('keywords')
        if not search:
            abort(400, "Search keywords required")
        return search
    elif request.method == 'GET':
        return request.args.get('keywords', '')

def category_tag_filter(base_query, selected, cat_or_tag):
    if selected and 'all' not in selected:
        conditions = [f"{cat_or_tag} = '{value}'" for value in selected]
        base_query += f" AND ({' OR '.join(conditions)})"
    return base_query

@bp.route('/get_products', methods=['GET', 'POST'])
def get_products():
    page = request.args.get('page', 1, type=int)
    selected_categories = request.args.getlist('categories')
    selected_tags = request.args.getlist('tags')
    selected_subtags = request.args.getlist('subtags')
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

    # Add category/tag filter if applicable
    base_query = category_tag_filter(base_query, selected_categories, 'category')
    base_query = category_tag_filter(base_query, selected_tags, 'tag')
    base_query = category_tag_filter(base_query, selected_subtags, 'subtag')

    # Append search criteria to the base query
    for keyword in keywords:
        base_query += f" AND (name ~* '\\m{keyword}\\M' OR description ~* '\\m{keyword}\\M')"

    # Execute the count query with search criteria
    total_query = 'SELECT COUNT(*) ' + base_query
    total_result = app.db.execute(total_query)
    total = total_result[0][0] if total_result else 0

    # Execute the main query with search criteria and pagination
    main_query = 'SELECT id, name, price, description, available, category, image_url, \
                (SELECT AVG(stars) FROM product_rating WHERE product_rating.pid = products.id GROUP BY pid) AS avg_stars' + base_query
    if sort_by and sort_by != 'all' and sort_order:
        main_query += f' ORDER BY {sort_by} {sort_order}'
    main_query += ' LIMIT :limit OFFSET :offset;'
    products = app.db.execute(main_query, limit=PER_PAGE, offset=offset)

    return render_template('products.html', products=products,
                           keywords=keywords,
                           total=total,
                           per_page=PER_PAGE,
                           page=page,
                           selected_categories=selected_categories,
                           selected_tags=selected_tags,
                           selected_subtags=selected_subtags,
                           tag_subtag_mapping=tag_subtag_mapping,
                           sort_by=sort_by,
                           sort_order=sort_order)

@bp.route('/product_details/<int:pid>', methods=['GET', 'POST'])
def product_details(pid):
    # product info from products table
    product_query = '''
    SELECT id, name, price, description, available, category, image_url, \
    (SELECT AVG(stars) FROM product_rating WHERE pid = :pid GROUP BY pid) AS avg_stars
    FROM products
    WHERE id = :pid
    '''
    product_result = app.db.execute(product_query, pid=pid)

    if product_result:
        name = product_result[0][1]
        price = product_result[0][2]
        description = product_result[0][3]
        available = product_result[0][4]
        category = product_result[0][5]
        image_url = product_result[0][6]
        avg_stars = product_result[0][7]

    # list each seller and their current quantities
    seller_query = f'''
    SELECT uid, quantity,
           CONCAT(users.firstname, ' ', users.lastname) AS name
    FROM seller_inventory
    JOIN users ON users.id = seller_inventory.uid
    WHERE pid = {pid}
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