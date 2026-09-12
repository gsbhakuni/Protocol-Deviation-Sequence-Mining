import pandas as pd

def build_sequences(df):

    sequences = (
        df.groupby("patient_id")["event"]
        .apply(list)
        .tolist()
    )

    return sequences
