from flask import current_app as app

class SellerInventory:
    def __init__(self, seller_id, product_id, quantity):
        self.uid = seller_id
        self.pid = product_id
        self.quantity = quantity

    @staticmethod
    def get(uid):
        rows = app.db.execute('''
SELECT uid, pid, quantity
FROM Seller_Inventory
WHERE uid = :uid
''',
                              uid=uid)
        return SellerInventory(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT uid, pid, quantity
FROM Seller_Inventory
WHERE uid = :uid
''',
                              uid=uid)
        return [SellerInventory(*row) for row in rows]
