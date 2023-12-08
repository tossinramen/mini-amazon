from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
import datetime
import csv
import random
import hashlib

from .models.cart import Cart
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('carts', __name__)

@bp.route('/cart/<int:uid>')
def cart(uid):
    # user check
    # uid=current_user.get_id
    # cart = Cart.get_by_uid(uid)
    # cart_id = cart.id
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = uid))
    if count > 0:
        # get current user's cart
        cart_items = Cart.get_items_by_uid(uid)
    else:
        cart_items = None

    if cart_items is None:
        cart_items = []  # ensure cart items is always an iterable

    # render cart pg with line items
    return render_template('carts.html', cart_items=cart_items, uid=uid)

@bp.route('/redirect_to_user_cart')
def redirect_to_user_cart():
    user_id = request.form.get('user_id')
    return redirect(url_for('carts.cart', uid=current_user.id))

@bp.route('/update_all_quantities', methods=['GET', 'POST'])
def update_all_quantities():
    print(request.form)
    for key in request.form:
        if key.startswith('quantity_'):
            # identifiers extracted
            _, id, pid, sid = key.split('_')
            # line_item = LineItem.get_by_id(id)
            # id, sid, pid = line_item[0], line_item[1]
            new_quantity = request.form[key]
            
            app.db.execute('''
                UPDATE CartLineItems
                SET qty = :new_quantity
                WHERE id = :id
                AND pid = :pid
                AND sid = :sid
                ''', new_quantity=new_quantity, id=id, pid=pid, sid=sid, uid=current_user.id)
    return redirect(url_for('carts.cart', uid=current_user.id))

@bp.route('/remove_item/<int:id>/<int:pid>/<int:sid>', methods=['GET', 'POST'])
def remove_item(id, pid, sid):
    app.db.execute('''
        DELETE FROM CartLineItems
        WHERE id = :id
        AND pid = :pid
        AND sid = :sid
        ''', id=id, pid=pid, sid=sid, uid=current_user.id)
    flash("Item removed successfully!", 'success')
    return redirect(url_for('carts.cart', uid=current_user.id))





PER_PAGE = 10
@bp.route('/orders/<int:uid>')
def orders(uid):
    if not current_user.is_authenticated or current_user.id != uid:
        return redirect(url_for('users.login'))
    
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    raw_order_items = get_orders_by_uid(uid, limit=PER_PAGE, offset=offset)

    order_items = []
    used_end_parts = set() 
    for item in raw_order_items:
        fulfillment_time = item['fulfillment_time']
        if fulfillment_time:
            formatted_time = fulfillment_time.isoformat()
            hash_input = f"{item['purchase_id']}-{formatted_time}".encode()
        else:
            hash_input = f"{item['purchase_id']}".encode()

        hash_object = hashlib.sha256(hash_input)
        base_order_end_part = hash_object.hexdigest()[:10]

        order_end_part = base_order_end_part
        i = 0
        while order_end_part in used_end_parts:
            i += 1
            order_end_part = f"{base_order_end_part}-{i}"

        used_end_parts.add(order_end_part)
        order_number = f"ORDER {item['purchase_id']}-{order_end_part}"
        item['order_number'] = order_number
        order_items.append(item)

    total_orders = get_total_orders_count(uid)
    return render_template('orders.html', order_items=order_items, uid=uid, page=page, per_page=PER_PAGE, total=total_orders)

def get_orders_by_uid(uid, limit, offset):
    sql_query = '''
        SELECT pur.id as purchase_id,
               SUM(bli.price * bli.qty) as total_price,
               BOOL_AND(bli.fulfilled) as all_fulfilled,
               MAX(CASE WHEN bli.fulfilled THEN pur.time_purchased ELSE NULL END) as fulfillment_time
        FROM BoughtLineItems bli
        INNER JOIN Products p ON bli.pid = p.id
        INNER JOIN Purchases pur ON bli.id = pur.id
        WHERE pur.uid = :uid
        GROUP BY pur.id
        ORDER BY pur.time_purchased DESC  -- Added sorting by purchase time in descending order
        LIMIT :limit OFFSET :offset
    '''
    result = app.db.execute(sql_query, uid=uid, limit=limit, offset=offset)
    order_items = []
    for row in result:
        item = {
            'purchase_id': row[0], 
            'total_price': row[1], 
            'fulfilled': row[2],
            'fulfillment_time': row[3]  
        }
        order_items.append(item)
    return order_items


def get_total_orders_count(uid):
    count_query = '''
        SELECT COUNT(DISTINCT pur.id)
        FROM BoughtLineItems bli
        INNER JOIN Purchases pur ON bli.id = pur.id
        WHERE pur.uid = :uid
    '''
    total_result = app.db.execute(count_query, uid=uid)
    total = total_result[0][0] if total_result else 0
    return total

@bp.route('/order_details/<int:uid>/<int:purchase_id>')
def order_details(uid, purchase_id):
    if not current_user.is_authenticated or current_user.id != uid:
        return redirect(url_for('users.login'))


    order_details = get_order_details(purchase_id)

    return render_template('order_details.html', order_details=order_details, order_number=f"ORDER #{purchase_id}")

def get_order_details(purchase_id):
    sql_query = '''
        SELECT pr.name, bli.qty, bli.price, u.firstname, u.lastname, bli.fulfilled, pur.time_purchased
        FROM BoughtLineItems bli
        INNER JOIN Products pr ON bli.pid = pr.id
        INNER JOIN Users u ON bli.sid = u.id
        INNER JOIN Purchases pur ON bli.id = pur.id
        WHERE pur.id = :purchase_id
    '''
    result = app.db.execute(sql_query, purchase_id=purchase_id)
    order_details = []

    for row in result:
        detail = {
            'product_name': row[0],
            'quantity': row[1],
            'price': row[2],
            'seller_name': f"{row[3]} {row[4]}",
            'fulfilled': row[5],
            'fulfillment_time': row[6] if row[5] else 'Purchase not fulfilled'
        }
        order_details.append(detail)

    return order_details
    return redirect(url_for('carts.cart', uid=current_user.id))

@bp.route('/submit_cart', methods=['POST'])
def submit_cart():
    user_id = current_user.id
    # fetch cart items
    cart_items = Cart.get_items_by_uid(user_id)
    
    id = Cart.get_id_by_uid(user_id)
    Purchase.create(id, user_id)

    purchase_id = id

    for item in cart_items:
        app.db.execute('''
            INSERT INTO BoughtLineItems(id, sid, pid, qty, price)
            VALUES(:purchase_id, :sid, :pid, :qty, :price)
        ''', purchase_id=purchase_id, sid=item.sid, pid=item.pid, qty=item.qty, price=item.price)

    # clear cart items
    
    Cart.clear_cart(user_id)

    return redirect(url_for('users.user_purchases', uid=user_id))
