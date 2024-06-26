import pandas as pd

df_output = pd.read_parquet('output.parquet')
sum_predicted_durations = df_output['predicted_duration'].sum()
print(f"Sum of predicted durations: {sum_predicted_durations}")
