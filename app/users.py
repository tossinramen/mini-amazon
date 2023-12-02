from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from .models.user import User





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
    return redirect(url_for('users.user_purchases', uid=current_user.get_id()))

@bp.route('/profile')
@login_required  
def profile():
    return render_template('profile.html', user=current_user)

PER_PAGE = 10  

@bp.route('/user_purchases/<int:uid>', methods=['GET'])
@login_required
def user_purchases(uid):
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM Purchases WHERE uid = :uid', uid=uid)
    # Assuming the first element of the tuple is the 'total_count'.
    total = total_result[0][0] if total_result else 0

    query = '''
    SELECT p.id AS purchase_id, pr.name AS product_name, b.qty, b.price, p.time_purchased, b.fulfilled
    FROM Purchases p
    JOIN BoughtLineItems b ON p.id = b.id
    JOIN Products pr ON b.pid = pr.id
    WHERE p.uid = :uid
    ORDER BY p.time_purchased DESC
    LIMIT :limit OFFSET :offset
    '''
    user_purchases = app.db.execute(query, uid=uid, limit=PER_PAGE, offset=offset)

    return render_template('user_purchases.html', user_purchases=user_purchases, total=total, page=page, per_page=PER_PAGE, uid=uid)

@bp.route('/seller_page')
def redirect_to_seller_inventory():
    return redirect(url_for('seller_inventory.inventory', uid=current_user.get_id()))

@bp.route('/my_past_seller_orders')
def my_past_seller_orders():
    return redirect(url_for('seller_inventory.past_seller_orders', uid=current_user.get_id()))

@bp.route('/redirect_to_user_purchases', methods=['POST'])
def redirect_to_user_purchases():
    user_id = request.form.get('user_id')
    return redirect(url_for('users.user_purchases', uid=user_id))



@bp.route('/manage_profile')
@login_required
def manage_profile():
    return render_template('manage_profile.html', user=current_user)

@bp.route('/update_email', methods=['POST'])
@login_required
def update_email():
    new_email = request.form['email']
    update_query = 'UPDATE Users SET email = :email WHERE id = :user_id'
    app.db.execute(update_query, email=new_email, user_id=current_user.get_id())
    flash('Email updated successfully.')
    return redirect(url_for('users.profile'))


@bp.route('/update_firstname', methods=['POST'])
@login_required
def update_firstname():
    new_firstname = request.form['firstname']
    update_query = 'UPDATE Users SET firstname = :firstname WHERE id = :user_id'
    app.db.execute(update_query, firstname=new_firstname, user_id=current_user.get_id())
   
    return redirect(url_for('users.profile'))

@bp.route('/update_lastname', methods=['POST'])
@login_required
def update_lastname():
    new_lastname = request.form['lastname']
    update_query = 'UPDATE Users SET lastname = :lastname WHERE id = :user_id'
    app.db.execute(update_query, lastname=new_lastname, user_id=current_user.get_id())
    
    return redirect(url_for('users.profile'))

@bp.route('/update_address', methods=['POST'])
@login_required
def update_address():
    new_address = request.form['address']
    update_query = 'UPDATE Users SET address = :address WHERE id = :user_id'
    app.db.execute(update_query, address=new_address, user_id=current_user.get_id())
  
    return redirect(url_for('users.profile'))

@bp.route('/update_balance', methods=['POST'])
@login_required
def update_balance():
    return render_template('balance_management.html', user=current_user)

@bp.route('/deposit', methods=['POST'])
@login_required
def deposit():
    deposit_amount = Decimal(request.form['deposit_amount'])
    current_balance = current_user.balance
    new_balance = current_balance + deposit_amount
    update_query = 'UPDATE Users SET balance = :balance WHERE id = :user_id'
    app.db.execute(update_query, balance=str(new_balance), user_id=current_user.get_id())
 
    return redirect(url_for('users.profile'))

@bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    withdraw_amount = Decimal(request.form['withdraw_amount'])
    current_balance = current_user.balance
    if withdraw_amount > current_balance:
    
        return redirect(url_for('users.update_balance'))

    new_balance = current_balance - withdraw_amount
    update_query = 'UPDATE Users SET balance = :balance WHERE id = :user_id'
    app.db.execute(update_query, balance=str(new_balance), user_id=current_user.get_id())
    return redirect(url_for('users.profile'))