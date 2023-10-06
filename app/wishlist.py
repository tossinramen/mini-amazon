from flask import render_template
from flask_login import current_user
from flask import jsonify
import datetime

from .models.product import Product
from .models.wishlist import WishListItem

from flask import Blueprint
bp = Blueprint('wishes', __name__)


@bp.route('/wishlist')
def wishes():
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        wishlists = WishListItem.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        wishlists = None
    # render the page by adding information to the index.html file
    return jsonify([item.__dict__ for item in wishlists])
