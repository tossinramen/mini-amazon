from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
from flask_wtf import FlaskForm
import datetime

from .models.product import Product
from .models.product_rating import Product_Rating
from .models.purchase import Purchase
from .models.user import User
from flask import session
from flask import request
from flask import Blueprint
from flask import jsonify

bp = Blueprint('product_rating', __name__)
#Setting lengths for pagination and description
PER_PAGE = 10
MAX_DESCRIPTION_LENGTH = 255

#General function that helps produce the product rating page for the current user
@bp.route('/product_rating')
def product_rating():
    #Creates the offset and pages for pagination
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM Product_Rating WHERE uid = :uid', uid=current_user.id)
    total = total_result[0][0] if total_result else 0

    #Makes sure the user is in the database
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = current_user.id))
    if count > 0:
        #Gets all the product ratings for the current user
        ratings = Product_Rating.get_all(current_user.id, limit=PER_PAGE, offset = offset)  
    else:
        ratings = None    
    #Renders the html file for product rating
    return render_template('product_rating.html',
                           ratings=ratings, total=total, page=page, per_page=PER_PAGE, uid = current_user.id)  


#redirects to edit review page while keeping pid of the product
@bp.route('/redirect_to_edit_review', methods=['GET', 'POST'])
def redirect_to_edit_review():
    pid = request.args.get('pid')
    referring_page = request.referrer
    return redirect(url_for('product_rating.edit_review', pid=pid, referring_page=referring_page))

#Get the current rating to view before updating
@bp.route('/edit_review/<int:pid>', methods=['GET', 'POST'])
def edit_review(pid):
    uid = current_user.id
    referring_page = request.args.get('referring_page')
    ratings = Product_Rating.get(uid, pid)
    return render_template('edit_review.html',
                           ratings=ratings, referring_page=referring_page) 

#updates the review
@bp.route('/update_pr', methods=['GET', 'POST'])
def update_data():
    #Get values for update
    description = request.form.get('description')
    stars = request.form.get('stars')
    uid = current_user.id
    pid = request.form.get('pid')
    referring_page = request.form.get('referring_page')
    image_url = request.form.get('image_url')
    #Query for updating table
    update_query = ('''UPDATE Product_Rating SET description = :description, stars = :stars, image_url=:image_url WHERE pid = :pid and uid = :uid''') 
    app.db.execute(update_query, description = description, stars = stars, pid = pid, uid = uid, image_url=image_url)
    #If the user is coming from the product_rating table, go back after the update, otherwise go to the detailed product page
    if 'product_rating' in referring_page:
        return redirect(url_for('product_rating.product_rating'))
    else:
        return redirect(url_for('products.product_details', pid=pid))

#Redirect for deleting a product review, keeping the pid of the product
@bp.route('/redirect_to_delete_review', methods=['GET', 'POST'])
def redirect_to_delete_review():
    pid = request.args.get('pid')
    referring_page = request.referrer
    return redirect(url_for('product_rating.delete_review', pid=pid, referring_page=referring_page))

#Function that deletes the review given the current uid and pid of the project from the redirect function
@bp.route('/delete_pr/<int:pid>', methods=['GET', 'POST'])
def delete_review(pid):
    uid = current_user.id
    referring_page = request.args.get('referring_page')
    #Query for deleting the row in the database
    delete_query = ('''DELETE FROM Product_Rating WHERE pid = :pid and uid = :uid''') 
    app.db.execute(delete_query, pid = pid, uid = uid)
    #If the user is coming from the product_rating table, go back after the update, otherwise go to the detailed product page
    if 'product_rating' in referring_page:
        return redirect(url_for('product_rating.product_rating'))
    else:
        return redirect(url_for('products.product_details', pid=pid))

#redirect for adding a new review, keeping the pid of the product
@bp.route('/redirect_to_add_review', methods=['GET', 'POST'])
def redirect_to_add_review():
    pid = request.args.get('pid')
    return redirect(url_for('product_rating.add_review', pid=pid))

#Get the current user id to use on the add review page
@bp.route('/add_review/<int:pid>', methods=['GET', 'POST'])
def add_review(pid):
    uid = current_user.id   
    return render_template('add_product_review.html', pid=pid)

#Function to add a review to the table
@bp.route('/insert_pr', methods=['GET', 'POST'])
def insert_data():
    #Making sure the request is valid
    if request.method == 'POST' or request.method == 'GET':
        #Get the input for the new row
        description = request.form.get('description')
        stars = request.form.get('stars')
        uid = current_user.id
        pid = request.form.get('pid')
        image_url = request.form.get('image_url')
        try:
            #Validate the input
            if not (1 <= int(stars) <= 5):
                raise ValueError("Stars must be between 1 and 5.")

            if len(description) > MAX_DESCRIPTION_LENGTH:
                raise ValueError(f"Description exceeds the maximum length of {MAX_DESCRIPTION_LENGTH} characters.")

            #Query to insert into the table with the input from before
            insert_query = '''
                INSERT INTO Product_Rating (uid, pid, description, upvotes, downvotes, stars, time_reviewed, image_url)
                VALUES (:uid, :pid, :description, 0, 0, :stars, current_timestamp, :image_url)
            ''' 
            app.db.execute(insert_query, description=description, stars=stars, pid=pid, uid=uid, image_url=image_url)
            #Redirect back to the detailed product page
            return redirect(url_for('products.product_details', pid = pid))

        except (ValueError, Exception) as error:
            print(f"Error: {error}")

    return render_template('add_review.html')      
