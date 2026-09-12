import streamlit as st
from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.data_preprocessing import load_and_clean_data
from src.sequence_builder import build_sequences

df = load_and_clean_data("data/dataset.csv")

sequences = build_sequences(df)

st.title("Clinical Trial Mining")
st.write(df.head(5))
st.write("Patients:", len(sequences))
st.write(sequences[:3])