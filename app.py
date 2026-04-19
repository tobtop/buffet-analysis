import streamlit as st
import pandas as pd

st.title("Busy Buffet Analysis")

df = pd.read_excel("2026_Data_Test1_Final_-_Busy_Buffet_Dataset.xlsx", sheet_name="133")
st.dataframe(df)
