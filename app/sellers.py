from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User


from flask import Blueprint
bp = Blueprint('sellers', __name__)
from .models.seller_inventory import SellerInventory

# @bp.route('/seller_page')
# def profile():
#     return render_template('profile.html', user=current_user)

@bp.route('/seller_page')
def seller_page():
    return redirect(url_for('seller_inventory.inventory', uid=current_user.get_id()))
