import os
import pandas as pd

def dt(hour, minute, second=0):
    from datetime import datetime
    return datetime(2023, 1, 1, hour, minute, second)

# Create the dataframe as specified
data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
]
columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
df_input = pd.DataFrame(data, columns=columns)

# Set the environment variables
os.environ['S3_ENDPOINT_URL'] = 'http://localhost:4566'
os.environ['INPUT_FILE_PATTERN'] = 's3://nyc-duration/in/{year:04d}-{month:02d}.parquet'
os.environ['OUTPUT_FILE_PATTERN'] = 's3://nyc-duration/out/{year:04d}-{month:02d}.parquet'

# Define storage options for S3
options = {
    'client_kwargs': {
        'endpoint_url': os.getenv('S3_ENDPOINT_URL')
    }
}

# Save the input dataframe to S3
input_file = 's3://nyc-duration/in/2023-01.parquet'
df_input.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)

# Run the batch.py script for January 2023
os.system('python batch.py 2023 1')

# Read the output from S3
output_file = 's3://nyc-duration/out/2023-01.parquet'
df_output = pd.read_parquet(output_file, storage_options=options)

# Calculate the sum of predicted durations
sum_predicted_durations = df_output['predicted_duration'].sum()
print(f"Sum of predicted durations: {sum_predicted_durations}")