#!/bin/sh

if [ "$STREAM_DATA_SOURCE" = "etl_pipeline" ]; then
    cd /app/etl_pipeline
    exec python generator.py
elif [ "$STREAM_DATA_SOURCE" = "microservices" ]; then
    cd /app/microservices
    exec python generator.py
else
    echo "Invalid STREAM_DATA_SOURCE value. Please set it to either 'etl_pipeline' or 'microservices'."
    exit 1
fi