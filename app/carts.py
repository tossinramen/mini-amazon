from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
import datetime

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