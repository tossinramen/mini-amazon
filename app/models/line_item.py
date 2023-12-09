from flask import current_app as app

# LineItem class constructor
class LineItem:
    def __init__(self, id, sid, pid, qty, price, product_name):
        self.id = id
        self.sid = sid
        self.pid = pid
        self.qty = qty
        self.price = price
        self.product_name = product_name

    # get line items by cart id
    @staticmethod
    def get_by_id(id):
        rows = app.db.execute('''
            SELECT li.id as id, li.sid as sid, li.pid as pid, li.qty as qty, li.price as price, p.name as product_name
            FROM CartLineItems as li
            JOIN Products p ON p.id = li.pid
            WHERE li.id = :id
            ORDER BY p.name ASC
            ''', id=id)
        # if no items found
        if not rows:
            return None
        else:
            # create LineItem objects for each row, return as list
            return [LineItem(*row) for row in rows]
