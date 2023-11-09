from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
import datetime
import csv

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
    return render_template('carts.html', cart_items=cart_items, uid=uid)

@bp.route('/redirect_to_user_cart', methods=['POST'])
def redirect_to_user_cart():
    user_id = request.form.get('user_id')
    return redirect(url_for('carts.cart', uid=user_id))

@bp.route('/update_all_quantities', methods=['POST'])
def update_all_quantities():
    # Loop over all expected quantity fields
    for key in request.form:
        if key.startswith('quantity_'):
            liid = key.split('_')[1]  # Extract line item ID from the key
            new_quantity = request.form[key]
            if new_quantity:
                # Update the quantity in the database
                app.db.execute('''
                    UPDATE LineItems
                    SET qty = :new_quantity
                    WHERE liid = :liid
                    ''', new_quantity=new_quantity, liid=liid)

    # Redirect back to the cart page
    uid = request.form.get('user_id')
    flash("All quantities updated successfully!", 'success')
    return redirect(url_for('carts.cart', uid=uid))

@bp.route('/remove_item/<int:liid>', methods=['POST'])
def remove_item(liid):
    # Ensure the user is logged in to remove items
    if not current_user.is_authenticated:
        flash("You must be logged in to remove items.", 'danger')
        return redirect(url_for('users.login'))

    try:
        # Execute the delete query
        app.db.execute('''
            DELETE FROM LineItems
            WHERE liid = :liid
            AND cid = (
                SELECT cid
                FROM Carts
                WHERE uid = :uid
            )
        ''', liid=liid, uid=current_user.id)
        flash("Item removed successfully!", 'success')
    except Exception as e:
        # Log this error
        flash("An error occurred while removing the item.", 'danger')

    # Redirect back to the cart page
    return redirect(url_for('carts.cart', uid=current_user.id))