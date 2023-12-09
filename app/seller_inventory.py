from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app as app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from .models.user import User
from .models.seller_inventory import SellerInventory
from datetime import datetime

from flask import Blueprint
bp = Blueprint('seller_inventory', __name__)


# @bp.route('/seller_page/<int:uid>')
# def inventory(uid):
#     page = request.args.get('page', 1, type=int)
#     per_page = 10  
#     offset = (page - 1) * per_page
#     seller_inventory = SellerInventory.get_all_by_uid_with_pagination(uid, per_page, offset)
#     total_items = SellerInventory.count_all_by_uid(uid)  
#     total_pages = (total_items + per_page - 1) // per_page
    
#     return render_template('seller_page.html', inventory=seller_inventory,
#                            page=page, per_page=per_page, total=total_items,
#                            total_pages=total_pages, uid=uid)

#updated inventory page with sort and search functionality implemented
@bp.route('/seller_page/<int:uid>')
def inventory(uid):
    PER_PAGE = 10
    # the default page is generated if no search or sort arguments were passed in
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort_type', default='pid', type=str)
    sort_order = request.args.get('sort_order', default='desc', type=str)
    search_type = request.args.get('search_type', default='product_id', type=str)
    search_order = request.args.get('search_order', type=str)
    offset = (page - 1) * PER_PAGE

    # Assuming you have a total count query
    total_query = '''
        SELECT COUNT(*) AS total_count FROM (SELECT uid, pid, quantity, name, price
        FROM Seller_Inventory, Products
        WHERE uid = :uid
        AND Seller_Inventory.pid = Products.id
        '''

    # Modify the query based on search conditions
    if search_type == 'product_id' and search_order:
        total_query += " AND pid = :search_order"
        search_type = 'pid'
    elif search_type == 'product_name' and search_order:
        total_query += " AND name ~* :search_order"
        search_type = 'name'
    elif search_type == 'quantity' and search_order:
        total_query += " AND quantity = :search_order"
        search_type = 'qty'

    if sort_type == 'product_id':
        sort_type = 'pid'
    elif sort_type == 'product_name':
        sort_type = 'name'
    elif sort_type == 'quantity':
        sort_type = 'qty'

    total_query += ") as B"

    # Execute the modified total count query
    total_result = app.db.execute(total_query, uid=uid, search_order=search_order)
    total = total_result[0][0] if total_result else 0

    # Build the base query
    query = """
        SELECT uid, pid, quantity, name, price, image_url
        FROM Seller_Inventory, Products
        WHERE uid = :uid
        AND Seller_Inventory.pid = Products.id
    """

    # Add search conditions
    if search_type == 'pid' and search_order:
        query += " AND pid = :search_order"
    elif search_type == 'name' and search_order:
        query += " AND name ~* :search_order"
    elif search_type == 'qty' and search_order:
        query += " AND qty = :search_order"

    

    # Add ORDER BY clause
    if sort_type and sort_type != 'None':
        query += f" ORDER BY {sort_type} {sort_order}"

    # Add LIMIT and OFFSET
    query += " LIMIT :limit OFFSET :offset"

    # Execute the query
    seller_inventory = app.db.execute(
        query,
        uid=uid,
        search_order=search_order,
        limit=PER_PAGE,
        offset=offset
    )

    return render_template(
        'seller_page.html',
        inventory=seller_inventory,
        page=page,
        per_page=PER_PAGE,
        total=total,
        total_pages=(total + PER_PAGE - 1) // PER_PAGE,
        uid=uid,
        search_type=search_type,
        search_order=search_order,
        sort_order=sort_order
    )


