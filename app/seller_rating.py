from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
from flask_wtf import FlaskForm
import datetime

from .models.product import Product
from .models.seller_rating import Seller_Rating
from .models.purchase import Purchase
from .models.user import User

from flask import session
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
bp = Blueprint('seller_rating', __name__)
PER_PAGE = 10
MAX_DESCRIPTION_LENGTH = 255
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

@bp.route('/redirect_to_add_seller_review', methods=['GET', 'POST'])
def redirect_to_add_seller_review():
    sid = request.args.get('sid')
    print(sid)
    return redirect(url_for('seller_rating.add_seller_review', sid=sid))

#Get the current rating to view before updating
@bp.route('/add_seller_review/<int:sid>', methods=['GET', 'POST'])
def add_seller_review(sid):
    uid = current_user.id   
    return render_template('add_seller_review.html', sid=sid)


@bp.route('/insert_sr', methods=['GET', 'POST'])
def insert_seller_data():
    if request.method == 'POST' or request.method == 'GET':
        description = request.form.get('description')
        stars = request.form.get('stars')
        uid = current_user.id
        sid = request.form.get('sid')
        try:
            # Validate input
            if not (1 <= int(stars) <= 5):
                raise ValueError("Stars must be between 1 and 5.")

            if len(description) > MAX_DESCRIPTION_LENGTH:
                raise ValueError(f"Description exceeds the maximum length of {MAX_DESCRIPTION_LENGTH} characters.")
            
            # Insert a new record into the Seller_Rating table
            insert_query = '''
                INSERT INTO Seller_Rating (uid, sid, description, upvotes, downvotes, stars, time_reviewed)
                VALUES (:uid, :sid, :description, 0, 0, :stars, current_timestamp)
            '''
            app.db.execute(insert_query, description = description, stars = stars, sid = sid, uid = uid)
            # Commit the transaction

            return redirect(url_for('users.public_user_profile', user_id = sid))

        except (ValueError, Exception) as error:
            print(f"Error: {error}")

    return render_template('add_seller_review.html')      

