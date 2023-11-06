from flask import current_app as app


class Product_Rating:  
    def __init__(self, uid, pid, product_name, description, upvotes, downvotes, stars, time_reviewed,): 
        self.uid = uid
        self.pid = pid
        self.product_name = product_name
        self.description = description
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.stars = stars
        self.time_reviewed = time_reviewed  

    @staticmethod
    def get_last_5(uid):
        rows = app.db.execute('''
            SELECT pr.uid as uid, pr.pid as pid, p.name as product_name, pr.description, pr.upvotes, pr.downvotes, pr.stars, pr.time_reviewed
            FROM Product_Rating pr
            JOIN Products p ON p.id = pr.pid
            WHERE uid = :uid
            ORDER BY time_reviewed DESC
            ''', uid=uid)
        if not rows:
            return None
        else:  
            return [Product_Rating(*row) for row in rows[:5]]
    
    @staticmethod
    def get(id):
        rows = app.db.execute("""
            SELECT id, email, firstname, lastname
            FROM Users
            WHERE id = :id
            """, id=id)
        return User(*(rows[0])) if rows else None
