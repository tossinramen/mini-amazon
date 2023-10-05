from flask import current_app as app


class Product_Rating:  
    def __init__(self, uid, pid, time_reviewed, description, upvotes, downvotes, stars): 
        self.uid = uid
        self.pid = pid
        self.time_reviewed = time_reviewed
        self.description = description
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.stars = stars  

    @staticmethod
    def get_last_5(uid):
        rows = app.db.execute('''
            SELECT *
            FROM Product_Rating
            WHERE uid = :uid
            ORDER BY time_reviewed DESC
            ''', uid=uid)
        if not rows:
            return None
        else:  
            return [Product_Rating(*row) for row in rows[:5]]
