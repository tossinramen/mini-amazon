from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
import datetime

from .models.product import Product
from .models.product_rating import Product_Rating
from .models.purchase import Purchase
from .models.user import User

from flask import Blueprint
from flask import jsonify
bp = Blueprint('product_rating', __name__)


@bp.route('/product_rating/<int:uid>', methods=['GET', 'POST'])
def product_rating(uid):
    # get all available products for sale:
    # find the products current user has bought:
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = uid))

    if count > 0:
        ratings = Product_Rating.get_last_5(uid)  
    else:
        ratings = None    
    return render_template('product_rating.html',
                           ratings=ratings)  
    # render the page by adding information to the index.html file
    # return render_template('index.html',
    #                        avail_products=products,
    #                        rating_history=ratings)

@bp.route('/redirect_to_user_reviews', methods=['POST'])
def redirect_to_user_reviews():
    user_id = request.form.get('user_id')
    return redirect(url_for('product_rating.product_rating', uid=user_id))
