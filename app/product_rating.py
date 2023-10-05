from flask import render_template
from flask_login import current_user
import datetime

from .models.product import Product
from .models.product_rating import Product_Rating
from .models.purchase import Purchase

from flask import Blueprint
from flask import jsonify
bp = Blueprint('product_rating', __name__)


@bp.route('/product_rating')
def product_rating():
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        ratings = Product_Rating.get_last_5(
            current_user.id)  
    else:
        ratings = None
    return render_template('product_rating.html',
                           products=ratings)  
    # render the page by adding information to the index.html file
    # return render_template('index.html',
    #                        avail_products=products,
    #                        rating_history=ratings)
