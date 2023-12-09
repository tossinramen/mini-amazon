from flask import Blueprint, render_template, redirect, url_for, abort, request,  current_app as app
from flask_login import login_required, current_user
import datetime

from .models.product import Product
from .models.wishlist import WishListItem

bp = Blueprint('wishes', __name__)

@bp.route('/wishlist')
def wishes():
    wishlists = WishListItem.get_all_by_uid_since(
        current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    return render_template('wishlist.html', wishlists=wishlists)

# @bp.route('/add_to_wishlist/<int:pid>', methods=['POST'])
# def add_to_wishlist(pid):
#     # check if the product is already in the wishlist
#     existing_item = WishListItem.exists(current_user.id, pid)
#     if existing_item:
#         abort(400, 'Item is already in your wishlist!')
#     else:
#         # add item to wishlist
#         WishListItem.register(current_user.id, pid, datetime.datetime.now())
#     return redirect(url_for('wishes.wishes'))

@bp.route('/remove_from_wishlist/<int:pid>', methods=['POST'])
def remove_from_wishlist(pid):
    # Remove item from wishlist
    WishListItem.remove(current_user.id, pid)
    return redirect(url_for('wishes.wishes'))
'''
@bp.route('/add_to_cart/<int:pid>', methods=['POST'])
def add_to_cart(id, pid, sid, price):
    # Remove item from wishlist
    app.db.execute(''''''
            INSERT INTO CartLineItems(id, sid, pid, qty, price)
            VALUES(:id, :pid, :sid, :pid, :qty, :price)'''''', id = id, sid=sid, pid=pid, qty=1, price=price)
    WishListItem.remove(current_user.id, pid)
    return redirect(url_for('wishes.wishes'))
'''

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
    
    # extract and display product details if found
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

    # render detailed product with fetched info
    return render_template('detailed_product.html', name=name,
                           price=price,
                           description=description,
                           available=available,
                           category=category,
                           image_url=image_url,
                           avg_stars=avg_stars,
                           seller_info=seller_info)

# remove an item from cart
@bp.route('/remove_item/<int:id>', methods=['GET', 'POST'])
def remove_item(id):
    # delete specified item
    app.db.execute('''
        DELETE FROM Wishes
        WHERE id = :id
        ''', id=id)
    # redirect to cart pg
    return redirect(url_for('carts.view_wishlist', uid=current_user.id))