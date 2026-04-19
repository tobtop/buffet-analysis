import streamlit as st
import pandas as pd

st.title("Busy Buffet Analysis")

df = pd.read_excel("2026-Data-Test1-Final.xlsx", sheet_name="133")
st.dataframe(df)
