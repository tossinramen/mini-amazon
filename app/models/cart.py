from flask import current_app as app
from .line_item import LineItem

# Cart class constructor
class Cart:
    def __init__(self, id, uid):
        self.id = id
        self.uid = uid

    # gets cart based on user id
    @staticmethod
    def get_by_uid(uid):
        # finds cart
        row = app.db.execute('''
            SELECT id, uid
            FROM Carts
            WHERE uid = :uid
            ''', uid=uid)
        # returns cart if found
        if not row:
            return None
        else:  
            return Cart(*(row[0]))

    # gets items from users cart
    @staticmethod
    def get_items_by_uid(uid):
        # get current user's cart
        cart = Cart.get_by_uid(uid)
    
        # if exists, else set to none
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
    
    # clears users cart
    @staticmethod
    def clear_cart(uid):
        # delete line items from cart
        app.db.execute('''
            DELETE FROM CartLineItems
            WHERE id IN (
                SELECT id FROM Carts WHERE uid = :uid
            )''', uid=uid)
        
        # fetch all current cart IDs
        curr_ids =  app.db.execute('''
            SELECT id
            FROM Carts
            ''')
        
        # determine max cart ID
        max_id = 0
        for id in curr_ids:
            max_id = max(id[0], max_id)
        
        # delete the cart itself
        app.db.execute('''
            DELETE FROM Carts
            WHERE id IN (
                SELECT id FROM Carts WHERE uid = :uid
            )''', uid=uid)
        # ignore
        # Cart.create_new_cart(max_id+1,uid)
    
    # create new cart after deletion
    @staticmethod
    def create_new_cart(id, uid):
        # ins new cart into table and return its id
        new_cart_id = app.db.execute('''
            INSERT INTO Carts (id, uid)
            VALUES (:id, :uid)
            RETURNING id
            ''', id=id, uid=uid)
        return new_cart_id

    # get card id for given user id
    @staticmethod
    def get_id_by_uid(uid):
        # cart id for specific user
         row = app.db.execute('''
            SELECT id
            FROM Carts
            WHERE uid = :uid
            ''', uid=uid)
         # return cart id if found
         return row[0][0] if row else None