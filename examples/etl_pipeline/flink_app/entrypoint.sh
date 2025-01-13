#!/bin/bash

cd /opt/flink/code/etl_pipeline/flink_app && \
flink run -m jobmanager:8081 -py main.py --pyFiles business_logic.py,database.py
