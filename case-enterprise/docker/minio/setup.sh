#!/bin/bash
set -e

echo "Waiting for MinIO to be ready..."
until mc alias set local http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD} 2>/dev/null; do
    echo "MinIO not ready yet, retrying in 2 seconds..."
    sleep 2
done

echo "Creating lakehouse bucket..."
mc mb local/lakehouse --ignore-existing

echo "Setting bucket policy to public (for demo)..."
mc anonymous set public local/lakehouse

echo "✅ MinIO setup complete!"
mc ls local/
