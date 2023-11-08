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
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            writer.writerow([uid, email, password, firstname, lastname])
        print(f'{num_users} generated')
    return


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

def gen_product_ratings(num_product_ratings, available_pids):
    with open('Product_Rating.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product_Rating...', end=' ', flush=True)
        for id in range(num_product_ratings):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            num = random.randrange(1,5)
            upvote_num = random.randrange(0, num_users)
            downvote_num = random.randrange(0, num_users - upvote_num)    
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            description = fake.paragraph(nb_sentences=num)
            upvotes = upvote_num
            downvotes = downvote_num
            stars = random.randrange(1,5)
            time_reviewed = fake.date_time()
            writer.writerow([uid, pid, description, upvotes, downvotes, stars, time_reviewed])
        print(f'{num_product_ratings} generated')
    return

def gen_seller_ratings(num_seller_ratings, available_pids):
    with open('Seller_Rating.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller_Rating...', end=' ', flush=True)
        for id in range(num_seller_ratings):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            num = random.randrange(1,5)
            upvote_num = random.randrange(0, num_users)
            downvote_num = random.randrange(0, num_users - upvote_num)
            uid = fake.random_int(min=0, max=num_users-1)
            sid = fake.random_int(min=0, max=num_users-1)
            while (uid == sid):
                sid = fake.random_int(min=0, max=num_users-1)
            description = fake.paragraph(nb_sentences=num)
            upvotes = upvote_num
            downvotes = downvote_num
            stars = random.randrange(1,5)
            time_reviewed = fake.date_time()
            writer.writerow([uid, sid, description, upvotes, downvotes, stars, time_reviewed])
        print(f'{num_seller_ratings} generated')
    return

gen_users(num_users)
available_pids = gen_products(num_products)
gen_purchases(num_purchases, available_pids)
gen_product_ratings(num_product_ratings, available_pids)
gen_seller_ratings(num_seller_ratings, available_pids)
