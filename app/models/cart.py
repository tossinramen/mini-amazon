from flask import current_app as app
from .line_item import LineItem

class Cart:
    def __init__(self, id, uid):
        self.id = id
        self.uid = uid

    @staticmethod
    def get_by_uid(uid):
        row = app.db.execute('''
            SELECT id, uid
            FROM Carts
            WHERE uid = :uid
            ''', uid=uid)
        if not row:
            return None
        else:  
            return Cart(*(row[0]))

    @staticmethod
    def get_items_by_uid(uid):
        # get current user's cart
        cart = Cart.get_by_uid(uid)
    
        if cart:
            # get line items in the cart
            line_items = LineItem.get_by_id(cart.id)
        else:
            line_items = None

        return line_items
