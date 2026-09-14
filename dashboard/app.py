import streamlit as st
import pandas as pd
from pathlib import Path
from collections import Counter
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

#Title of dashboard
st.set_page_config(
    page_title="Protocol Deviation Mining",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Protocol Deviation Sequence Mining Dashboard")
st.caption(
    "Discover frequent event pathways leading to protocol deviations using PrefixSpan sequential pattern mining."
)

#Support Slider
mini_support = st.sidebar.slider(
    "Minimum Support",
    min_value=50,
    max_value=3000,
    value=100,
    step=10
)
patterns = mine_patterns(sequences, min_support=mini_support)


#Tabs to divide dashboard
tab1, tab2, tab3 = st.tabs(
    [
        "Overview",
        "Pattern Mining",
        "Sequence Explorer"
    ]
)


#Find the patterns that leads to deviation
deviation_patterns = get_deviation_patterns(patterns)
total_deviations = df[df['deviation_flag'] == 1]['patient_id'].nunique()


#Sort the patterns according to their support
deviation_patterns = sort_patterns(deviation_patterns)


#Add support percentage to the data
deviation_patterns = add_support_percentage(deviation_patterns, len(sequences))


#Create a table of deviation patterns
table = pd.DataFrame(deviation_patterns, columns=['Support', 'Support Percentage', 'Pattern'])
table["Pattern"] = table["Pattern"].apply(
    lambda x: " → ".join(x)
)


#Lengths of diffrent patterns leading to deviation
pattern_lengths = [len(pattern) for _,_,pattern in deviation_patterns]
length_df = pd.DataFrame(pattern_lengths, columns=["Lengths"])


#Calculating the most occuring events that leads to protocol deviation
event_counter = Counter()
for support, percentage, pattern in deviation_patterns:
    for event in pattern[:-1]:
        event_counter[event] += support
top_events = event_counter.most_common(10)
risk_df = pd.DataFrame(
    top_events,
    columns=["Event", "Score"]
)


with tab1:
    with st.container(border=True):
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
    with st.container(border=True):
        #Key Insights
        st.subheader("Key Insights")
        top_pattern = deviation_patterns[0]
        st.info(

        f"""Most common deviation pathway: {' → '.join(top_pattern[2])}

        Support: {top_pattern[0]}
        """
    )

with tab2:
    st.write("Current Support: ", mini_support)

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
    st.subheader("Top Risk Events")
    st.bar_chart(risk_df.set_index("Event"))

with tab3:

    st.subheader("Patient Journey Viewer")
    selected_patient = st.selectbox(
        "Select Patient",
        df["patient_id"].unique()
    )

    patient_df = df[df["patient_id"] == selected_patient]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Events", len(patient_df))
    with col2:
        st.metric("Deviation", "Yes" if patient_df['deviation_flag'].max() else "No")
    with col3:
        st.metric("Site", patient_df['site_id'].iloc[0])

    patient_events = (patient_df.sort_values("timestamp"))
    for event in patient_events["event"]:
        if event == "Protocol Deviation":
            st.error(event)
        else:
            st.success(event)