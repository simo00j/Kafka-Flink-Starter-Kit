import os
import json
import logging
from kafka import KafkaConsumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
def create_consumer(topic, bootstrap_servers, group_id):
    """Create and return a Kafka consumer."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def process_notification_event(notification_event):
    """Process a notification event."""
    user_id = notification_event.get('user_id')
    notification_type = notification_event.get('notification_type')
    event_time = notification_event.get('event_time')

    logger.info(f"Received notification event: {notification_event}")

    # Implement notification logic
    if notification_type == 'email':
        # Placeholder for sending an email
        logger.info(f"Sending email notification to user_id: {user_id}")
    elif notification_type == 'sms':
        # Placeholder for sending an SMS
        logger.info(f"Sending SMS notification to user_id: {user_id}")
    elif notification_type == 'push':
        # Placeholder for sending a push notification
        logger.info(f"Sending push notification to user_id: {user_id}")
    else:
        logger.warning(f"Unknown notification type: {notification_type}")

def main():
    # Load configuration from environment variables
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-broker-1:9092')
    topic = os.getenv('KAFKA_NOTIFICATIONS_TOPIC', 'notifications')
    group_id = os.getenv('NOTIFICATION_SERVICE_GROUP_ID', 'notification-service-group')

    # Create Kafka consumer
    consumer = create_consumer(topic, bootstrap_servers, group_id)

    logger.info(f"Notification Service is running and listening to '{topic}' topic...")

    # Consume messages
    try:
        for message in consumer:
            notification_event = message.value
            process_notification_event(notification_event)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        consumer.close()
        logger.info("Consumer closed.")

if __name__ == '__main__':
    main()
