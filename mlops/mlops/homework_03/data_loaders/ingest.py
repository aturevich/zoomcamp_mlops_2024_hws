import requests
from io import BytesIO
from typing import List

import pandas as pd
import numpy as np

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def ingest_files(**kwargs) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []

    base_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet'

    year = 2023
    months = [3]  # Only March 2023

    for month in months:
        url = base_url.format(year=year, month=month)
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(response.text)

        df = pd.read_parquet(BytesIO(response.content))
        df['tpep_pickup_datetime_cleaned'] = df['tpep_pickup_datetime'].astype(np.int64) // 10**9
        dfs.append(df)

    return pd.concat(dfs)