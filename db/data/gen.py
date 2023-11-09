from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

num_users = 100
num_products = 2000
num_purchases = 2500
num_product_ratings = 1000
num_seller_ratings = 1000

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


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
            balance = round(fake.pydecimal(left_digits=5, right_digits=2, positive=True), 2)
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
            price = '{:.2f}'.format(fake.pydecimal(min_value=1, max_value=500, right_digits=2))
            available = int(fake.random_element(elements=(1, 0)) == 1)  # Map True to 1 and False to 0
            if available == 1:
                available_pids.append(pid)
            writer.writerow([pid, name, price, available])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


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


def gen_seller_inventory(seller_uids, product_uids, max_products, max_quantity_per_product):
    with open('Seller_Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller Inventory...', end=' ', flush=True)
        for seller_uid in seller_uids:
            num_products = fake.random_int(min=0, max=max_products)
            selected_products = random.sample(product_uids, num_products)

            for product_uid in selected_products:
                quantity = fake.random_int(min=1, max=max_quantity_per_product)
                writer.writerow([seller_uid, product_uid, quantity])

        print(f'{len(seller_uids)} seller inventory records generated')

    return

def gen_purchases(user_ids, num_orders):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        available_pids = [] 
        for pid in range(1, num_orders + 1):
            available_pids.append(pid)
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            time_purchased = fake.date_time()
            uid = random.choice(user_ids)
            writer.writerow([pid, uid, time_purchased])
        print(f'{num_orders} generated')
    return available_pids

def gen_bought_line_items(available_purchases, seller_ids, product_ids, mode):

    with open('BoughtLineItems.csv', mode) as f:
        writer = get_csv_writer(f)
        print('BoughtLineItems...', end=' ', flush=True)

        total_line_items = 0
        generated_combinations = set()

        for purchase_id in available_purchases:
            num_line_items = fake.random_int(1, 10)
            for _ in range(num_line_items):
                while True:
                    sid = random.choice(seller_ids)
                    pid = random.choice(product_ids)
                    combination = (purchase_id, sid, pid)

                    if combination not in generated_combinations:
                        generated_combinations.add(combination)
                        qty = fake.random_int(min=1, max=10)
                        price = '{:.2f}'.format(fake.pydecimal(min_value=10, max_value=100, right_digits=2))
                        fulfilled = fake.boolean()
                        writer.writerow([purchase_id, sid, pid, qty, price, fulfilled])
                        total_line_items += 1
                        break
        print(f'{total_line_items} line items generated')
    return

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

                    if combination not in generated_combinations:
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



available_users = gen_users(num_users)
available_pids = gen_products(num_products)
# gen_purchases(num_purchases, available_pids)
available_seller_ids = gen_sellers(available_users, 0.3) 
gen_seller_inventory(available_seller_ids, available_pids, 100, 10000) 
available_purchase_ids = gen_purchases(available_users, 1000)
gen_bought_line_items(available_purchase_ids, available_seller_ids, available_pids, "w")
available_cids = gen_carts(available_users, 1000)
gen_cart_line_items(available_cids, available_seller_ids, available_pids, "w")
gen_product_ratings(num_product_ratings, available_pids)
gen_seller_ratings(num_seller_ratings, available_pids)
