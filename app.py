import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.title("Busy Buffet Analysis — Task 1")

# ── Load Data ──────────────────────────────────────
sheets = ['133', '143', '153', '173', '183']
all_dfs = []
for sheet in sheets:
    df = pd.read_excel("2026-Data-Test1-Final.xlsx", sheet_name=sheet)
    df['day'] = sheet
    all_dfs.append(df)
combined = pd.concat(all_dfs, ignore_index=True)

# ── Clean & Prep ───────────────────────────────────
def to_minutes(t):
    if pd.isna(t): return None
    if isinstance(t, datetime.time): return t.hour * 60 + t.minute
    if isinstance(t, float): return t * 24 * 60
    return None

for col in ['queue_start','queue_end','meal_start','meal_end']:
    combined[col+'_min'] = combined[col].apply(to_minutes)

combined['wait_min']     = combined['queue_end_min'] - combined['queue_start_min']
combined['meal_dur_min'] = combined['meal_end_min'] - combined['meal_start_min']
combined = combined[~((combined['meal_dur_min'].notna()) & (combined['meal_dur_min'] < 0))]

# ── Comment 1 ──────────────────────────────────────
st.header("Comment 1 — ลูกค้าต้องรอนาน และบางคนเลิกรอกลับ")

waited = combined[combined['queue_start'].notna() & combined['queue_end'].notna()]
wait_summary = waited.groupby('Guest_type')['wait_min'].mean().reset_index()
wait_summary.columns = ['Guest_type', 'avg_wait_min']

fig1 = px.bar(wait_summary, x='Guest_type', y='avg_wait_min',
              color='Guest_type', title='Average Wait Time by Guest Type')
st.plotly_chart(fig1)

walkaway = combined[combined['queue_start'].notna() & combined['meal_start'].isna()]
wa_summary = walkaway.groupby('Guest_type').size().reset_index()
wa_summary.columns = ['Guest_type', 'walkaway_count']

fig2 = px.bar(wa_summary, x='Guest_type', y='walkaway_count',
              color='Guest_type', title='Walk-away Count by Guest Type')
st.plotly_chart(fig2)

# ── Comment 2 ──────────────────────────────────────
st.header("Comment 2 — ยุ่งทุกวัน ไม่ยั่งยืน")

daily_pax = combined.groupby(['day','Guest_type'])['pax'].sum().reset_index()

fig3 = px.bar(daily_pax, x='day', y='pax', color='Guest_type',
              barmode='group', title='Total Pax per Day by Guest Type')
st.plotly_chart(fig3)

# ── Comment 3 ──────────────────────────────────────
st.header("Comment 3 — Walk-in นั่งนานกว่า In-house")

has_meal = combined[combined['meal_dur_min'].notna() & (combined['meal_dur_min'] > 0)]

fig4 = px.box(has_meal, x='Guest_type', y='meal_dur_min',
              color='Guest_type', title='Meal Duration by Guest Type')
st.plotly_chart(fig4)
