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
            query = '''SELECT li.id as id, li.sid as sid, u.firstname || ' ' || u.lastname as seller_name, li.pid as pid, li.qty as qty, li.price as price, p.name as product_name
            FROM CartLineItems as li 
            JOIN Products p ON p.id = li.pid
            JOIN Users u ON li.sid = u.id
            WHERE li.id = :id
            AND u.id = li.sid
            ORDER BY p.name ASC
            '''
            line_items = app.db.execute(query, id=cart.id)
            # line_items = LineItem.get_by_id(cart.id)
        else:
            line_items = None

        return line_items
    
    @staticmethod
    def clear_cart(uid):
        app.db.execute('''
            DELETE FROM CartLineItems
            WHERE id IN (
                SELECT id FROM Carts WHERE uid = :uid
            )''', uid=uid)
        
        curr_ids =  app.db.execute('''
            SELECT id
            FROM Carts
            ''')
        max_id = 0
        for id in curr_ids:
            max_id = max(id[0], max_id)
        
        
        app.db.execute('''
            DELETE FROM Carts
            WHERE id IN (
                SELECT id FROM Carts WHERE uid = :uid
            )''', uid=uid)
        
        # Cart.create_new_cart(max_id+1,uid)
    
    @staticmethod
    def create_new_cart(id, uid):

        new_cart_id = app.db.execute('''
            INSERT INTO Carts (id, uid)
            VALUES (:id, :uid)
            RETURNING id
            ''', id=id, uid=uid)
        return new_cart_id

    @staticmethod
    def get_id_by_uid(uid):
         row = app.db.execute('''
            SELECT id
            FROM Carts
            WHERE uid = :uid
            ''', uid=uid)
         return row[0][0] if row else None