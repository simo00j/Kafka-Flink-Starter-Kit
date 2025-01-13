# database.py

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Database:
    def __init__(self, host, port, user, password, database):
        self.conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }

    def get_sensor_metadata(self, sensor_id):
        query = "SELECT location, sensor_type, calibration_date FROM sensors WHERE sensor_id = %s"
        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (sensor_id,))
                    result = cursor.fetchone()
                    return result
        except Exception as e:
            print(f"Error fetching metadata for sensor_id {sensor_id}: {e}")
            return None