@bp.route('/seller_orders/<int:uid>', methods=['GET', 'POST'])
def seller_orders(uid):
    PER_PAGE = 10
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort_type', default='order_date', type=str)
    sort_order = request.args.get('sort_order', default='desc', type=str)
    search_type = request.args.get('search_type', default='order_id', type=str)
    search_order = request.args.get('search_order', type=str)
    offset = (page - 1) * PER_PAGE

    if search_type == "order_date":
        search_type = "time_purchased"
    elif search_type == "buyer_address":
        search_type = "address"
    elif search_type == "buyer_name":
        search_type = "name"
    elif search_type == "fulfilled_status":
        search_type = "fulfilled"
    elif search_type == "quantity":
        search_type = "qty"
    elif search_type == "order_id":
        search_type = "id"
    elif search_type == "product_id":
        search_type = "pid"
    elif search_type == "product_name":
        search_type = "p_name"

    if sort_type == "order_date":
        sort_type = "time_purchased"
    elif sort_type == "buyer_address":
        sort_type = "address"
    elif sort_type == "buyer_name":
        sort_type = "name"
    elif sort_type == "fulfilled_status":
        sort_type = "fulfilled"
    elif sort_type == "quantity":
        sort_type = "qty"
    elif sort_type == "order_id":
        sort_type = "id"
    elif sort_type == "product_id":
        sort_type = "pid"
    elif sort_type == "product_name":
        sort_type = "p_name"

    # Assuming you have a total count query
    total_query = '''SELECT COUNT(*) AS total_count FROM (SELECT BoughtLineItems.id, sid, pid, Products.name as p_name, qty, BoughtLineItems.price, time_purchased, CONCAT(users.firstname, ' ', users.lastname) AS name, Users.address, fulfilled, time_fulfilled
        FROM BoughtLineItems, Users, Purchases, Products
        WHERE sid = :uid
        AND Purchases.id = BoughtLineItems.id
        AND Products.id = BoughtLineItems.pid
        AND Users.id = Purchases.uid
        '''

    # Modify the query based on search conditions
    if search_type =='id' and search_order:
        total_query += " AND BoughtLineItems.id = :search_order"
    elif search_type =='pid' and search_order:
        total_query += " AND BoughtLineItems.pid = :search_order"
    elif search_type == "time_purchased" and search_order:
        total_query += " AND time_purchased = :search_order"
    elif search_type == "address" and search_order:
        total_query += " AND address ~* :search_order"
    elif search_type == "fulfilled" and search_order:
        total_query += " AND fulfilled = :search_order"
    elif search_type == "qty" and search_order:
        total_query += " AND qty = :search_order"
    elif search_type == "p_name" and search_order:
        total_query += " AND products.name ~* :search_order"
    elif search_type == "name" and search_order:
        total_query += " AND (users.firstname || ' ' || users.lastname) ~* :search_order"

    total_query += ") as B"

    # Execute the modified total count query
    total_result = app.db.execute(total_query, uid=uid, search_order=search_order)
    total = total_result[0][0] if total_result else 0

    # Build the base query
    query = """
        SELECT BoughtLineItems.id, Users.id as uid, sid, pid, qty, Products.name as p_name, BoughtLineItems.price, time_purchased, CONCAT(users.firstname, ' ', users.lastname) AS name, Users.address, fulfilled, time_fulfilled, Purchases.id as purchase_id
        FROM BoughtLineItems, Users, Purchases, Products
        WHERE sid = :uid
        AND Purchases.id = BoughtLineItems.id
        AND Products.id = BoughtLineItems.pid
        AND Users.id = Purchases.uid
    """

    # Add search conditions
    if search_type =='id' and search_order:
        query += " AND BoughtLineItems.id = :search_order"
    elif search_type =='pid' and search_order:
        query += " AND BoughtLineItems.pid = :search_order"
    elif search_type == "time_purchased" and search_order:
        query += " AND time_purchased = :search_order"
    elif search_type == "address" and search_order:
        query += " AND address ~* :search_order"
    elif search_type == "fulfilled" and search_order:
        query += " AND fulfilled = :search_order"
    elif search_type == "qty" and search_order:
        query += " AND qty = :search_order"
    elif search_type == "p_name" and search_order:
        query += " AND products.name ~* :search_order"
    elif search_type == "name" and search_order:
        query += " AND (users.firstname || ' ' || users.lastname) ~* :search_order"

    # Add ORDER BY clause
    if sort_type and sort_type != 'None':
        query += f" ORDER BY {sort_type} {sort_order}"

    # Add LIMIT and OFFSET
    query += " LIMIT :limit OFFSET :offset"

    # Execute the query
    seller_orders = app.db.execute(
        query,
        uid=uid,
        search_order=search_order,
        limit=PER_PAGE,
        offset=offset
    )

    return render_template(
        'seller_orders.html',
        inventory=seller_orders,
        total=total,
        page=page,
        per_page=PER_PAGE,
        uid=uid,
        search_type=search_type,
        search_order=search_order,
        sort_order=sort_order
    )





@bp.route('/redirect_to_edit_quantity', methods=['GET', 'POST'])
def redirect_to_edit_quantity():
    pid = request.args.get('pid')
    return redirect(url_for('seller_inventory.edit_quantity', pid=pid))

