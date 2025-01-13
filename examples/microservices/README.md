# Event-Driven Microservices with Apache Flink SQL

An event-driven microservices architecture showcasing real-time data processing using Apache Flink SQL, Apache Kafka, and auxiliary services. This example demonstrates stream processing of user events, checkouts, and product updates with a declarative SQL approach.

## Architecture Overview

The system consists of several interconnected components:

- **Event Processing**: Apache Flink SQL for real-time event processing
- **Message Queue**: Apache Kafka for event streaming
- **Data Storage**: PostgreSQL for persistent storage
- **Support Services**: 
  - Email Service for notification handling
  - User Service for profile management

### Event Flow

1. Event sources generate various events (user activities, checkouts, updates)
2. Flink SQL processes events using declarative transformations
3. Processed events are routed to appropriate sinks (Kafka/PostgreSQL)
4. Auxiliary services react to relevant events

## Project Structure

```
examples/microservices/
├── data_generator/              # Test data generation
│   ├── generator.py            # Event generator
│   └── requirements.txt        # Generator dependencies
├── flink_app/                  # Flink SQL application
│   ├── configs.py             # Configuration management
│   ├── entrypoint.sh          # Application entry point
│   ├── main.py                # Main Flink SQL application
│   ├── process/               # Processing SQL statements
│   │   ├── process_events_kafka.sql
│   │   ├── process_events_postgres.sql
│   │   └── update_products.sql
│   ├── sink/                  # Sink SQL statements
│   │   ├── print_updates.sql
│   │   ├── processed_events_kafka.sql
│   │   ├── processed_events_postgres.sql
│   │   └── products.sql
│   └── source/                # Source SQL statements
│       ├── checkout_events.sql
│       ├── updates.sql
│       ├── user_events.sql
│       └── user_profiles.sql
└── services/                  # Auxiliary services
    ├── email_service/         # Email notification service
    │   ├── app.py
    │   ├── Dockerfile
    │   └── requirements.txt
    └── user_service/          # User profile service
        ├── app.py
        ├── Dockerfile
        └── requirements.txt
```

## SQL Processing Pipeline

### Sources

- **user_events.sql**: Captures user interaction events
- **checkout_events.sql**: Processes purchase transactions
- **updates.sql**: Handles product/inventory updates
- **user_profiles.sql**: Manages user profile data

### Processing

- **process_events_kafka.sql**: Real-time event processing logic
- **process_events_postgres.sql**: Event persistence transformations
- **update_products.sql**: Product catalog update logic

### Sinks

- **processed_events_kafka.sql**: Routes processed events to Kafka
- **processed_events_postgres.sql**: Stores processed events in PostgreSQL
- **products.sql**: Updates product inventory
- **print_updates.sql**: Debugging sink for monitoring

## Auxiliary Services

### Email Service

A notification service that:
- Listens for relevant events on Kafka topics
- Sends transactional emails based on event types
- Handles email templating and delivery

### User Service

A profile management service that:
- Maintains user profile information
- Provides user data for event enrichment
- Handles profile updates and preferences

## Setup and Deployment

1. **Environment Setup**

```bash
# Build all services
make build

# Start infrastructure
make infra-up
```

2. **Start Services**

```bash
# Launch microservices demo
make microservices-demo
```

## Configuration

Key configuration points:

- **Flink SQL**: SQL statements in respective directories (source, process, sink)
- **Service Configuration**: Environment variables in docker-compose.yml
- **Event Schemas**: Defined in process SQL files

### Event Types

1. **User Events**
```sql
CREATE TABLE user_events (
    user_id STRING,
    event_type STRING,
    timestamp TIMESTAMP,
    metadata MAP<STRING, STRING>
)
```

2. **Checkout Events**
```sql
CREATE TABLE checkout_events (
    order_id STRING,
    user_id STRING,
    total_amount DECIMAL,
    items ARRAY<ROW<item_id STRING, quantity INT>>
)
```

## Development

### Adding New Event Types

1. Create source SQL definition in `source/`
2. Add processing logic in `process/`
3. Define sink configuration in `sink/`
4. Update `main.py` to include new SQL statements

### Extending Services

1. Create new service directory under `services/`
2. Implement service logic
3. Add Dockerfile and requirements.txt
4. Update docker-compose.yml

## Monitoring and Debugging

- Use `print_updates.sql` sink for debugging
- Monitor Flink SQL operations via Flink Dashboard
- Check service logs using docker-compose logs

## Troubleshooting

Common issues and solutions:

1. **Event Processing Delays**
   - Check Kafka consumer lag
   - Verify Flink parallelism settings
   - Monitor backpressure metrics

2. **Service Communication Issues**
   - Verify Kafka connectivity
   - Check service health endpoints
   - Review network configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add/modify SQL statements or services
4. Test thoroughly
5. Submit a Pull Request

## License

[MIT License](LICENSE)