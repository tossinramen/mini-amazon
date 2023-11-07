from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

num_users = 100
num_products = 2000
num_purchases = 2500

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    available_users = []
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            available_users.append(uid)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            writer.writerow([uid, email, password, firstname, lastname])
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
            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)
            writer.writerow([pid, name, price, available])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


def gen_purchases(num_purchases, available_pids):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            time_purchased = fake.date_time()
            writer.writerow([id, uid, pid, time_purchased])
        print(f'{num_purchases} generated')
    return


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


available_users = gen_users(num_users)
available_pids = gen_products(num_products)
gen_purchases(num_purchases, available_pids)
available_seller_ids = gen_sellers(available_users, 0.3) 
gen_seller_inventory(available_seller_ids, available_pids, 100, 10000) 
