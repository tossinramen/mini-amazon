from flask import current_app as app
from .product import Product

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
    def get_by_pid(pid):
        rows = app.db.execute('''
SELECT uid, pid, quantity
FROM Seller_Inventory
WHERE pid = :pid
''',
                              pid=pid)
        return SellerInventory(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_with_pagination(uid, limit, offset):
        rows = app.db.execute('''
SELECT uid, pid, quantity
FROM Seller_Inventory
WHERE uid = :uid
LIMIT :limit OFFSET :offset
''',
                              uid=uid, limit=limit, offset=offset)
        return [SellerInventory(*row) for row in rows]

    @staticmethod
    def count_all_by_uid(uid):
        result = app.db.execute('''
SELECT COUNT(*) AS total_count
FROM Seller_Inventory
WHERE uid = :uid
''',
                                uid=uid)
        return result[0][0] if result else 0

    @staticmethod
    def get_by_uid_pid(uid, pid):
        rows = app.db.execute('''
SELECT uid, pid, quantity, name, image_url, price
FROM Seller_Inventory, Products
WHERE uid = :uid
AND products.id = :pid
AND pid = :pid
''',
                              uid=uid, pid=pid)
        return rows
    
    @staticmethod
    def get_pid_by_name(name):
        rows = app.db.execute('''
            SELECT id
            FROM Products
            WHERE name = :name
        ''', name=name)

        return rows[0][0] if rows else None

