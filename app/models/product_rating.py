from flask import current_app as app


class Product_Rating:  
    def __init__(self, uid, pid, product_name, description, upvotes, downvotes, stars, time_reviewed, image_url): 
        self.uid = uid
        self.pid = pid
        self.product_name = product_name
        self.description = description
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.stars = stars
        self.time_reviewed = time_reviewed  
        self.image_url = image_url

    #Gets all of the products reviews, given a current uid
    @staticmethod
    def get_all(uid, limit, offset):
        rows = app.db.execute('''
            SELECT pr.uid as uid, pr.pid as pid, p.name as product_name, pr.description, pr.upvotes, pr.downvotes, pr.stars, pr.time_reviewed, pr.image_url
            FROM Product_Rating pr
            JOIN Products p ON p.id = pr.pid
            WHERE uid = :uid
            ORDER BY time_reviewed DESC
            LIMIT :limit OFFSET :offset
            ''', uid=uid, limit=limit, offset=offset)
        if not rows:
            return None
        else:  
            return [Product_Rating(*row) for row in rows]
    
    #Gets the matching review between the uid and pid given if there is one
    @staticmethod
    def get(uid, pid):
        rows = app.db.execute('''
            SELECT pr.uid as uid, pr.pid as pid, p.name as product_name, pr.description, pr.upvotes, pr.downvotes, pr.stars, pr.time_reviewed, pr.image_url
            FROM Product_Rating pr
            JOIN Products p ON p.id = pr.pid
            WHERE uid = :uid and pid = :pid
            ORDER BY time_reviewed DESC
            ''', uid=uid, pid=pid)
        return [Product_Rating(*row) for row in rows[:5]]
