from flask import render_template, redirect, url_for, flash, abort, request, current_app as app
from flask_login import current_user
import datetime
import csv
import random
import hashlib
from .models.seller_inventory import SellerInventory

from .models.cart import Cart
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('carts', __name__)

@bp.route('/cart/<int:uid>')
def cart(uid):
    # user check
    # uid=current_user.get_id
    # cart = Cart.get_by_uid(uid)
    # cart_id = cart.id
    count = len(app.db.execute('''SELECT id FROM Users WHERE id = :uid''', uid = uid))
    if count > 0:
        # get current user's cart
        cart_items = Cart.get_items_by_uid(uid)
    else: # user does not exist
        cart_items = None

    if cart_items is None:
        cart_items = []  # ensure cart items is always an iterable

    # render cart pg with user cart line items
    return render_template('carts.html', cart_items=cart_items, uid=uid)

@bp.route('/redirect_to_user_cart')
def redirect_to_user_cart():
    # get user id from form data and redirect to user cart pg
    user_id = request.form.get('user_id')
    return redirect(url_for('carts.cart', uid=current_user.id))

@bp.route('/update_all_quantities', methods=['GET', 'POST'])
def update_all_quantities():
    print(request.form) # debugging
    for key in request.form:
        if key.startswith('quantity_'):
            # split key to obtain identifiers
            _, id, pid, sid = key.split('_')
            new_quantity = int(request.form[key])  # convert qty to integer

            # query to get max avail qty from seller inv
            max_quantity_result = app.db.execute('''
                SELECT quantity
                FROM Seller_Inventory
                WHERE uid = :sid
                AND pid = :pid
                ''', sid=sid, pid=pid)

            if max_quantity_result:
                max_quantity = max_quantity_result[0][0] # extract integer qty val from res
                # update cart item qty if within limit
                if new_quantity <= max_quantity:
                    app.db.execute('''
                        UPDATE CartLineItems
                        SET qty = :new_quantity
                        WHERE id = :id
                        AND pid = :pid
                        AND sid = :sid
                        ''', new_quantity=new_quantity, id=id, pid=pid, sid=sid, uid=current_user.id)
                else:
                    # error if new qty exceeds avail stock
                    abort(400, "Insufficient inventory for one or more items. Quantities not updated.")
            else:
                # error if item not in seller inv
                abort(400, "Item not found in seller inventory.")
    # back to cart pg after updating qtys
    return redirect(url_for('carts.cart', uid=current_user.id))

# remove an item from cart
@bp.route('/remove_item/<int:id>/<int:pid>/<int:sid>', methods=['GET', 'POST'])
def remove_item(id, pid, sid):
    # delete specified item
    app.db.execute('''
        DELETE FROM CartLineItems
        WHERE id = :id
        AND pid = :pid
        AND sid = :sid
        ''', id=id, pid=pid, sid=sid, uid=current_user.id)
    # redirect to cart pg
    return redirect(url_for('carts.cart', uid=current_user.id))




# route to view orders for a user
PER_PAGE = 10
@bp.route('/orders/<int:uid>')
def orders(uid):
    # redirect to login if not authenticated
    if not current_user.is_authenticated or current_user.id != uid:
        return redirect(url_for('users.login'))
    
    # determine pg number and calc offset for pagination
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE

    # retrieve order items
    raw_order_items = get_orders_by_uid(uid, limit=PER_PAGE, offset=offset)

    # processing to generate unique order num
    order_items = []
    used_end_parts = set() 
    for item in raw_order_items:
        fulfillment_time = item['fulfillment_time']
        #create order names based on purchase id and time
        #sellerid not work - orders can be from multiple sellers.
        if fulfillment_time:
            formatted_time = fulfillment_time.isoformat()
            hash_input = f"{item['purchase_id']}-{formatted_time}".encode()
        else:
            hash_input = f"{item['purchase_id']}".encode()

        hash_object = hashlib.sha256(hash_input)
        base_order_end_part = hash_object.hexdigest()[:10]
        #make sure all unique
        order_end_part = base_order_end_part
        i = 0
        while order_end_part in used_end_parts:
            i += 1
            order_end_part = f"{base_order_end_part}-{i}"

        used_end_parts.add(order_end_part)
        #purchase id + hashed time
        order_number = f"ORDER {item['purchase_id']}-{order_end_part}"
        item['order_number'] = order_number
        order_items.append(item)

    # calc total num of orders for pagination and render orders pg
    total_orders = get_total_orders_count(uid)
    return render_template('orders.html', order_items=order_items, uid=uid, page=page, per_page=PER_PAGE, total=total_orders)

