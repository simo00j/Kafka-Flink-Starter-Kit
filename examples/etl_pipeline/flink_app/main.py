# main.py

import os
import json
from typing import Dict
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaRecordSerializationSchema
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from business_logic import DataEnrichment, SumAggregator, create_jdbc_sink, JsonStringToRowMapFunction

def get_connection_params() -> Dict[str, str]:
    return {
        'host': os.getenv('DB_HOST', 'postgres'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': os.getenv('DB_NAME', 'etl')
    }

def add_jars_to_env(env: StreamExecutionEnvironment):
    jars = [
        "flink-connector-jdbc-3.0.0-1.16.jar",
        "flink-sql-connector-kafka-1.17.0.jar",
        "postgresql-42.6.0.jar"
    ]
    
    jar_path = "/opt/flink"  # Update this path to where your JARs are located
    env.add_jars(*[f"file://{os.path.join(jar_path, jar)}" for jar in jars])

def main():
    # Set up the streaming execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Add required JARs
    add_jars_to_env(env)
    
    conn_params = get_connection_params()

    # Create Kafka source for raw data
    kafka_source_raw = KafkaSource.builder() \
        .set_bootstrap_servers('kafka-broker-1:9092') \
        .set_topics('raw-data') \
        .set_group_id('flink-enrichment') \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    raw_stream = env.from_source(
        source=kafka_source_raw,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka Source for Enrichment"
    )

    # Enrich the stream data using the DataEnrichment function
    enriched_stream = raw_stream.flat_map(
        DataEnrichment(conn_params), 
        output_type=Types.STRING()
    )

    # Kafka sink for processed-data topic
    kafka_sink_processed = KafkaSink.builder() \
        .set_bootstrap_servers('kafka-broker-1:9092') \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
                .set_topic('processed-data')
                .set_value_serialization_schema(SimpleStringSchema())
                .build()
        ) \
        .build()

    enriched_stream.sink_to(kafka_sink_processed)

    # Kafka source for processed-data topic
    kafka_source_processed = KafkaSource.builder() \
        .set_bootstrap_servers('kafka-broker-1:9092') \
        .set_topics('processed-data') \
        .set_group_id('flink-aggregation') \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    processed_stream = env.from_source(
        source=kafka_source_processed,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka Source for Aggregation"
    )

    def safe_key_by(value):
        try:
            return json.loads(value)['sensor_id']
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON: {e}")
            return -1  # default key for invalid records

    # Aggregate data by sensor_id using key_by and SumAggregator
    aggregated_stream = processed_stream \
        .key_by(safe_key_by, key_type=Types.INT()) \
        .process(SumAggregator(), output_type=Types.STRING())

    
    row_stream = aggregated_stream.map(
    JsonStringToRowMapFunction(),
    output_type=Types.ROW([Types.INT(), Types.FLOAT(), Types.FLOAT()])
    )
    # Sink aggregated data to PostgreSQL
    jdbc_sink = create_jdbc_sink(conn_params)
    row_stream.add_sink(jdbc_sink)

    # Execute the job
    env.execute("ETL Pipeline with DataStream API - Enrichment and Aggregation")

if __name__ == '__main__':
    main()