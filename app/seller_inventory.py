from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from .models.user import User
from .models.seller_inventory import SellerInventory

from flask import Blueprint
bp = Blueprint('seller_inventory', __name__)


@bp.route('/seller_page/<int:uid>')
def inventory(uid):
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page
    offset = (page - 1) * per_page

    # Retrieve the seller's inventory with pagination
    seller_inventory = SellerInventory.get_all_by_uid(uid)
    total_items = len(seller_inventory)

    return render_template('seller_page.html', inventory=seller_inventory, page=page, per_page=per_page, total=total_items, uid=uid)

@bp.route('/past_seller_orders')
def past_seller_orders():
    return redirect(url_for('users.past_seller_orders', uid=current_user.get_id()))