from flask import current_app as app


class Product:
    def __init__(self, id, name, price, description, available, category, image_url):
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.available = available
        self.category = category
        self.image_url = image_url

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, description, available, category, image_url
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, price, description, available, category, image_url
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
