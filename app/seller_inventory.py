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
    per_page = 10  
    offset = (page - 1) * per_page
    seller_inventory = SellerInventory.get_all_by_uid_with_pagination(uid, per_page, offset)
    total_items = SellerInventory.count_all_by_uid(uid)  
    total_pages = (total_items + per_page - 1) // per_page  
    return render_template('seller_page.html', inventory=seller_inventory,
                           page=page, per_page=per_page, total=total_items,
                           total_pages=total_pages, uid=uid)



@bp.route('/past_seller_orders/<int:uid>')
def past_seller_orders(uid):
    PER_PAGE = 10 
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM BoughtLineItems WHERE sid = :uid', uid=uid)
    # Assuming the first element of the tuple is the 'total_count'.
    total = total_result[0][0] if total_result else 0

    query = """
        SELECT id, sid, pid, qty, price, fulfilled
        FROM BoughtLineItems
        WHERE sid = :uid
        LIMIT :limit OFFSET :offset
    """
    
    seller_orders = app.db.execute(query, uid=uid, limit=PER_PAGE, offset=offset)  
    
    return render_template('seller_orders.html', inventory=seller_orders, total=total,
                           page=page, per_page=PER_PAGE, uid=uid)