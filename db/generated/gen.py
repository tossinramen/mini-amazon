from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random
from datetime import datetime, timedelta

num_users = 100
num_products = 2000
num_purchases = 2500
num_product_ratings = 1000
num_seller_ratings = 1000

Faker.seed(0)
fake = Faker()

# api_key = "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"
# client = OpenAI(api_key=api_key)


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

#MAKE SURE BALANCE IS DECIMAL NOT INTEGER
#split name into first and last
#uid, email, password, firstname, lastname, address, balance
def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        available_users = []
        for uid in range(num_users):
            available_users.append(uid)
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = fake.address().replace("\n", ", ")
            balance = 0.00
            writer.writerow([uid, email, password, firstname, lastname, address, balance])
        print(f'{num_users} generated')
    return available_users


def gen_products(num_products):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)

            name = fake.sentence(nb_words=4)[:-1]

            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'

            description = fake.sentence(nb_words=20)[:-1]
            
            # available = 'true'
            # with open('db/generated/Seller_Inventory.csv', 'r') as inventory_file:
            #     reader = csv.reader(inventory_file)
            #     total_quantity = 0
            #     for row in reader:
            #         if int(row[1]) == pid:
            #             total_quantity += int(row[2])
            #     if total_quantity == 0:
            #         available = 'false'
            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)

            category = fake.random_element(elements=('Electronics', 
                                                    'Fashion and Apparel', 
                                                    'Home and Garden', 
                                                    'Books and Media', 
                                                    'Health and Beauty'))

            tag, subtag = gen_product_tags(category)

            image_url = f"https://picsum.photos/200/200/?random={pid}"

            writer.writerow([pid, name, price, description, available, category, tag, subtag, image_url])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

def gen_product_tags(category):
    """
    Given the category of a product, generate a tag and a subtag (i.e. a hierarchy of tags) to add to the product.
    """
    tag_subtag_mapping = {
        'Electronics': {
            'Smartphones': ('iPhone', 'Samsung Galaxy', 'Google Pixel', 'OnePlus'),
            'Laptops': ('MacBook', 'Dell XPS', 'HP Spectre', 'Lenovo ThinkPad'),
            'Headphones': ('Over-ear', 'In-ear', 'Wireless', 'Noise-canceling'),
            'Smartwatches': ('Apple Watch', 'Samsung Galaxy Watch', 'Fitbit', 'Garmin'),
            'Cameras': ('DSLR', 'Mirrorless', 'Point-and-Shoot', 'Action Cameras'),
            'Gaming Consoles': ('PlayStation', 'Xbox', 'Nintendo Switch'),
            'Smart Home': ('Smart Speakers', 'Smart Lights', 'Smart Thermostats', 'Smart Security Cameras')
        },
        'Fashion and Apparel': {
            'Clothing': ('T-Shirts', 'Dresses', 'Jeans', 'Sweaters'),
            'Footwear': ('Sneakers', 'Boots', 'Sandals', 'Heels'),
            'Accessories': ('Hats', 'Scarves', 'Bags', 'Watches')
        },
        'Home and Garden': {
            'Furniture': ('Sofas', 'Chairs', 'Tables', 'Beds'),
            'Decor': ('Lamps', 'Candles', 'Mirrors', 'Wall Art'),
            'Appliances': ('Refrigerators', 'Microwaves', 'Washing Machines', 'Coffee Makers')
        },
        'Books and Media': {
            'Books': ('Fiction', 'Non-fiction', 'Mystery', 'Science Fiction'),
            'Movies': ('Action', 'Comedy', 'Drama', 'Science Fiction'),
            'Music': ('Rock', 'Pop', 'Hip Hop', 'Electronic')
        },
        'Health and Beauty': {
            'Skincare': ('Cleansers', 'Moisturizers', 'Serums', 'Sunscreen'),
            'Makeup': ('Lipstick', 'Eyeshadow', 'Foundation', 'Mascara'),
            'Fitness': ('Yoga Mats', 'Dumbbells', 'Resistance Bands', 'Treadmills')
        }
    }

    tag = fake.random_element(elements=list(tag_subtag_mapping[category].keys()))
    subtag = fake.random_element(elements=tag_subtag_mapping[category][tag])

    return tag, subtag


