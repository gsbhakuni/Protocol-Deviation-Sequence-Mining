import pandas as pd

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values(
        by=["patient_id", "timestamp"]
    )

    df = df.reset_index(drop=True)

    return df
