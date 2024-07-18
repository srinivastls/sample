import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tabula
import os

# Ensure JAVA_HOME and PATH are correctly set


def extract_data(uploaded_file):
    tables = tabula.read_pdf(uploaded_file, pages="all", multiple_tables=True)
    dfs = []
    if tables:
        for df in tables:
            li = list(df.columns)
            if "TEST NAME" in li and "VALUE" in li:
                dfs.append(df)
    return pd.concat(dfs) if dfs else None

def plot_comparison(df1, df2):
    # Merge the two DataFrames on 'TEST NAME'
    merged_df = pd.merge(df1, df2, on='TEST NAME', suffixes=('_1', '_2'))

    # Group the data by units
    grouped = merged_df.groupby(merged_df['UNITS_1'].fillna(merged_df['UNITS_2']))

    # Plot the graphs
    for unit, group in grouped:
        # Further split the groups based on value ranges if needed
        # For simplicity, let's split if the range of values is greater than 100
        if group['VALUE_1'].max() - group['VALUE_1'].min() > 100:
            # Split into two subgroups based on median
            median = group['VALUE_1'].median()
            group1 = group[group['VALUE_1'] <= median]
            group2 = group[group['VALUE_1'] > median]

            fig, axes = plt.subplots(1, 2, figsize=(12, 6))
            group1.plot(x='TEST NAME', y=['VALUE_1', 'VALUE_2'], kind='bar', ax=axes[0], title=f"{unit} (Lower Range)")
            group2.plot(x='TEST NAME', y=['VALUE_1', 'VALUE_2'], kind='bar', ax=axes[1], title=f"{unit} (Upper Range)")
        else:
            fig, ax = plt.subplots(figsize=(12, 6))
            group.plot(x='TEST NAME', y=['VALUE_1', 'VALUE_2'], kind='bar', title=unit, ax=ax)

        plt.ylabel('Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

# Streamlit app
st.title("PDF Report Comparison")

# File upload
uploaded_file1 = st.file_uploader("Upload the first PDF file", type=["pdf"])
uploaded_file2 = st.file_uploader("Upload the second PDF file", type=["pdf"])

if uploaded_file1 and uploaded_file2:
    df1 = extract_data(uploaded_file1)
    df2 = extract_data(uploaded_file2)

    if df1 is not None and df2 is not None:
        plot_comparison(df1, df2)
    else:
        st.warning("No tables with 'TEST NAME' and 'VALUE' columns found in one or both PDFs.")
