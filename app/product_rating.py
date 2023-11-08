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


# @bp.route('/product_rating/<int:uid>', methods=['GET', 'POST'])
@bp.route('/product_rating')
def product_rating():
    # get all available products for sale:
    # find the products current user has bought:
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = current_user.id))

    if count > 0:
        ratings = Product_Rating.get_last_5(current_user.id)  
    else:
        ratings = None    
    return render_template('product_rating.html',
                           ratings=ratings)  
    # render the page by adding information to the index.html file
    # return render_template('index.html',
    #                        avail_products=products,
    #                        rating_history=ratings)


@bp.route('/edit_review/<int:pid>', methods=['GET', 'POST'])
def edit_review(pid):
    # get all available products for sale:
    # find the products current user has bought:
    uid = current_user.id
    ratings = Product_Rating.get(uid, pid)    
    return render_template('edit_review.html',
                           ratings=ratings) 

# @bp.route('/redirect_to_user_reviews', methods=['POST'])
# def redirect_to_user_reviews():
#     return redirect(url_for('product_rating.product_rating'))

@bp.route('/redirect_to_edit_review', methods=['GET', 'POST'])
def redirect_to_edit_review():
    pid = request.args.get('pid')
    return redirect(url_for('product_rating.edit_review', pid=pid))

@bp.route('/update_pr', methods=['GET', 'POST'])
def update_data():
    description = request.form.get('description')
    stars = request.form.get('stars')
    uid = current_user.id
    pid = request.form.get('pid')
    update_query = ('''UPDATE Product_Rating SET description = :description, stars = :stars WHERE pid = :pid and uid = :uid''') 

    app.db.execute(update_query, description = description, stars = stars, pid = pid, uid = uid)
    # Perform the update query using the data provided

    return redirect(url_for('product_rating.product_rating'))
