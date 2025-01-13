# business_logic.py

import json
import logging
from typing import Dict, Any
import os
import sys
from database import Database
from pyflink.datastream.functions import RuntimeContext, FlatMapFunction, KeyedProcessFunction
from pyflink.common.typeinfo import Types
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Row
from pyflink.datastream import MapFunction
logging.basicConfig(level=logging.INFO)

# Enrichment function for the first job
class DataEnrichment(FlatMapFunction):
    def __init__(self, conn_params: Dict[str, str]):
        self.conn_params = conn_params
        self.db = None
        self.metadata_cache = {}

    def open(self, runtime_context: RuntimeContext):
        self.db = Database(**self.conn_params)

    def flat_map(self, value: str) -> None:
        """Enrich incoming sensor data with metadata"""
        try:
            # Parse incoming JSON
            sensor_data = json.loads(value)
            sensor_id = sensor_data.get("sensor_id")
            
            if not sensor_id:
                logging.warning(f"Missing sensor_id in record: {value}")
                return
                
            # Get metadata from cache or database
            if sensor_id in self.metadata_cache:
                location, sensor_type, calibration_date = self.metadata_cache[sensor_id]
            else:
                result = self.db.get_sensor_metadata(sensor_id)
                if result:
                    location, sensor_type, calibration_date = result
                    # Cache the result
                    self.metadata_cache[sensor_id] = (location, sensor_type, calibration_date)
                else:
                    location, sensor_type, calibration_date = "Unknown", "Unknown", "Unknown"
            
            if calibration_date != 'Unknown':
                calibration_date = calibration_date.strftime('%Y-%m-%d')
            
            # Combine data
            enriched_data = {
                **sensor_data,
                "location": location,
                "sensor_type": sensor_type,
                "calibration_date": calibration_date
            }
            
            # Output enriched record
            yield json.dumps(enriched_data)
            
        except Exception as e:
            logging.error(f"Error processing record {value}: {e}")

# Aggregation function for the second job
class SumAggregator(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        # Initialize state descriptors for sum and count
        self.sum_state = runtime_context.get_state(
            ValueStateDescriptor("sum_state", Types.FLOAT())
        )
        self.count_state = runtime_context.get_state(
            ValueStateDescriptor("count_state", Types.INT())
        )

    def process_element(self, value, ctx):
        data = json.loads(value)
        co2_emission = data.get("co2_emission", 0.0)
        sensor_id = data.get("sensor_id")

        # Update total emission
        total_emission = self.sum_state.value() or 0.0
        total_emission += co2_emission
        self.sum_state.update(total_emission)

        # Update count
        count = self.count_state.value() or 0
        count += 1
        self.count_state.update(count)

        # Calculate average
        average_emission = total_emission / count if count != 0 else 0.0

        # Prepare aggregated data
        aggregated_data = {
            "sensor_id": sensor_id,
            "total_emission": total_emission,
            "average_emission": average_emission
        }
        yield json.dumps(aggregated_data)

# Function to create JDBC sink for PostgreSQL
def create_jdbc_sink(conn_params: Dict[str, str]):
    from pyflink.datastream.connectors.jdbc import JdbcSink, JdbcConnectionOptions, JdbcExecutionOptions

    insert_sql = """
        INSERT INTO processed_data 
            (sensor_id, total_emission, average_emission) 
        VALUES 
            (?, ?, ?)
        ON CONFLICT (sensor_id) DO UPDATE SET
            total_emission = EXCLUDED.total_emission,
            average_emission = EXCLUDED.average_emission
    """
    type_info = Types.ROW([Types.INT(), Types.FLOAT(), Types.FLOAT()])


    def statement_builder(statement, record):
        try:
            data = json.loads(record)
            statement.setInt(1, int(data['sensor_id']))
            statement.setDouble(2, float(data['total_emission']))
            statement.setDouble(3, float(data['average_emission']))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logging.error(f"Error building statement: {e}")
            raise

    jdbc_url = f"jdbc:postgresql://{conn_params['host']}:{conn_params['port']}/{conn_params['database']}"
    
    jdbc_connection_options = JdbcConnectionOptions.JdbcConnectionOptionsBuilder() \
        .with_url(jdbc_url) \
        .with_driver_name("org.postgresql.Driver") \
        .with_user_name(conn_params['user']) \
        .with_password(conn_params['password']) \
        .build()

    jdbc_execution_options = JdbcExecutionOptions.builder() \
        .with_batch_size(500) \
        .with_batch_interval_ms(200) \
        .with_max_retries(3) \
        .build()

    return JdbcSink.sink(
        insert_sql,
        type_info=type_info,
        jdbc_connection_options=jdbc_connection_options,
        jdbc_execution_options=jdbc_execution_options
    )

class JsonStringToRowMapFunction(MapFunction):
    def map(self, value):
        try:
            data = json.loads(value)
            sensor_id = int(data['sensor_id'])
            total_emission = float(data['total_emission'])
            average_emission = float(data['average_emission'])
            return Row(sensor_id, total_emission, average_emission)
        except Exception as e:
            logging.error(f"Error converting JSON to Row: {e} | Value: {value}")
            return None