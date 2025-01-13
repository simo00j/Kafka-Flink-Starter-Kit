# Kafka-Flink Starter Pack

A ready-to-use starter pack for bootstrapping Kafka-Flink stream processing projects. This pack provides a complete infrastructure setup with monitoring and two example implementations showcasing different Flink APIs.

## Getting Started

All commands should be run from the root directory of the project.

```bash
# Clone the repository
git clone <repository-url>
cd kafka-flink-starter

# Build all required containers
make build

# Start the infrastructure
make infra-up
```

## Available Make Commands

```bash
# Infrastructure
make build              # Build all Docker images
make infra-up           # Start Kafka, Zookeeper, PostgreSQL, Flink, and monitoring
make clean             # Stop all services and clean up containers

# Example Applications
make etl-stream         # Start data generator for ETL example
make etl_flink_job      # Submit ETL Flink job
make etl-demo           # Run complete ETL demo (combines above commands)

make microservices-stream    # Start data generator for microservices example
make microservices_flink_job # Submit microservices Flink job
make microservices-demo      # Run complete microservices demo
```

## Example Applications

The starter pack includes two examples showing different approaches to stream processing:

1. **ETL Pipeline** (`examples/etl_pipeline/`)
   - Uses Flink DataStream API
   - Programmatic approach to stream processing
   - Python-based data processing

2. **Microservices** (`examples/microservices/`)
   - Uses Flink Table API/SQL
   - Declarative approach to stream processing
   - SQL-based transformations

## Infrastructure Components

Access points after `make infra-up`:
- Kafka: localhost:9092
- Flink Dashboard: http://localhost:8081
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- PostgreSQL: localhost:5432

## Project Structure
```
.
├── examples/                    # Example implementations
├── infrastructure/             # Shared infrastructure
│   ├── data_generator_containers/
│   ├── flink_containers/
│   ├── grafana/
│   ├── kafka_setup/
│   └── prometheus/
├── docker-compose.yml
└── Makefile
```

## Requirements
- Docker and Docker Compose
- Make
- Minimum 8GB RAM
- 20GB free disk space

## Documentation

- Detailed ETL example: [examples/etl_pipeline/README.md](examples/etl_pipeline/README.md)
- Microservices example: [examples/microservices/README.md](examples/microservices/README.md)

## Quick Start - ETL Example

```bash
# From root directory
make infra-up
make etl-demo
```

## Quick Start - Microservices Example

```bash
# From root directory
make infra-up
make microservices-demo
```

## License

[MIT License](LICENSE)

For detailed documentation about specific components, refer to the README files in their respective directories.