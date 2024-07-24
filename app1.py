import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tabula

# Function to extract data from PDF
def extract_data(uploaded_file):
    tables = tabula.read_pdf(uploaded_file, pages="all", multiple_tables=True)
    dfs = []
    if tables:
        for df in tables:
            li = list(df.columns)
            if ("TEST NAME" in li and "VALUE" in li) or ("Test Description" in li and " Value Observed" in li):
                dfs.append(df)
    return pd.concat(dfs) if dfs else None

# Function to plot comparison graphs
def plot_comparison(df1, df2, df3):
    # Merge the three DataFrames on 'TEST NAME'
    merged_df = pd.merge(pd.merge(df1, df2, on='TEST NAME', suffixes=('_1', '_2')), df3, on='TEST NAME')
    merged_df = merged_df.rename(columns={'VALUE': 'VALUE_3', 'UNITS': 'UNITS_3'})

    # Group the data by units
    grouped = merged_df.groupby(merged_df['UNITS_1'].fillna(merged_df['UNITS_2']).fillna(merged_df['UNITS_3']))

    # Plot the graphs
    for unit, group in grouped:
        # Calculate total values for each TEST NAME
        group['TOTAL_1'] = group['VALUE_1'].fillna(0) 
        group['TOTAL_2'] = group['VALUE_2'].fillna(0)
        group['TOTAL_3'] = group['VALUE_3'].fillna(0)

        # Display the table
        st.write(f"Unit: {unit}")
        st.dataframe(group[['TEST NAME', 'TOTAL_1', 'TOTAL_2', 'TOTAL_3']])

        # Check if there's a significant range in values
        if group['TOTAL_1'].max() - group['TOTAL_1'].min() > 100:
            # Split into two subgroups based on median
            median = group['TOTAL_1'].median()
            group1 = group[group['TOTAL_1'] <= median]
            group2 = group[group['TOTAL_1'] > median]

            fig, axes = plt.subplots(1, 2, figsize=(12, 6))
            group1_plot = group1.plot(x='TEST NAME', y=['TOTAL_1', 'TOTAL_2', 'TOTAL_3'], kind='bar', ax=axes[0], title=f"{unit} (Lower Range)")
            group2_plot = group2.plot(x='TEST NAME', y=['TOTAL_1', 'TOTAL_2', 'TOTAL_3'], kind='bar', ax=axes[1], title=f"{unit} (Upper Range)")
            annotate_bars(group1_plot)
            annotate_bars(group2_plot)
        else:
            fig, ax = plt.subplots(figsize=(12, 6))
            group_plot = group.plot(x='TEST NAME', y=['TOTAL_1', 'TOTAL_2', 'TOTAL_3'], kind='bar', title=unit, ax=ax)
            annotate_bars(group_plot)

        plt.ylabel('Total Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

# Function to annotate bars
def annotate_bars(plot):
    for p in plot.patches:
        plot.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                      ha='center', va='center', xytext=(0, 10), textcoords='offset points')

# Streamlit app
st.title("PDF Report Comparison")

# File uploads
uploaded_file1 = st.file_uploader("Upload the first PDF file", type=["pdf"])
uploaded_file2 = st.file_uploader("Upload the second PDF file", type=["pdf"])
uploaded_file3 = st.file_uploader("Upload the third PDF file", type=["pdf"])

if uploaded_file1 and uploaded_file2 and uploaded_file3:
    df1 = extract_data(uploaded_file1)
    df2 = extract_data(uploaded_file2)
    df3 = extract_data(uploaded_file3)

    if df1 is not None and df2 is not None and df3 is not None:
        plot_comparison(df1, df2, df3)
    else:
        st.warning("No tables with 'TEST NAME' and 'VALUE' columns found in one or more PDFs.")
