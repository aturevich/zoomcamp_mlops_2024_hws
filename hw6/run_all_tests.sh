#!/bin/bash

# Set environment variables
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL="http://localhost:4566"

# Ensure Localstack is running
docker-compose up -d

# Run unit tests
echo "Running unit tests..."
pipenv run pytest tests/test_batch.py

# Run the integration test script
echo "Running integration test..."
python tests/integration_test.py

# Verify the output
output_file="s3://nyc-duration/out/2023-01.parquet"
echo "Listing S3 output files..."
aws --endpoint-url=http://localhost:4566 s3 ls s3://nyc-duration/out/
echo "Downloading output file..."
aws --endpoint-url=http://localhost:4566 s3 cp $output_file ./output.parquet

# Read and display the sum of predicted durations
echo "Calculating sum of predicted durations..."
python - <<EOF
import pandas as pd
df_output = pd.read_parquet('output.parquet')
sum_predicted_durations = df_output['predicted_duration'].sum()
print(f"Sum of predicted durations: {sum_predicted_durations}")
EOF

# Clean up
echo "Cleaning up..."
rm output.parquet

echo "All tests completed."
