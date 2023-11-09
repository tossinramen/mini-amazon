from flask import current_app as app


class Seller_Rating:  
    def __init__(self, uid, sid, seller_firstname, seller_lastname, description, upvotes, downvotes, stars, time_reviewed): 
        self.uid = uid
        self.sid = sid
        self.seller_firstname = seller_firstname
        self.seller_lastname = seller_lastname
        self.description = description
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.stars = stars
        self.time_reviewed = time_reviewed  

    @staticmethod
    def get_all(uid, limit, offset):
        rows = app.db.execute('''
            SELECT sr.uid as uid, sr.sid as sid, s.firstname as seller_firstname, s.lastname as seller_lastname, sr.description, sr.upvotes, sr.downvotes, sr.stars, sr.time_reviewed
            FROM Seller_Rating sr
            JOIN Users s ON s.id = sr.sid
            WHERE uid = :uid
            ORDER BY time_reviewed DESC
            LIMIT :limit OFFSET :offset
            ''', uid=uid)
        if not rows:
            return None
        else:  
            return [Seller_Rating(*row) for row in rows]
    
    @staticmethod
    def get(uid, sid):
        rows = app.db.execute('''
            SELECT sr.uid as uid, sr.sid as sid, s.firstname as seller_firstname, s.lastname as seller_lastname, sr.description, sr.upvotes, sr.downvotes, sr.stars, sr.time_reviewed
            FROM Seller_Rating sr
            JOIN Users s ON s.id = sr.sid
            WHERE uid = :uid and sid = :sid
            ORDER BY time_reviewed DESC
            ''', uid=uid, sid=sid)
        return [Seller_Rating(*row) for row in rows[:5]]
