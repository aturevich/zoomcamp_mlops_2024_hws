import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
import mlflow
import mlflow.sklearn
import pickle
import os
import time
import requests

# Function to read dataframe and compute duration
def read_dataframe(filename):
    df = pd.read_parquet(filename)
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    df['PULocationID'] = df['PULocationID'].astype(str)
    df['DOLocationID'] = df['DOLocationID'].astype(str)
    return df

# Wait for MLflow server to be ready
mlflow_uri = 'http://mlflow:5000'
while True:
    try:
        response = requests.get(mlflow_uri)
        if response.status_code == 200:
            break
    except requests.ConnectionError:
        pass
    time.sleep(1)

# Load data for March 2023
df = read_dataframe('./data/yellow_tripdata_2023-03.parquet')

# One-hot encoding
dicts = df[['PULocationID', 'DOLocationID']].to_dict(orient='records')
dv = DictVectorizer()
X = dv.fit_transform(dicts)

# Training a model
y = df['duration'].values
lr = LinearRegression()
lr.fit(X, y)

# Print the model intercept
print(f"Model intercept: {lr.intercept_}")

# Set up MLflow
mlflow.set_tracking_uri(mlflow_uri)
mlflow.set_experiment('nyc-taxi-experiment-hw3')

# Start an MLflow run
with mlflow.start_run():
    # Log the model
    mlflow.sklearn.log_model(lr, "model")

    # Save and log the DictVectorizer as an artifact
    vectorizer_dir = 'artifacts'
    os.makedirs(vectorizer_dir, exist_ok=True)
    vectorizer_path = os.path.join(vectorizer_dir, 'dict_vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(dv, f)
    mlflow.log_artifact(vectorizer_path)

    # Log model parameters
    mlflow.log_param("model_type", "LinearRegression")

    # Log model metrics
    mlflow.log_metric("intercept", lr.intercept_)

print("Model and vectorizer logged to MLflow.")
