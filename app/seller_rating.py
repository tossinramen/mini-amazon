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
#Base function that helps create the seller rating page that displays all the seller ratings of the current user
@bp.route('/seller_rating')
def seller_rating():
    #Helps make the pagination work and have the right formatting
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM Seller_Rating WHERE uid = :uid', uid=current_user.id)
    total = total_result[0][0] if total_result else 0
    
    #Check that the current user exists, should always be 1
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = current_user.id))

    #Get all of the current user's seller ratings  
    query = '''
    SELECT sr.*, u.id as seller_id, u.firstname as seller_firstname, u.lastname as seller_lastname
    FROM Seller_Rating sr
    JOIN Users u ON sr.sid = u.id
    WHERE sr.uid = :uid
    ORDER BY sr.time_reviewed DESC
    LIMIT :limit OFFSET :offset
    '''
    s_ratings = app.db.execute(query, uid=current_user.id, limit=PER_PAGE, offset=offset)
    #Render the seller_rating page
    return render_template('seller_rating.html',
                           s_ratings=s_ratings, total=total, page=page, per_page=PER_PAGE, uid=current_user.id)

#Simple redirect from the detailed orders page to the seller's public profile
@bp.route('/redirect_to_seller_page', methods=['GET', 'POST'])
def redirect_to_seller_page():
    sid = request.args.get('sid')
    return redirect(url_for('users.public_user_profile', user_id = sid))

#Redirect from anywhere that a seller review is present to the edit function, keeps the sid of the seller
@bp.route('/redirect_to_edit_review_sellers', methods=['GET', 'POST'])
def redirect_to_edit_review_sellers():
    sid = request.args.get('sid')
    referring_page_sellers = request.referrer
    return redirect(url_for('seller_rating.edit_review_sellers', sid=sid, referring_page_sellers=referring_page_sellers))

#The edit review function that uses the html file, edit_review_seller, keeps the sid of the seller and finds the rating of the user on the seller
@bp.route('/edit_review_sellers/<int:sid>', methods=['GET', 'POST'])
def edit_review_sellers(sid):
    # get all available products for sale:
    # find the products current user has bought:
    uid = current_user.id
    referring_page_sellers = request.args.get('referring_page_sellers')
    #Uses the get function of the seller_rating file in the models folder to get the old rating
    s_ratings = Seller_Rating.get(uid, sid)    
    return render_template('edit_review_sellers.html',
                           s_ratings=s_ratings, referring_page_sellers=referring_page_sellers) 

#Uses the updated input to update the review of the user and the seller that was chosen
@bp.route('/update_sr', methods=['GET', 'POST'])
def update_data():
    #Collecting the input from the user to use in the query
    description = request.form.get('description')
    stars = request.form.get('stars')
    uid = current_user.id
    sid = request.form.get('sid')
    image_url = request.form.get('image_url')
    #Holds the page that the user came from for redirection
    referring_page_sellers = request.form.get('referring_page_sellers')
    #Updates the table
    update_query = ('''UPDATE Seller_Rating SET description = :description, stars = :stars, image_url = :image_url WHERE sid = :sid and uid = :uid''') 

    app.db.execute(update_query, description = description, stars = stars, sid = sid, uid = uid, image_url=image_url)
    #Uses the reffering page to determine which page the user came from originally and to go back to that page
    if 'seller_rating' in referring_page_sellers:   
        return redirect(url_for('seller_rating.seller_rating'))
    else:
        return redirect(url_for('users.public_user_profile', user_id = sid))
    
#Simple redirection to the deletion function for seller reviews, keeps the sid of the seller
@bp.route('/redirect_to_delete_review_sellers', methods=['GET', 'POST'])
def redirect_to_delete_review_sellers():
    sid = request.args.get('sid')
    referring_page_sellers = request.referrer
    return redirect(url_for('seller_rating.delete_review_sellers', sid=sid, referring_page_sellers=referring_page_sellers))

#Deletes the review of the current user and the seller that was chosen
@bp.route('/delete_sr/<int:sid>', methods=['GET', 'POST'])
def delete_review_sellers(sid):
    uid = current_user.id
    referring_page_sellers = request.args.get('referring_page_sellers')
    #Query that deletes the correct row from the seller rating table
    delete_query = ('''DELETE FROM Seller_Rating WHERE sid = :sid and uid = :uid''') 
    app.db.execute(delete_query, sid = sid, uid = uid)
    #Uses the reffering page to determine which page the user came from originally and to go back to that page
    if 'seller_rating' in referring_page_sellers:
        return redirect(url_for('seller_rating.seller_rating'))
    else:
        return redirect(url_for('users.public_user_profile', user_id = sid))

#Redirection for the add seller review function, keeping the sid
@bp.route('/redirect_to_add_seller_review', methods=['GET', 'POST'])
def redirect_to_add_seller_review():
    sid = request.args.get('sid')
    return redirect(url_for('seller_rating.add_seller_review', sid=sid))

#Gives the sid to the html file
@bp.route('/add_seller_review/<int:sid>', methods=['GET', 'POST'])
def add_seller_review(sid):
    uid = current_user.id   
    return render_template('add_seller_review.html', sid=sid)

#Adds the new row to the table
@bp.route('/insert_sr', methods=['GET', 'POST'])
def insert_seller_data():
    #Checks the request method
    if request.method == 'POST' or request.method == 'GET':
        #Gathers input from the user, initially from the html file
        description = request.form.get('description')
        stars = request.form.get('stars')
        uid = current_user.id
        sid = request.form.get('sid')
        image_url = request.form.get('image_url')
        try:
            #Validate the input
            if not (1 <= int(stars) <= 5):
                raise ValueError("Stars must be between 1 and 5.")

            if len(description) > MAX_DESCRIPTION_LENGTH:
                raise ValueError(f"Description exceeds the maximum length of {MAX_DESCRIPTION_LENGTH} characters.")
            
            #Query that inserts the new row into the seller rating table
            insert_query = '''
                INSERT INTO Seller_Rating (uid, sid, description, upvotes, downvotes, stars, time_reviewed, image_url)
                VALUES (:uid, :sid, :description, 0, 0, :stars, current_timestamp, :image_url)
            '''
            app.db.execute(insert_query, description = description, stars = stars, sid = sid, uid = uid, image_url=image_url)
            #Redirect back to public user profile of the seller
            return redirect(url_for('users.public_user_profile', user_id = sid))
        #Error Catch
        except (ValueError, Exception) as error:
            print(f"Error: {error}")
    #Catchs mistakes
    return render_template('add_seller_review.html')      

