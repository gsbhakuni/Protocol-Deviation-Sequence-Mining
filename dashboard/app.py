from src.data_preprocessing import load_and_clean_data
from src.sequence_builder import build_sequences

df = load_and_clean_data("data/dataset.csv")

sequences = build_sequences(df)