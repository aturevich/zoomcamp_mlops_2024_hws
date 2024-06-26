import os
import pandas as pd
from datetime import datetime
from batch import prepare_data, get_input_path, get_output_path

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def test_prepare_data():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
    ]
    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)
    
    categorical = ['PULocationID', 'DOLocationID']
    actual_df = prepare_data(df, categorical)
    
    expected_data = [
        {'PULocationID': '-1', 'DOLocationID': '-1', 'duration': 9.0},
        {'PULocationID': '1', 'DOLocationID': '1', 'duration': 8.0}
    ]
    expected_df = pd.DataFrame(expected_data)
    
    pd.testing.assert_frame_equal(actual_df[categorical + ['duration']].reset_index(drop=True), expected_df)

def test_get_input_path():
    os.environ['INPUT_FILE_PATTERN'] = "s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
    input_path = get_input_path(2023, 3)
    assert input_path == "s3://nyc-duration/in/2023-03.parquet"

def test_get_output_path():
    os.environ['OUTPUT_FILE_PATTERN'] = "s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
    output_path = get_output_path(2023, 3)
    assert output_path == "s3://nyc-duration/out/2023-03.parquet"

if __name__ == "__main__":
    import pytest
    pytest.main()