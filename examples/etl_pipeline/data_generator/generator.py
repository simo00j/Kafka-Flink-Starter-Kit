# data_generator.py

from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime, timedelta
from database import Database

producer = KafkaProducer(
    bootstrap_servers='kafka-broker-1:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_sensor_data():
    while True:
        data = {
            "sensor_id": random.randint(1, 100),
            "co2_emission": round(random.uniform(50.0, 200.0), 2),
            "event_time": time.time()
        }
        producer.send('raw-data', value=data)
        print(f"Produced: {data}")
        time.sleep(1)

def random_date_within_year():
    start_date = datetime(datetime.now().year, 1, 1)
    end_date = datetime(datetime.now().year, 12, 31)
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

def get_connection_params() -> Dict[str, str]:
    return {
        'host': os.getenv('DB_HOST', 'postgres'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'dbname': os.getenv('DB_NAME', 'etl')
    }

if __name__ == "__main__":
    conn_params = get_connection_params()
    db = Database(**conn_params)
    db.setup_database()
    
    sensor_types = ['Type_A', 'Type_B', 'Type_C']
    sample_sensors = [
        (i, f'Location_{i}', random.choice(sensor_types), random_date_within_year().strftime('%Y-%m-%d'))
        for i in range(1, 101)
    ]

    db.insert_sensor_data(sample_sensors)
    generate_sensor_data()
