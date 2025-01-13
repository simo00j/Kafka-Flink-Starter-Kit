#!/bin/bash

cd /opt/flink/code/microservices/flink_app && \
flink run -m jobmanager:8081 -py main.py 
