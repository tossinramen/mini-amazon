from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
import datetime

from .models.cart import Cart
from .models.line_item import LineItem

from flask import Blueprint
bp = Blueprint('carts', __name__)

@bp.route('/cart/<int:uid>', methods=['GET', 'POST'])
def cart(uid):
    # user check
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = uid))

    if count > 0:
        # get current user's cart
        cart_items = Cart.get_items_by_uid(uid)
    else:
        cart_items = None

    # render cart pg with line items
    return render_template('carts.html', cart_items=cart_items)

@bp.route('/redirect_to_user_cart', methods=['POST'])
def redirect_to_user_cart():
    user_id = request.form.get('user_id')
    return redirect(url_for('carts.cart', uid=user_id))
