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
st.markdown(
    """
    Discover frequent event sequences leading to
    protocol deviations in clinical trial records
    using PrefixSpan sequential pattern mining.
    """
)

tab1, tab2, tab3 = st.tabs(
    [
        "Overview",
        "Pattern Mining",
        "Sequence Explorer"
    ]
)

support = st.sidebar.slider(
    "Minimum Support",
    min_value=50,
    max_value=3000,
    value=100,
    step=10
)

patterns = mine_patterns(sequences, min_support=support)

#Find the patterns that leads to deviation
deviation_patterns = get_deviation_patterns(patterns)
total_deviations = df[df['deviation_flag'] == 1]['patient_id'].nunique()

#Sort the patterns according to their support
deviation_patterns = sort_patterns(deviation_patterns)

#Add support percentage to the data
deviation_patterns = add_support_percentage(deviation_patterns, len(sequences))

table = pd.DataFrame(deviation_patterns, columns=['Support', 'Support Percentage', 'Pattern'])
table["Pattern"] = table["Pattern"].apply(
    lambda x: " → ".join(x)
)
pattern_lengths = [len(pattern) for _,_,pattern in deviation_patterns]
length_df = pd.DataFrame(pattern_lengths, columns=["Lengths"])

with tab1:

    #KPI cards
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
            "Deviation Patterns",
            len(deviation_patterns)
        )

    #Severity Distribution
    severity_counts = (
        df[df["deviation_flag"] == 1]
        ["deviation_severity"]
        .value_counts()
    )
    st.subheader("Severity Distribution Chart")
    st.bar_chart(severity_counts)

    #Site-wise Distribution
    st.subheader("Site-wise Deviation Analysis")
    site_deviation = df[df['deviation_flag'] == 1]["site_id"].value_counts()
    st.bar_chart(site_deviation)

    #Key Insights
    st.subheader("Key Insights")
    top_pattern = deviation_patterns[0]
    st.info(
        f"""Most common deviation pathway: {' → '.join(top_pattern[2])}

        Support: {top_pattern[0]}
        """
    )

with tab2:
    st.write("Current Support: ", support)

    # st.subheader("Pattern Search")
    search = st.text_input("Search Pattern")
    if search:
        table = table[table["Pattern"].str.contains(search, case=False)]

    #Top Patterns Table
    st.subheader("Top Protocol Deviation Patterns")
    st.dataframe(table.head(20), use_container_width=True)

    #Pattern Length Distribution
    st.subheader("Pattern Length Distribution")
    st.bar_chart(length_df["Lengths"].value_counts())

    #Top Risk Events


with tab3:

    st.subheader("Patient Journey Viewer")
    selected_patient = st.selectbox(
        "Select Patient",
        df["patient_id"].unique()
    )

    patient_events = (
        df[df["patient_id"] == selected_patient]
        .sort_values("timestamp")
    )

    for event in patient_events["event"]:
        st.write("➡️", event)