@bp.route('/edit_quantity/<int:pid>', methods=['GET', 'POST'])
def edit_quantity(pid):
    uid = current_user.id
    product = SellerInventory.get_by_uid_pid(uid, pid)    
    return render_template('edit_inventory_quantity.html',
                           product=product) 


@bp.route('/update_quantity', methods=['GET', 'POST'])
def update_quantity():
    new_quantity = request.form.get('new_quantity')
    pid = request.form.get('pid')
    uid = current_user.id

    if new_quantity == "0":
        update_query = ('''DELETE FROM Seller_Inventory WHERE uid = :uid AND pid = :pid''')
        app.db.execute(update_query, uid = uid, pid = pid)
        if SellerInventory.get_by_pid(pid) == None:
            availability_query = ('''UPDATE Products SET available = FALSE WHERE id = :pid''')
            app.db.execute(availability_query, pid=pid)
    else:
        update_query = ('''UPDATE Seller_Inventory SET quantity = :new_quantity WHERE uid = :uid AND pid = :pid''')
        app.db.execute(update_query, uid = uid, new_quantity = new_quantity, pid = pid)

    
    # Perform the update query using the data provided

    return redirect(url_for('users.redirect_to_seller_inventory'))


@bp.route('/redirect_to_add_product_page', methods=['GET', 'POST'])
def redirect_to_add_product_page():
    uid = current_user.id
    return redirect(url_for('seller_inventory.add_product_page', uid=uid))

@bp.route('/add_product_page/<int:uid>', methods=['GET', 'POST'])
def add_product_page(uid):
    return render_template('add_product.html')

@bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    uid = current_user.id
    p_name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    category = request.form.get('category')
    tag = request.form.get('tag')
    subtag = request.form.get('subtag')
    quantity = request.form.get('quantity')
    picture = request.form.get('picture')

    # Check if the product already exists
    pid = SellerInventory.get_pid_by_name(p_name)

    if pid is not None:
        product_check = SellerInventory.get_by_uid_pid(uid, pid)
        if product_check is not None:
            flash("Product already exists in seller inventory. Operation Cancelled.", 'error')
            return redirect(url_for('users.redirect_to_seller_inventory'))
        else:
            # Product doesn't exist in the seller's inventory, add a new entry
            insert_query = '''
                INSERT INTO Seller_Inventory (uid, pid, quantity)
                VALUES (:uid, :pid, :quantity)
            '''
            app.db.execute(insert_query, uid=uid, pid=pid, quantity=quantity)
            # Update availability in the Products table
            availability_query = '''
                UPDATE Products
                SET available = TRUE
                WHERE id = :pid
            '''
            app.db.execute(availability_query, pid=pid)
    else:
        # Product does not exist, insert into Products table to generate a new pid
        insert_product_query = '''
            INSERT INTO Products (name, price, description, available, category, tag, subtag, image_url)
            VALUES (:name, :price, :description, TRUE, :category, :tag, :subtag, :image_url)
            RETURNING id
        '''
        result = app.db.execute(
            insert_product_query,
            name=p_name,
            price=price,
            description=description,
            category=category,
            tag=tag,
            subtag=subtag,
            image_url=picture
        )
        # pid = result[0] if result else None
        pid = SellerInventory.get_pid_by_name(p_name)
        # Insert into Seller_Inventory
        if pid is not None:
            insert_inventory_query = '''
                INSERT INTO Seller_Inventory (uid, pid, quantity)
                VALUES (:uid, :pid, :quantity)
            '''
            app.db.execute(insert_inventory_query, uid=uid, pid=pid, quantity=quantity)

    flash("Product added to seller inventory successfully.", 'success')
    return redirect(url_for('users.redirect_to_seller_inventory'))

@bp.route('/toggle_fulfillment/<int:order_id>/<int:pid>/<int:fulfilled>/', methods=['GET', 'POST'])
def toggle_fulfillment(order_id, pid, fulfilled):
    uid = current_user.id
    current_time = datetime.utcnow()

    # Toggle the fulfillment status
    if fulfilled:
        update_query = '''
            UPDATE BoughtLineItems
            SET fulfilled = FALSE, time_fulfilled = NULL
            WHERE id = :order_id AND sid = :uid AND pid = :pid
        '''
    else:
        update_query = '''
            UPDATE BoughtLineItems
            SET fulfilled = TRUE, time_fulfilled = :current_time
            WHERE id = :order_id AND sid = :uid AND pid = :pid
        '''
    app.db.execute(update_query, order_id=order_id, uid=uid, pid=pid, current_time=current_time)

    return redirect(url_for('seller_inventory.seller_orders', uid=uid))

