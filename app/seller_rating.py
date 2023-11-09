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
PER_PAGE = 10

@bp.route('/seller_rating')
def seller_rating():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM Seller_Rating WHERE uid = :uid', uid=current_user.id)
    # Assuming the first element of the tuple is the 'total_count'.
    total = total_result[0][0] if total_result else 0
    # get all available products for sale:
    # find the products current user has bought:
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = current_user.id))

    if count > 0:
        s_ratings = Seller_Rating.get_all(current_user.id, limit=PER_PAGE, offset = offset)
    else:
        s_ratings = None    
    return render_template('seller_rating.html',
                           s_ratings=s_ratings, total=total, page=page, per_page=PER_PAGE, uid = current_user.id)  
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
