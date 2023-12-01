from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from .models.user import User
from .models.seller_inventory import SellerInventory

from flask import Blueprint
bp = Blueprint('seller_inventory', __name__)


@bp.route('/seller_page/<int:uid>')
def inventory(uid):
    page = request.args.get('page', 1, type=int)
    per_page = 10  
    offset = (page - 1) * per_page
    seller_inventory = SellerInventory.get_all_by_uid_with_pagination(uid, per_page, offset)
    total_items = SellerInventory.count_all_by_uid(uid)  
    total_pages = (total_items + per_page - 1) // per_page  
    return render_template('seller_page.html', inventory=seller_inventory,
                           page=page, per_page=per_page, total=total_items,
                           total_pages=total_pages, uid=uid)

@bp.route('/past_seller_orders/<int:uid>')
def past_seller_orders(uid):
    PER_PAGE = 10 
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM BoughtLineItems WHERE sid = :uid', uid=uid)
    # Assuming the first element of the tuple is the 'total_count'.
    total = total_result[0][0] if total_result else 0

    query = """
        SELECT id, sid, pid, qty, price, fulfilled
        FROM BoughtLineItems
        WHERE sid = :uid
        LIMIT :limit OFFSET :offset
    """
    
    seller_orders = app.db.execute(query, uid=uid, limit=PER_PAGE, offset=offset)  
    
    return render_template('seller_orders.html', inventory=seller_orders, total=total,
                           page=page, per_page=PER_PAGE, uid=uid)

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
