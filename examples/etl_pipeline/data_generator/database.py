import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, host, port, user, password, dbname):
        self.conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': dbname
        }

    def create_database(self):
        """Create the database if it does not exist."""
        # Connect to default 'postgres' database first
        conn_params = self.conn_params.copy()
        conn_params['database'] = 'postgres'
        
        conn = None
        try:
            # Create a connection without using context manager
            conn = psycopg2.connect(**conn_params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Required for CREATE DATABASE
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.conn_params['database'],))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.conn_params['database']}")
                logger.info(f"Database '{self.conn_params['database']}' created successfully.")
            else:
                logger.info(f"Database '{self.conn_params['database']}' already exists.")
                
        except psycopg2.Error as e:
            logger.error(f"Error creating database '{self.conn_params['database']}': {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def create_sensors_table(self):
        """Create the sensors table if it does not exist."""
        create_table_query = """
            CREATE TABLE IF NOT EXISTS sensors (
                sensor_id INT PRIMARY KEY,
                location VARCHAR(255),
                sensor_type VARCHAR(100),
                calibration_date DATE
            );
        """
        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_query)
                    conn.commit()
                    logger.info("Table 'sensors' created or already exists.")
        except psycopg2.Error as e:
            logger.error(f"Error creating table 'sensors': {e}")
            raise

    def create_processed_data_table(self):
        """Create the processed_data table if it does not exist."""
        create_table_query = """
            CREATE TABLE IF NOT EXISTS processed_data (
                sensor_id INT PRIMARY KEY,
                total_emission FLOAT,
                average_emission FLOAT,
                FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
            );
        """
        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_query)
                    conn.commit()
                    logger.info("Table 'processed_data' created or already exists.")
        except psycopg2.Error as e:
            logger.error(f"Error creating table 'processed_data': {e}")
            raise

    def setup_database(self):
        """Set up the database by creating necessary tables."""
        self.create_database()
        self.create_sensors_table()
        self.create_processed_data_table()

    def insert_sensor_data(self, sensor_data):
        """Insert sensor data into the sensors table."""
        insert_query = """
            INSERT INTO sensors (sensor_id, location, sensor_type, calibration_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (sensor_id) DO NOTHING;
        """
        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor() as cursor:
                    cursor.executemany(insert_query, sensor_data)
                    conn.commit()
                    logger.info("Sample data inserted into 'sensors' table.")
        except psycopg2.Error as e:
            logger.error(f"Error inserting data into 'sensors' table: {e}")
            raise