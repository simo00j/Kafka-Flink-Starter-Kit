import os
import json
import random
import time
from datetime import datetime
from uuid import uuid4
import psycopg2
from psycopg2 import sql, OperationalError
from kafka import KafkaProducer
from faker import Faker

fake = Faker()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('POSTGRES_DB', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
}

# Kafka producer configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-broker-1:9092')

# Number of records to generate
NUM_USER_RECORDS = int(os.getenv('NUM_USER_RECORDS', '100'))
NUM_PRODUCT_RECORDS = int(os.getenv('NUM_PRODUCT_RECORDS', '50'))
NUM_EVENTS = int(os.getenv('NUM_EVENTS', '1000'))

# Function to wait for the database to be ready
def wait_for_db(max_retries=10, delay=5):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            conn.close()
            print("Database is ready!")
            return
        except OperationalError as e:
            print(f"Database not ready yet. Retrying in {delay} seconds...")
            time.sleep(delay)
            retries += 1
    raise Exception("Could not connect to the database after several retries.")

# Function to initialize the database
def init_db():
    conn = psycopg2.connect(**DB_PARAMS)
    curr = conn.cursor()
    # Create users table if it doesn't exist
    curr.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            username VARCHAR(255),
            email VARCHAR(255),
            password VARCHAR(255)
        );
    """)
    # Create products table if it doesn't exist
    curr.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            description TEXT,
            price DECIMAL(10, 2)
        );
    """)
    # Create processed_events table if it doesn't exist
    curr.execute("""
        CREATE TABLE IF NOT EXISTS processed_events (
            event_id VARCHAR(255),
            user_id VARCHAR(255),
            username VARCHAR(255),
            email VARCHAR(255),
            event_type VARCHAR(50),
            action_type VARCHAR(50),
            product_id VARCHAR(255),
            total_amount DECIMAL(10, 2),
            event_time TIMESTAMP
        );
    """)
    conn.commit()
    curr.close()
    conn.close()
    print("Database initialized.")


# Function to check if the database is empty
def is_db_empty():
    conn = psycopg2.connect(**DB_PARAMS)
    curr = conn.cursor()
    curr.execute("SELECT COUNT(*) FROM users;")
    user_count = curr.fetchone()[0]
    curr.execute("SELECT COUNT(*) FROM products;")
    product_count = curr.fetchone()[0]
    curr.close()
    conn.close()
    return user_count == 0 and product_count == 0

# Function to generate and insert user data into PostgreSQL
def gen_user_data(num_user_records: int) -> None:
    conn = psycopg2.connect(**DB_PARAMS)
    curr = conn.cursor()
    for _ in range(num_user_records):
        user_id = str(uuid4())
        username = fake.user_name()
        email = fake.email()
        password = fake.password()
        curr.execute(
            """INSERT INTO users (id, username, email, password) VALUES (%s, %s, %s, %s)""",
            (user_id, username, email, password),
        )
    conn.commit()
    curr.close()
    conn.close()
    print(f"Inserted {num_user_records} user records.")

# Function to generate and insert product data into PostgreSQL
def gen_product_data(num_product_records: int) -> None:
    conn = psycopg2.connect(**DB_PARAMS)
    curr = conn.cursor()
    for _ in range(num_product_records):
        product_id = str(uuid4())
        name = fake.word()
        description = fake.text()
        price = round(random.uniform(10, 500), 2)
        curr.execute(
            """INSERT INTO products (id, name, description, price) VALUES (%s, %s, %s, %s)""",
            (product_id, name, description, price),
        )
    conn.commit()
    curr.close()
    conn.close()
    print(f"Inserted {num_product_records} product records.")

# Function to fetch all user IDs from PostgreSQL
def get_user_ids():
    conn = psycopg2.connect(**DB_PARAMS)
    curr = conn.cursor()
    curr.execute("SELECT id FROM users")
    user_ids = [row[0] for row in curr.fetchall()]
    curr.close()
    conn.close()
    return user_ids

# Function to fetch all product IDs from PostgreSQL
def get_product_ids():
    conn = psycopg2.connect(**DB_PARAMS)
    curr = conn.cursor()
    curr.execute("SELECT id FROM products")
    product_ids = [row[0] for row in curr.fetchall()]
    curr.close()
    conn.close()
    return product_ids