def get_orders_by_uid(uid, limit, offset):
    # fetch order details, aggregation
    sql_query = '''
        SELECT pur.id as purchase_id,
               SUM(bli.price * bli.qty) as total_price,
               BOOL_AND(bli.fulfilled) as all_fulfilled,
               MAX(CASE WHEN bli.fulfilled THEN pur.time_purchased ELSE NULL END) as fulfillment_time
        FROM BoughtLineItems bli
        INNER JOIN Products p ON bli.pid = p.id
        INNER JOIN Purchases pur ON bli.id = pur.id
        WHERE pur.uid = :uid
        GROUP BY pur.id
        ORDER BY pur.time_purchased DESC  -- Added sorting by purchase time in descending order
        LIMIT :limit OFFSET :offset
    '''
    result = app.db.execute(sql_query, uid=uid, limit=limit, offset=offset)
    order_items = []
    for row in result:
        # dict for each order item
        item = {
            'purchase_id': row[0], 
            'total_price': row[1], 
            'fulfilled': row[2],
            'fulfillment_time': row[3]  
        }
        order_items.append(item)
    return order_items


def get_total_orders_count(uid):
    # counts total num distinct orders for a user
    count_query = '''
        SELECT COUNT(DISTINCT pur.id)
        FROM BoughtLineItems bli
        INNER JOIN Purchases pur ON bli.id = pur.id
        WHERE pur.uid = :uid
    '''
    total_result = app.db.execute(count_query, uid=uid)
    # extract count
    total = total_result[0][0] if total_result else 0
    return total

#order details for each order (what purchases are included in the order)
@bp.route('/order_details/<int:uid>/<int:purchase_id>')
def order_details(uid, purchase_id):
    # user auth, match uid
    if not current_user.is_authenticated or current_user.id != uid:
        return redirect(url_for('users.login'))

    # retrieve detailed order info and render
    order_details = get_order_details(purchase_id)
    return render_template('order_details.html', order_details=order_details, order_number=f"ORDER #{purchase_id}")

# need fulfillment type IF fulfilled. 
def get_order_details(purchase_id):
    # details of each product in a specific purchase
    sql_query = '''
        SELECT pr.name, bli.qty, bli.price, u.firstname, u.lastname, bli.fulfilled, bli.time_fulfilled
        FROM BoughtLineItems bli
        INNER JOIN Products pr ON bli.pid = pr.id
        INNER JOIN Users u ON bli.sid = u.id
        INNER JOIN Purchases pur ON bli.id = pur.id
        WHERE pur.id = :purchase_id
    '''
    result = app.db.execute(sql_query, purchase_id=purchase_id)
    order_details = []

    for row in result:
        # dict for products in order
        detail = {
            'product_name': row[0],
            'quantity': row[1],
            'price': row[2],
            'seller_name': f"{row[3]} {row[4]}",
            'fulfilled': row[5],
            'time_fulfilled': row[6] if row[5] else 'Purchase not fulfilled'
        }
        order_details.append(detail)

    return order_details

