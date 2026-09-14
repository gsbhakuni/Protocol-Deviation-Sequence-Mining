import streamlit as st
import pandas as pd
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


st.title("Protocol Deviation Sequence Mining Dashboard")


support = st.sidebar.slider(
    "Minimum Support",
    min_value=50,
    max_value=500,
    value=100,
    step=10
)

#Find all the patterns using PrefixSpan
st.write("Current Support: ", support)
patterns = mine_patterns(sequences, min_support=support)

#Find the patterns that leads to deviation
deviation_patterns = get_deviation_patterns(patterns)

total_deviations = df[df['deviation_flag'] == 1]['patient_id'].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Patients",
        len(sequences)
    )

with col2:
    st.metric(
        "Total Events",
        len(df)
    )

with col3:
    st.metric(
        "Deviation Patients",
        total_deviations
    )
with col4:
    st.metric(
        "Patterns Found",
        len(patterns)
    )

#Sort the patterns according to their support
deviation_patterns = sort_patterns(deviation_patterns)

#Add support percentage to the data
deviation_patterns = add_support_percentage(deviation_patterns, len(sequences))

table = pd.DataFrame(deviation_patterns, columns=['Support', 'Support Percentage', 'Pattern'])

table["Pattern"] = table["Pattern"].apply(
    lambda x: " → ".join(x)
)

pattern_lengths = [len(patterns) for _,_,patterns in deviation_patterns]
length_df = pd.DataFrame(pattern_lengths, columns=["Lengths"])

st.subheader("Top Protocol Deviation Patterns")
st.dataframe(table.head(20), use_container_width=True)

severity_counts = (
    df[df["deviation_flag"] == 1]
    ["deviation_severity"]
    .value_counts()
)

st.subheader("Severity Distribution Chart")
st.bar_chart(severity_counts)

st.subheader("Site-wise Deviation Analysis")
site_deviation = df[df['deviation_flag'] == 1]["site_id"].value_counts()
st.bar_chart(site_deviation)

st.subheader("Pattern Length Distribution")
st.bar_chart(length_df["Lengths"].value_counts())