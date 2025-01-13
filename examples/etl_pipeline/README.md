# Real-Time ETL Pipeline with Apache Flink and Kafka

A scalable real-time ETL (Extract, Transform, Load) pipeline implementation using Apache Flink, Apache Kafka, and PostgreSQL. This example demonstrates stream processing of sensor data with enrichment and aggregation capabilities.

## Architecture Overview

The pipeline consists of the following components:

- **Data Generation**: Simulated sensor data production using Python
- **Message Queue**: Apache Kafka for data streaming
- **Stream Processing**: Apache Flink for real-time data processing
- **Data Storage**: PostgreSQL for storing processed results
- **Monitoring**: Prometheus and Grafana for metrics collection and visualization

### Data Flow

1. Sensor data is generated and published to Kafka topic `raw-data`
2. Flink job enriches raw data with sensor metadata from PostgreSQL
3. Enriched data is published to Kafka topic `processed-data`
4. Second Flink job aggregates processed data by sensor
5. Aggregated results are stored in PostgreSQL

## Prerequisites

- Docker and Docker Compose
- Make (optional, for using Makefile commands)
- At least 4GB of available RAM
- Python 3.10 or higher (for local development)

## Project Structure

```
examples/etl_pipeline/
├── data_generator/
│   ├── generator.py        # Simulated sensor data producer
│   └── database.py        # Database operations for sensor metadata
├── flink_app/
│   ├── business_logic.py  # Stream processing logic
│   ├── database.py        # Database operations for Flink
│   ├── entrypoint.sh      # Flink job submission script
│   ├── main.py            # Flink application entry point
│   └── requirements.txt   # Python dependencies for Flink job
├── libs/                  # Directory for external libraries and dependencies
└── README.md             # This documentation file
```

## Setup and Deployment

1. **Environment Setup**

```bash
# Clone the repository
git clone <repository-url>

# Build Docker images
make build
```

2. **Start Infrastructure**

```bash
# Launch required services (Kafka, Zookeeper, PostgreSQL, Flink)
make infra-up
```

3. **Deploy Pipeline**

```bash
# Start the ETL pipeline
make etl-demo
```

## Monitoring

Access the monitoring interfaces:

- Flink Dashboard: http://localhost:8081
- Grafana: http://localhost:3000 (default credentials: admin/admin)
- Prometheus: http://localhost:9090

## Configuration

Key configuration files:

- `docker-compose.yml`: Service configurations
- `flink-conf.yaml`: Flink cluster settings
- `prometheus.yml`: Monitoring configuration
- `topics.json`: Kafka topic definitions

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| KAFKA_BROKER_ID | Kafka broker identifier | 1 |
| POSTGRES_DB | PostgreSQL database name | etl |
| FLINK_TASKMANAGER_SLOTS | Number of task slots | 6 |

## Database Schema

### Sensors Table
```sql
CREATE TABLE sensors (
    sensor_id INT PRIMARY KEY,
    location VARCHAR(255),
    sensor_type VARCHAR(100),
    calibration_date DATE
);
```

### Processed Data Table
```sql
CREATE TABLE processed_data (
    sensor_id INT PRIMARY KEY,
    total_emission FLOAT,
    average_emission FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
);
```

## Development

### Adding New Sensors

Modify `generator.py` to add new sensor types:

```python
sensor_types = ['Type_A', 'Type_B', 'Type_C', 'Type_D']  # Add new types here
```

### Modifying Stream Processing

The main processing logic is in `business_logic.py`. Key components:

- `DataEnrichment`: Enriches raw sensor data with metadata
- `SumAggregator`: Aggregates emissions data by sensor
- `JsonStringToRowMapFunction`: Converts JSON to Flink Row type

## Troubleshooting

Common issues and solutions:

1. **Kafka Connection Issues**
   - Verify Zookeeper is running: `docker-compose ps zookeeper`
   - Check Kafka logs: `docker-compose logs kafka-broker-1`

2. **Flink Job Failures**
   - Check TaskManager logs: `docker-compose logs taskmanager`
   - Verify enough task slots are available

3. **Database Connection Issues**
   - Ensure PostgreSQL is running: `docker-compose ps postgres`
   - Check database logs: `docker-compose logs postgres`

## Cleanup

```bash
# Stop all services and clean up
make clean
```


## License

[MIT License](LICENSE)