#cart when submitted goes to purchases and orders, needs to be cleared.
@bp.route('/submit_cart', methods=['POST'])
def submit_cart():
    user_id = current_user.id
    # fetch cart items
    cart_items = Cart.get_items_by_uid(user_id)
    # check curr inventory for each product in cart
    for item in cart_items:
        inventory_query = 'SELECT quantity FROM Seller_Inventory WHERE pid = :pid AND uid = :uid'
        curr_inventory = app.db.execute(inventory_query, pid=item.pid, uid=item.sid)
        new_quantity = curr_inventory[0][0] - item.qty

        # inventory handling
        if new_quantity == 0:
            # no more items left, remove from inv and update product availability
            update_query = ('''DELETE FROM Seller_Inventory WHERE uid = :uid AND pid = :pid''')
            app.db.execute(update_query, uid = item.sid, pid = item.pid)
            if SellerInventory.get_by_pid(item.pid) == None:
                availability_query = ('''UPDATE Products SET available = FALSE WHERE id = :pid''')
                app.db.execute(availability_query, pid=item.pid)
        else:
            # just update inv with new qty
            update_query = ('''UPDATE Seller_Inventory SET quantity = :new_quantity WHERE uid = :uid AND pid = :pid''')
            app.db.execute(update_query, uid = item.sid, new_quantity = new_quantity, pid = item.pid)
    
    # create purchase record
    id = Cart.get_id_by_uid(user_id)
    Purchase.create(id, user_id)

    purchase_id = id

    for item in cart_items:
        # add items to BoughtLineItems
        app.db.execute('''
            INSERT INTO BoughtLineItems(id, sid, pid, qty, price)
            VALUES(:purchase_id, :sid, :pid, :qty, :price)
        ''', purchase_id=purchase_id, sid=item.sid, pid=item.pid, qty=item.qty, price=item.price)

    # clear cart items after moving to purchase, go to purchases pg
    Cart.clear_cart(user_id)
    return redirect(url_for('users.user_purchases', uid=user_id))

@bp.route('/product_details/<int:pid>', methods=['GET', 'POST'])
def product_details(pid):
    # product info from products table
    product_query = '''
    SELECT id, name, price, description, available, category, image_url, \
    (SELECT AVG(stars) FROM product_rating WHERE pid = :pid GROUP BY pid) AS avg_stars
    FROM products
    WHERE id = :pid
    '''
    product_result = app.db.execute(product_query, pid=pid)
    
    # extract and display product details if found
    if product_result:
        name = product_result[0][1]
        price = product_result[0][2]
        description = product_result[0][3]
        available = product_result[0][4]
        category = product_result[0][5]
        image_url = product_result[0][6]
        avg_stars = product_result[0][7]
    
    # list each seller and their current quantities
    seller_query = f'''
    SELECT uid, quantity,
           CONCAT(users.firstname, ' ', users.lastname) AS name
    FROM seller_inventory
    JOIN users ON users.id = seller_inventory.uid
    WHERE pid = {pid}
    '''

    seller_info = app.db.execute(seller_query)

    # render detailed product with fetched info
    return render_template('detailed_product.html', name=name,
                           price=price,
                           description=description,
                           available=available,
                           category=category,
                           image_url=image_url,
                           avg_stars=avg_stars,
                           seller_info=seller_info)

@bp.route('/add_to_wishlist/<int:id>', methods=['POST'])
def add_to_wishlist(id):
    # check if the item is already in the wishlist
    existing_wishlist_item = app.db.execute(
        "SELECT * FROM Wishlist WHERE user_id = :user_id AND product_id = :pid",
        user_id=current_user.id, pid=pid
    )

    if existing_wishlist_item:
        flash("Item is already in the wishlist", "error")
    else:
        # add the item to the wishlist
        app.db.execute(
            "INSERT INTO Wishlist (user_id, product_id) VALUES (:user_id, :pid)",
            user_id=current_user.id, pid=pid
        )
        flash("Item added to wishlist", "success")

    return redirect(url_for('carts.cart', uid=current_user.id))


@bp.route('/view_wishlist/<int:uid>')
def view_wishlist(uid):
    # Retrieve wishlist items for the user
    wishlist_items = app.db.execute(
        "SELECT * FROM Wishlist INNER JOIN Products ON Wishlist.product_id = Products.id WHERE user_id = :uid",
        uid=uid
    )

    return render_template('wishlist.html', wishlist_items=wishlist_items, uid=uid)
