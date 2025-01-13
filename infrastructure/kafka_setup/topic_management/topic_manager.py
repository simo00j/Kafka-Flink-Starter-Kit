import logging
import json
from kafka.admin import KafkaAdminClient, NewTopic
from config import admin_config
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_topics_from_config(config_file='topics.json'):
    """Load topic configurations from a JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config['topics']

def create_topics():
    """Creates Kafka topics using the Admin API."""
    admin_client = KafkaAdminClient(bootstrap_servers=admin_config.bootstrap_servers)

    topics_config = load_topics_from_config()
    topic_list = []

    for topic in topics_config:
        new_topic = NewTopic(
            name=topic['name'],
            num_partitions=topic['num_partitions'],
            replication_factor=topic['replication_factor'],
            topic_configs=topic.get('configs', {})
        )
        topic_list.append(new_topic)

    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        logger.info("Topics created successfully.")
    except Exception as e:
        logger.error(f"An error occurred while creating topics: {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    create_topics()
