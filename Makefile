# Variables
TASKMANAGER_CONTAINER_NAME=taskmanager
INFRA_SERVICES=kafka-broker-1 zookeeper jobmanager topic-manager taskmanager postgres
DOCKER_COMPOSE=docker compose

.PHONY: build infra-up etl-stream microservices-stream etl_flink_job microservices_flink_job clean etl-demo microservices-demo

build:
	$(DOCKER_COMPOSE) build 

infra-up:
	@echo "Starting infrastructure services..."
	$(DOCKER_COMPOSE) up -d $(INFRA_SERVICES)

etl-stream:
	@echo "Starting ETL stream services..."
	$(DOCKER_COMPOSE) run -d --rm -e STREAM_DATA_SOURCE=etl_pipeline data-generator

microservices-stream:
	@echo "Starting Microservices stream services..."
	$(DOCKER_COMPOSE) run -d --rm -e STREAM_DATA_SOURCE=microservices data-generator

etl_flink_job:
	@echo "Submitting ETL Flink job..."
	docker exec -t $(TASKMANAGER_CONTAINER_NAME) /bin/bash -c "/opt/flink/code/etl_pipeline/flink_app/entrypoint.sh"

microservices_flink_job:
	@echo "Submitting Microservices Flink job..."
	docker exec -t $(TASKMANAGER_CONTAINER_NAME) /bin/bash -c "/opt/flink/code/microservices/flink_app/entrypoint.sh"

etl-demo: infra-up etl-stream etl_flink_job

microservices-demo: infra-up microservices-stream microservices_flink_job

clean:
	@echo "Stopping all services..."
	$(DOCKER_COMPOSE) down -v

.PHONY: infra_up etl-stream microservices-stream etl_flink_job microservices_flink_job clean