# def gen_purchases(num_purchases, available_pids):
#     with open('Purchases.csv', 'w') as f:
#         writer = get_csv_writer(f)
#         print('Purchases...', end=' ', flush=True)
#         for id in range(num_purchases):
#             if id % 100 == 0:
#                 print(f'{id}', end=' ', flush=True)
#             uid = fake.random_int(min=0, max=num_users-1)
#             pid = fake.random_element(elements=available_pids)
#             time_purchased = fake.date_time()
#             writer.writerow([id, uid, pid, time_purchased])
#         print(f'{num_purchases} generated')
#     return


def gen_sellers(user_ids, probability):
    available_sellers = []
    with open('Sellers.csv', 'w') as f:
        writer = get_csv_writer(f)
        num_sellers = 0
        print('Sellers...', end=' ', flush=True)

        for uid in user_ids:
            if random.random() < probability:
                available_sellers.append(uid)
                avg_rating = fake.random.uniform(1.0, 5.0)
                writer.writerow([uid, avg_rating])
                num_sellers += 1
                if num_sellers % 10 == 0:
                    print(f'{num_sellers}', end=' ', flush=True)
        print(f'{num_sellers} sellers generated')

    return  available_sellers


def gen_seller_inventory(seller_uids, product_uids, max_quantity_per_product):
    with open('Seller_Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller Inventory...', end=' ', flush=True)
        for product_uid in product_uids:
            num_sellers = fake.random_int(min=1, max=len(seller_uids)//10)
            selected_sellers = random.sample(seller_uids, num_sellers)

            for seller_uid in selected_sellers:
                quantity = fake.random_int(min=1, max=max_quantity_per_product)
                writer.writerow([seller_uid, product_uid, quantity])

        print(f'{len(seller_uids)} seller inventory records generated')

    return

from datetime import datetime, timedelta

def gen_purchases(user_ids, num_orders):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        available_pids = [] 
        for pid in range(1, num_orders + 1):
            
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            time_purchased = fake.date_time_between(start_date='-1y', end_date='now')  # Adjust the date range as needed
            available_pids.append((pid, time_purchased))
            uid = random.choice(user_ids)
            writer.writerow([pid, uid, time_purchased])
        print(f'{num_orders} generated')
    return available_pids

def gen_bought_line_items(available_purchases, seller_ids, product_ids):
    with open('BoughtLineItems.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('BoughtLineItems...', end=' ', flush=True)

        total_line_items = 0
        generated_combinations = set()

        for purchase_id, time_purchased in available_purchases:
            num_line_items = fake.random_int(1, 10)
            order_fulfilled = False
            order_fulfillment_date = None

            # if fulfill_orders:
                # Determine if the order is fulfilled based on its purchase date
            order_fulfilled = (datetime.utcnow() - time_purchased) > timedelta(days=14)

                # if order_fulfilled:
                #     # Generate a random fulfillment date within two weeks
                #     order_fulfillment_date = fake.date_time_between(start_date=purchase_date, end_date=purchase_date + timedelta(days=14))

            for _ in range(num_line_items):
                while True:
                    sid = random.choice(seller_ids)
                    pid = random.choice(product_ids)
                    combination = (purchase_id, sid, pid)

                    # Default purchase_date to a value in case fulfill_orders is False

                    if combination not in generated_combinations:
                        generated_combinations.add(combination)
                        qty = fake.random_int(min=1, max=10)
                        price = '{:.2f}'.format(fake.pydecimal(min_value=10, max_value=100, right_digits=2))

                        # Determine line item fulfillment status and time_fulfilled
                        line_item_fulfilled = True if order_fulfilled else fake.boolean()
                        line_item_fulfillment_date = (
                            # order_fulfillment_date
                            fake.date_time_between(start_date=time_purchased, end_date=time_purchased+timedelta(days=14))
                            if order_fulfilled
                            else fake.date_time_between(start_date=time_purchased, end_date='now')
                        )

                        # Write to CSV
                        writer.writerow([
                            purchase_id, sid, pid, qty, price, line_item_fulfilled, line_item_fulfillment_date
                        ])
                        total_line_items += 1
                        break

        print(f'{total_line_items} line items generated')


def gen_cart_line_items(available_carts, seller_ids, product_ids, mode):

    with open('CartLineItems.csv', mode) as f:
        writer = get_csv_writer(f)
        print('CartLineItems...', end=' ', flush=True)

        total_line_items = 0
        generated_combinations = set()

        for cart_id in available_carts:
            num_line_items = fake.random_int(1, 10)
            for _ in range(num_line_items):
                while True:
                    sid = random.choice(seller_ids)
                    pid = random.choice(product_ids)
                    combination = (cart_id, sid, pid)

                    if combination not in generated_combinations:
                        generated_combinations.add(combination)
                        qty = fake.random_int(min=1, max=10)
                        price = '{:.2f}'.format(fake.pydecimal(min_value=10, max_value=100, right_digits=2))
                        writer.writerow([cart_id, sid, pid, qty, price])
                        total_line_items += 1
                        break
        print(f'{total_line_items} line items generated')
    return

def gen_carts(user_ids, last_purchase_id):
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        available_cids = []
        
        for uid in user_ids:  # Start cart IDs at 1001
            cid = last_purchase_id + uid + 1
            available_cids.append(cid)
            if cid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            writer.writerow([cid, uid])
        
        print(f'{len(user_ids)} generated')
    return available_cids

def gen_product_ratings(num_product_ratings, available_pids):
    with open('Product_Rating.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product_Rating...', end=' ', flush=True)
        generated_combinations = set()

        for id in range(num_product_ratings):
            while True:
                    num = random.randrange(1,5)
                    upvote_num = random.randrange(0, num_users)
                    downvote_num = random.randrange(0, num_users - upvote_num)
                    uid = fake.random_int(min=0, max=num_users-1)
                    pid = fake.random_element(elements=available_pids)
                    combination = (uid, pid)

                    if combination not in generated_combinations:
                        if id % 100 == 0:
                            print(f'{id}', end=' ', flush=True)
                        generated_combinations.add(combination)
                        description = fake.paragraph(nb_sentences=num)
                        upvotes = upvote_num
                        downvotes = downvote_num
                        stars = random.randrange(1,5)
                        time_reviewed = fake.date_time()
                        writer.writerow([uid, pid, description, upvotes, downvotes, stars, time_reviewed])
                        break
        print(f'{num_product_ratings} generated')
    return

def gen_seller_ratings(num_seller_ratings, available_pids):
    with open('Seller_Rating.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller_Rating...', end=' ', flush=True)
        generated_combinations = set()

        for id in range(num_seller_ratings):
            while True:
                    num = random.randrange(1,5)
                    upvote_num = random.randrange(0, num_users)
                    downvote_num = random.randrange(0, num_users - upvote_num)
                    uid = fake.random_int(min=0, max=num_users-1)
                    sid = fake.random_int(min=0, max=num_users-1)
                    combination = (uid, sid)

                    if combination not in generated_combinations and uid != sid:
                        if id % 100 == 0:
                            print(f'{id}', end=' ', flush=True)
                        generated_combinations.add(combination)
                        description = fake.paragraph(nb_sentences=num)
                        upvotes = upvote_num
                        downvotes = downvote_num
                        stars = random.randrange(1,5)
                        time_reviewed = fake.date_time()
                        writer.writerow([uid, sid, description, upvotes, downvotes, stars, time_reviewed])
                        break
        print(f'{num_seller_ratings} generated')
    return


#

available_users = gen_users(num_users)
available_pids = gen_products(num_products)
# gen_purchases(num_purchases, available_pids)
available_seller_ids = gen_sellers(available_users, 0.3) 
gen_seller_inventory(available_seller_ids, available_pids, 1000) 
available_purchase_ids = gen_purchases(available_users, 1000)
gen_bought_line_items(available_purchase_ids, available_seller_ids, available_pids)
available_cids = gen_carts(available_users, 1000)
gen_cart_line_items(available_cids, available_seller_ids, available_pids, "w")
gen_product_ratings(num_product_ratings, available_pids)
gen_seller_ratings(num_seller_ratings, available_pids)
