from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from .models.user import User
from markupsafe import Markup




from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/my_purchases', methods=['GET'])
@login_required
def my_purchases():
    return redirect(url_for('users.user_purchases', uid=current_user.get_id())) #redirects to user_purchases.html

@bp.route('/profile') 
@login_required  
def profile():
    return render_template('profile.html', user=current_user)
#route to display the purchases made by a specific user, identified by 'uid'.
#filter by item, seller, and date.
PER_PAGE = 10  #pagination 
@bp.route('/user_purchases/<int:uid>', methods=['GET'])
@login_required
def user_purchases(uid):
    page = request.args.get('page', 1, type=int)
    item = request.args.get('item', type=str)
    seller = request.args.get('seller', type=str)
    date = request.args.get('date', type=str)
    offset = (page - 1) * PER_PAGE #calculating offset

    base_query = '''
    SELECT p.id AS purchase_id, pr.name AS product_name, b.qty, b.price, p.time_purchased, b.fulfilled, u.firstname || ' ' || u.lastname AS seller_name, u.id AS seller_id
    FROM Purchases p
    JOIN BoughtLineItems b ON p.id = b.id
    JOIN Products pr ON b.pid = pr.id
    JOIN Users u ON b.sid = u.id
    WHERE p.uid = :uid
    '''
    filter_clauses = [] # List to hold dynamic filter clauses
    params = {'uid': uid}

    if item:
        filter_clauses.append("pr.name ILIKE :item")
        params['item'] = f"%{item}%" 
    if seller:
        filter_clauses.append("(u.firstname || ' ' || u.lastname) ILIKE :seller")
        params['seller'] = f"%{seller}%"
    if date:
        filter_clauses.append("CAST(p.time_purchased AS DATE) = :date")
        params['date'] = date

    if filter_clauses:
        base_query += ' AND ' + ' AND '.join(filter_clauses)

    base_query += ' ORDER BY p.time_purchased DESC LIMIT :limit OFFSET :offset'
    user_purchases = app.db.execute(base_query, **params, limit=PER_PAGE, offset=offset)

    
    count_query = '''
    SELECT COUNT(*)
    FROM Purchases p
    JOIN BoughtLineItems b ON p.id = b.id
    JOIN Products pr ON b.pid = pr.id
    JOIN Users u ON b.sid = u.id
    WHERE p.uid = :uid
    '''
    if filter_clauses:
        count_query += ' AND ' + ' AND '.join(filter_clauses)
    total_result = app.db.execute(count_query, **params)
    total = total_result[0][0] if total_result else 0

    return render_template('user_purchases.html', user_purchases=user_purchases, total=total, page=page, per_page=PER_PAGE, uid=uid, item=item, seller=seller, date=date)

# redirects to the seller's inventory page
@bp.route('/seller_page')
def redirect_to_seller_inventory():
    return redirect(url_for('seller_inventory.inventory', uid=current_user.get_id()))
# Redirects to the seller's past orders page
@bp.route('/my_past_seller_orders')
def my_past_seller_orders():
    return redirect(url_for('seller_inventory.seller_orders', uid=current_user.get_id()))
#redirects to the user's purchases page based on uid
@bp.route('/redirect_to_user_purchases', methods=['POST'])
def redirect_to_user_purchases():
    user_id = request.form.get('user_id')
    return redirect(url_for('users.user_purchases', uid=user_id))


#route to manage profile
@bp.route('/manage_profile')
@login_required
def manage_profile():
    return render_template('manage_profile.html', user=current_user)

@bp.route('/update_email', methods=['POST'])
@login_required
def update_email():
    new_email = request.form['email']
    #check if the new email already exists in the database
    if User.email_exists(new_email):
        #flash an error message if the email already exists
        flash('Email already exists! Please choose another email.', 'error')
        return redirect(url_for('users.manage_profile'))
    
    #if the email does not exist, proceed with the update
    update_query = 'UPDATE Users SET email = :email WHERE id = :user_id'
    app.db.execute(update_query, email=new_email, user_id=current_user.get_id())
    flash('Your email has been updated successfully!', 'success')
    return redirect(url_for('users.profile'))

#update first and last name separately 
@bp.route('/update_firstname', methods=['POST'])
@login_required
def update_firstname():
    new_firstname = request.form['firstname']
    update_query = 'UPDATE Users SET firstname = :firstname WHERE id = :user_id'
    app.db.execute(update_query, firstname=new_firstname, user_id=current_user.get_id())
   
    return redirect(url_for('users.profile'))
#last name
@bp.route('/update_lastname', methods=['POST'])
@login_required
def update_lastname():
    new_lastname = request.form['lastname']
    update_query = 'UPDATE Users SET lastname = :lastname WHERE id = :user_id'
    app.db.execute(update_query, lastname=new_lastname, user_id=current_user.get_id())
    
    return redirect(url_for('users.profile'))
#update address
@bp.route('/update_address', methods=['POST'])
@login_required
def update_address():
    new_address = request.form['address']
    update_query = 'UPDATE Users SET address = :address WHERE id = :user_id'
    app.db.execute(update_query, address=new_address, user_id=current_user.get_id())
  
    return redirect(url_for('users.profile'))
#go to balance management page
@bp.route('/update_balance', methods=['POST'])
@login_required
def update_balance():
    return render_template('balance_management.html', user=current_user)
