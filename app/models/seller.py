from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login

class User(UserMixin):
    # ... your existing code for the User class ...

class Seller(User):
    def __init__(self, id, email, firstname, lastname, avg_rating):
        super().__init__(id, email, firstname, lastname)
        self.avg_rating = avg_rating

    @staticmethod
    def create_seller(email, password, firstname, lastname, avg_rating):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname)
VALUES(:email, :password, :firstname, :lastname)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname)
            id = rows[0][0]

            # Insert seller-specific data into the Sellers table
            app.db.execute("""
INSERT INTO Sellers(uid, avg_rating)
VALUES(:uid, :avg_rating)
""",
                            uid=id, avg_rating=avg_rating)

            return Seller.get(id)
        except Exception as e:
            # Handle exceptions here
            print(str(e))
            return None

    @staticmethod
    def get_by_id(id):
        rows = app.db.execute("""
SELECT U.id, U.email, U.firstname, U.lastname, S.avg_rating
FROM Users U
JOIN Sellers S ON U.id = S.uid
WHERE U.id = :id
""",
                              id=id)
        return Seller(*rows[0]) if rows else None

    # Add more seller-specific methods as needed

@login.user_loader
def load_user(id):
    # Define a function to load users (both regular users and sellers) based on their ID
    user = User.get(id)
    if user is None:
        user = Seller.get_by_id(id)
    return user
