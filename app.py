import streamlit as st
import pandas as pd

st.title("Busy Buffet Analysis")

# Load all sheets
sheets = ['133', '143', '153', '173', '183']
all_dfs = []

for sheet in sheets:
    df = pd.read_excel("2026-Data-Test1-Final.xlsx", sheet_name=sheet)
    df['day'] = sheet
    all_dfs.append(df)

combined = pd.concat(all_dfs, ignore_index=True)

st.write("Total rows:", len(combined))
st.dataframe(combined.head(10))