#handles deposits
@bp.route('/deposit', methods=['POST'])
@login_required
def deposit():
    #current + deposit amount
    deposit_amount = Decimal(request.form['deposit_amount'])
    current_balance = current_user.balance
    new_balance = current_balance + deposit_amount
    update_query = 'UPDATE Users SET balance = :balance WHERE id = :user_id'
    app.db.execute(update_query, balance=str(new_balance), user_id=current_user.get_id())
 
    return redirect(url_for('users.profile'))
#withdraw money 
@bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    withdraw_amount = Decimal(request.form['withdraw_amount'])
    current_balance = current_user.balance
    #check to make sure cant withdraw more than balance
    if withdraw_amount > current_balance:
    
        return redirect(url_for('users.update_balance'))

    new_balance = current_balance - withdraw_amount
    update_query = 'UPDATE Users SET balance = :balance WHERE id = :user_id'
    app.db.execute(update_query, balance=str(new_balance), user_id=current_user.get_id())
    return redirect(url_for('users.profile'))

#public profile, make diffeerent for seller. seller needs rating info about them.
@bp.route('/user/<int:user_id>', methods=['GET'])
def public_user_profile(user_id):
    user_query = 'SELECT id, firstname, lastname, email FROM Users WHERE id = :user_id'
    user_info_result = app.db.execute(user_query, user_id=user_id)
    user_info = user_info_result[0] if user_info_result else None

    reviews_query = '''
    SELECT pr.name, r.description, r.stars, r.time_reviewed, s.uid AS seller_id, u.firstname || ' ' || u.lastname AS seller_name
    FROM Product_Rating r
    JOIN Products pr ON r.pid = pr.id
    JOIN Seller_Inventory si ON pr.id = si.pid
    JOIN Sellers s ON si.uid = s.uid
    JOIN Users u ON s.uid = u.id
    WHERE r.uid = :user_id
    '''
    user_reviews = app.db.execute(reviews_query, user_id=user_id)

    is_seller_query = 'SELECT COUNT(*) FROM Sellers WHERE uid = :user_id'
    is_seller_result = app.db.execute(is_seller_query, user_id=user_id)
    is_seller = is_seller_result[0][0] > 0 if is_seller_result else False
    
    seller_info = None
    seller_reviews = None
    if is_seller:
        seller_query = '''
        SELECT address, avg_rating, COUNT(sr.sid) as rating_count
        FROM Users
        JOIN Sellers ON Users.id = Sellers.uid
        LEFT JOIN Seller_Rating sr ON Sellers.uid = sr.sid
        WHERE Users.id = :user_id
        GROUP BY Users.id, Sellers.avg_rating, Users.address
        '''
        seller_info_result = app.db.execute(seller_query, user_id=user_id)
        seller_info = seller_info_result[0] if seller_info_result else None
        
        seller_reviews_query = '''
        SELECT u.id AS reviewer_id, u.firstname || ' ' || u.lastname AS reviewer_name, sr.description, sr.stars, sr.time_reviewed
        FROM Seller_Rating sr
        JOIN Users u ON sr.uid = u.id
        WHERE sr.sid = :user_id
        '''
        seller_reviews = app.db.execute(seller_reviews_query, user_id=user_id)

    return render_template('public_user_profile.html', user_info=user_info, user_reviews=user_reviews, seller_info=seller_info, seller_reviews=seller_reviews)
#need for profile link
@bp.context_processor
def context_processor():
    def user_profile_link(user_id, user_name):
        return Markup(f'<a href="{url_for("users.public_user_profile", user_id=user_id)}">{user_name}</a>')
    return dict(user_profile_link=user_profile_link)


#user's spending. make sure to do pagination here. make spending history sortable by category, year, money.
@bp.route('/user_spending/<int:uid>', methods=['GET'])
@login_required
def user_spending(uid):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    user_info_query = 'SELECT firstname, lastname FROM Users WHERE id = :uid'
    user_info_result = app.db.execute(user_info_query, uid=uid)
    if user_info_result:
        firstname, lastname = user_info_result[0]
        user_name = f"{firstname} {lastname}"
    else:
        user_name = "Unknown User"

    spending_query = '''
    SELECT 
        EXTRACT(YEAR FROM p.time_purchased) AS year, 
        pr.category, 
        SUM(b.qty * b.price) AS total_spent
    FROM 
        Purchases p
    JOIN 
        BoughtLineItems b ON p.id = b.id
    JOIN 
        Products pr ON b.pid = pr.id
    WHERE 
        p.uid = :uid
    GROUP BY 
        year, pr.category
    ORDER BY 
        year DESC, pr.category
    LIMIT :limit OFFSET :offset
    '''
    spending_data = app.db.execute(spending_query, uid=uid, limit=per_page, offset=offset)

    count_query = '''
    SELECT COUNT(*)
    FROM (
        SELECT 1
        FROM Purchases p
        JOIN BoughtLineItems b ON p.id = b.id
        JOIN Products pr ON b.pid = pr.id
        WHERE p.uid = :uid
        GROUP BY EXTRACT(YEAR FROM p.time_purchased), pr.category
    ) AS count_subquery
    '''
    total_result = app.db.execute(count_query, uid=uid)
    total = total_result[0][0] if total_result else 0

    return render_template('user_spending.html', 
                           spending_data=spending_data, 
                           user_name=user_name, 
                           uid=uid, 
                           page=page, 
                           per_page=per_page, 
                           total=total)

