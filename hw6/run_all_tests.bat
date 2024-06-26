@echo off

REM Set environment variables
set INPUT_FILE_PATTERN=s3://nyc-duration/in/{year:04d}-{month:02d}.parquet
set OUTPUT_FILE_PATTERN=s3://nyc-duration/out/{year:04d}-{month:02d}.parquet
set S3_ENDPOINT_URL=http://localhost:4566

REM Ensure Localstack is running
docker-compose up -d

REM Run unit tests
echo Running unit tests...
pipenv run pytest tests/test_batch.py

REM Run the integration test script
echo Running integration test...
python tests\integration_test.py

REM Verify the output
set output_file=s3://nyc-duration/out/2023-01.parquet
echo Listing S3 output files...
aws --endpoint-url=http://localhost:4566 s3 ls s3://nyc-duration/out/
echo Downloading output file...
aws --endpoint-url=http://localhost:4566 s3 cp %output_file% .\output.parquet

REM Read and display the sum of predicted durations
echo Calculating sum of predicted durations...
python verify_output.py

REM Clean up
echo Cleaning up...
del output.parquet

echo All tests completed.
