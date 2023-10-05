from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.purchase import Purchase

bp = Blueprint('purchase', __name__)

@bp.route('/user/purchases', methods=['GET', 'POST'])
@login_required
def user_purchases():
    purchases = Purchase.get_purchases_by_user(current_user.id)
    return render_template('purchases.html', purchases=purchases)