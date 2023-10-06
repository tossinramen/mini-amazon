from flask import current_app as app

class LineItem:
    def __init__(self, liid, pid, cid, qty, product_name):
        self.liid = liid
        self.pid = pid
        self.cid = cid
        self.qty = qty
        self.product_name = product_name

    @staticmethod
    def get_by_cid(cid):
        rows = app.db.execute('''
            SELECT li.liid as liid, li.pid as pid, li.cid as cid, li.qty as qty, p.name as product_name
            FROM LineItems li
            JOIN Products p ON p.id = li.pid
            WHERE cid = :cid
            ORDER BY liid ASC
            ''', cid=cid)
        if not rows:
            return None
        else:  
            return [LineItem(*row) for row in rows]
