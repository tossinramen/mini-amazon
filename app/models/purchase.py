from flask import current_app as app

class Purchase:
    def __init__(self, id, uid, pid, time_purchased):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod  # This line should be indented to be part of the class
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT p.id, p.uid, bli.pid, p.time_purchased
FROM Purchases p
JOIN BoughtLineItems bli ON p.id = bli.id
WHERE p.uid = :uid
AND p.time_purchased >= :since
ORDER BY p.time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]