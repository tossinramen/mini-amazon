from flask import render_template
from flask_login import current_user
import datetime

from .models.seller_inventory import SellerInventory

from flask import Blueprint
bp = Blueprint('seller_inventory', __name__)


@bp.route('/seller_inventory/<int:uid>')
def inventory(uid):

    # if current_user.is_authenticated:
    #     seller_inventory = SellerInventory.get_all_by_uid(
    #         current_user.id)
    # else:
    #     seller_inventory = None
    # render the page by adding information to the inventory.html file
    seller_inventory = SellerInventory.get_all_by_uid(uid)
    return render_template('inventory.html',
                           inventory=seller_inventory)