# Function to generate a user event
def generate_user_event(user_id, product_id=None):
    event_id = str(uuid4())
    event_type = random.choice(['action', 'profile_update'])
    event_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    user_event = {
        "event_id": event_id,
        "user_id": user_id,
        "event_type": event_type,
        "event_time": event_time,
    }
    if event_type == 'action':
        action_type = random.choice(['click', 'scroll', 'view', 'like'])
        product_id = product_id or str(uuid4())
        user_agent = fake.user_agent()
        ip_address = fake.ipv4()
        url = fake.url()
        user_event.update({
            "action_type": action_type,
            "product_id": product_id,
            "user_agent": user_agent,
            "ip_address": ip_address,
            "url": url,
        })
    elif event_type == 'profile_update':
        new_email = fake.email()
        new_username = fake.user_name()
        user_event.update({
            "new_email": new_email,
            "new_username": new_username,
        })
    return user_event

# Function to generate a checkout event
def generate_checkout_event(user_id, product_id):
    checkout_id = str(uuid4())
    payment_method = fake.credit_card_provider()
    total_amount = round(random.uniform(20, 1000), 2)
    shipping_address = fake.address()
    billing_address = fake.address()
    event_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    checkout_event = {
        "checkout_id": checkout_id,
        "user_id": user_id,
        "product_id": product_id,
        "payment_method": payment_method,
        "total_amount": total_amount,
        "shipping_address": shipping_address,
        "billing_address": billing_address,
        "event_time": event_time,
    }
    return checkout_event

# Function to generate an update event (product updates)
def generate_update_event(product_id):
    event_id = str(uuid4())
    event_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    new_price = round(random.uniform(10, 500), 2)
    new_description = fake.text()
    update_event = {
        "event_id": event_id,
        "product_id": product_id,
        "new_price": new_price,
        "new_description": new_description,
        "event_time": event_time,
    }
    return update_event

# Function to generate a notification event
def generate_notification_event(user_id, notification_type):
    event_id = str(uuid4())
    event_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    notification_event = {
        "event_id": event_id,
        "user_id": user_id,
        "notification_type": notification_type,
        "event_time": event_time,
    }
    return notification_event

# Function to push events to a Kafka topic
def push_to_kafka(event, topic):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(topic, event)
    producer.flush()
    producer.close()

# Function to generate streaming data
def generate_streaming_data(num_events: int) -> None:
    user_ids = get_user_ids()
    product_ids = get_product_ids()
    for _ in range(num_events):
        user_id = random.choice(user_ids)
        product_id = random.choice(product_ids)
        # Decide which event to generate
        event_type = random.choices(
            ['user_event', 'checkout_event', 'update_event', 'notification_event'],
            weights=[50, 20, 20, 10],
            k=1
        )[0]
        if event_type == 'user_event':
            user_event = generate_user_event(user_id, product_id)
            push_to_kafka(user_event, 'user_events')
        elif event_type == 'checkout_event':
            checkout_event = generate_checkout_event(user_id, product_id)
            push_to_kafka(checkout_event, 'checkout_events')
        elif event_type == 'update_event':
            update_event = generate_update_event(product_id)
            push_to_kafka(update_event, 'updates')
        elif event_type == 'notification_event':
            notification_type = random.choice(['email', 'sms', 'push'])
            notification_event = generate_notification_event(user_id, notification_type)
            push_to_kafka(notification_event, 'notifications')

if __name__ == "__main__":
    # Wait for the database to be ready
    wait_for_db()

    # Initialize the database (create tables if not exist)
    init_db()

    # Check if the database is empty and populate it
    if is_db_empty():
        print("Database is empty. Generating initial data...")
        gen_user_data(NUM_USER_RECORDS)
        gen_product_data(NUM_PRODUCT_RECORDS)
    else:
        print("Database already has data. Skipping initial data generation.")

    # Generate streaming data
    print("Generating streaming data...")
    generate_streaming_data(NUM_EVENTS)
    print("Data generation completed.")
