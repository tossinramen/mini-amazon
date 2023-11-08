from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
import datetime

from .models.product import Product
from .models.seller_rating import Seller_Rating
from .models.purchase import Purchase
from .models.user import User

from flask import Blueprint
from flask import jsonify
bp = Blueprint('seller_rating', __name__)


@bp.route('/seller_rating')
def seller_rating():
    # get all available products for sale:
    # find the products current user has bought:
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = current_user.id))

    if count > 0:
        s_ratings = Seller_Rating.get_last_5(current_user.id)  
    else:
        s_ratings = None    
    return render_template('seller_rating.html',
                           s_ratings=s_ratings)  
    # render the page by adding information to the index.html file
    # return render_template('index.html',
    #                        avail_products=products,
    #                        rating_history=ratings)


@bp.route('/edit_review_sellers/<int:sid>', methods=['GET', 'POST'])
def edit_review_sellers(sid):
    # get all available products for sale:
    # find the products current user has bought:
    uid = current_user.id
    s_ratings = Seller_Rating.get(uid, sid)    
    return render_template('edit_review_sellers.html',
                           s_ratings=s_ratings) 

# @bp.route('/redirect_to_user_reviews', methods=['POST'])
# def redirect_to_user_reviews():
#     return redirect(url_for('product_rating.product_rating'))

@bp.route('/redirect_to_edit_review_sellers', methods=['GET', 'POST'])
def redirect_to_edit_review_sellers():
    sid = request.args.get('sid')
    return redirect(url_for('seller_rating.edit_review_sellers', sid=sid))

@bp.route('/update_sr', methods=['GET', 'POST'])
def update_data():
    description = request.form.get('description')
    stars = request.form.get('stars')
    uid = current_user.id
    sid = request.form.get('sid')
    update_query = ('''UPDATE Seller_Rating SET description = :description, stars = :stars WHERE sid = :sid and uid = :uid''') 

    app.db.execute(update_query, description = description, stars = stars, sid = sid, uid = uid)
    # Perform the update query using the data provided

    return redirect(url_for('seller_rating.seller_rating'))
