import streamlit as st
from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.data_preprocessing import load_and_clean_data
from src.sequence_builder import build_sequences
from src.prefixspan_mining import mine_patterns
from src.pattern_analysis import (get_deviation_patterns , add_support_percentage, sort_patterns)

#Load the dataset
df = load_and_clean_data("data/dataset.csv")

#Retrieve all the sequences from the dataset
sequences = build_sequences(df)

#Find all the patterns using PrefixSpan
patterns = mine_patterns(sequences)

#Find the patterns that leads to deviation
deviation_patterns = get_deviation_patterns(patterns)

#Sort the patterns according to their support
deviation_patterns = sort_patterns(deviation_patterns)

#Add support percentage to the data
deviation_patterns = add_support_percentage(deviation_patterns, len(sequences))

st.title("Clinical Trial Mining")
st.write(df.head(5))
st.write("Patients:", len(sequences))
st.write(sequences[:3])