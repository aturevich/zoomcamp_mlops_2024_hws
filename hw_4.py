import argparse
import pickle
import pandas as pd
import numpy as np
import os

# Define argument parser
def parse_args():
    parser = argparse.ArgumentParser(description='Process trip data and generate predictions.')
    parser.add_argument('--year', type=int, required=True, help='Year of the trip data')
    parser.add_argument('--month', type=int, required=True, help='Month of the trip data')
    return parser.parse_args()

# Function to read data
def read_data(filename, categorical):
    df = pd.read_parquet(filename)
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

# Main function
def main(year, month):
    # Load the model
    with open('/app/model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)
    
    # Define categorical columns
    categorical = ['PULocationID', 'DOLocationID']

    # Construct the URL for the data file
    filename = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    
    # Read the data
    df = read_data(filename, categorical)
    
    # Prepare data for prediction
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)
    
    # Calculate standard deviation and mean of predictions
    sd = np.std(y_pred)
    mean_pred = np.mean(y_pred)
    
    print("Standard Deviation of predictions:", sd)
    print("Mean predicted duration:", mean_pred)
    
    # Create ride_id
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    
    # Create a DataFrame with the predictions
    df_result = pd.DataFrame({
        'ride_id': df['ride_id'],
        'predictions': y_pred
    })
    
    # Define the output file path
    output_file = 'results.parquet'
    
    # Save the DataFrame as a Parquet file
    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )
    
    # Check the size of the output file
    file_size = os.path.getsize(output_file)
    print(f"Size of the output file: {file_size} bytes")

if __name__ == '__main__':
    args = parse_args()
    main(args.year, args.month)