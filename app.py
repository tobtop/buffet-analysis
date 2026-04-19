import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.title("Busy Buffet Analysis — Hotel Amber 85")

st.markdown("""
### บริบทของโจทย์
โรงแรม Hotel Amber 85 เปิดบุฟเฟ่ต์อาหารเช้าพร้อมโปรโมชั่น:
- กินได้ไม่อั้น (All you can eat)
- ราคา 159 บาท วันธรรมดา / 199 บาท วันหยุด  
- นั่งได้สูงสุด 5 ชั่วโมง

หลังโปรโมทผ่าน TikTok ลูกค้า Walk-in เพิ่มขึ้นกะทันหัน 
ทำให้บุฟเฟ่ต์แน่นและบริหารยาก ทีม data จึงถูกส่งมาวิเคราะห์

### ข้อมูลที่ใช้
- **5 วัน** ของการเก็บข้อมูล (วัน 133, 143, 153, 173, 183)
- **363 กลุ่มลูกค้า** หลัง clean data
- แบ่งเป็น **In-house** (พักโรงแรม) และ **Walk-in** (มาเฉพาะบุฟเฟ่ต์)
""")

st.divider()

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

waited   = combined[combined['queue_start'].notna() & combined['queue_end'].notna()]
walkaway = combined[combined['queue_start'].notna() & combined['meal_start'].isna()]
has_meal = combined[combined['meal_dur_min'].notna() & (combined['meal_dur_min'] > 0)]

wait_summary = waited.groupby('Guest_type')['wait_min'].mean().reset_index()
wait_summary.columns = ['Guest_type', 'avg_wait_min']

wa_summary = walkaway.groupby('Guest_type').size().reset_index()
wa_summary.columns = ['Guest_type', 'walkaway_count']

daily_pax = combined.groupby(['day','Guest_type'])['pax'].sum().reset_index()

# ── Task 1 ──────────────────────────────────────
st.title("Task 1 — พิสูจน์คำพูดพนักงาน")

# Comment 1
st.header("Comment 1 —  ลูกค้าต้องรอนานจริงไหม? และบางคนเลิกรอจนกลับ")
st.write("พนักงานบอกว่าลูกค้าทั้งสองประเภทต้องรอนานจนบางคนเลิกรอ จะเห็นได้ว่าลูกค้าจาก Walk-in รอนานกว่าจริงและเป็นเวลา 38 นาที")

col1, col2, col3 = st.columns(3)
col1.metric("In-house รอเฉลี่ย", "28 นาที")
col2.metric("Walk-in รอเฉลี่ย", "38 นาที")
col3.metric("Walk-away ทั้งหมด", "14 กลุ่ม")

fig1 = px.bar(wait_summary, x='Guest_type', y='avg_wait_min',
              color='Guest_type', title='Average Wait Time by Guest Type')
st.plotly_chart(fig1)
st.caption("✅ Task 1: Walk-in รอเฉลี่ย 38 นาที นานกว่า In-house ที่รอแค่ 28 นาที")
st.info("❌ Task 2 Action 3: Queue skip ช่วย In-house แต่ Walk-in ยังรอนานอยู่ดี ไม่แก้ปัญหาหลัก")

fig2 = px.bar(wa_summary, x='Guest_type', y='walkaway_count',
              color='Guest_type', title='Walk-away Count by Guest Type')
st.plotly_chart(fig2)
st.info("✅ Task 1: มีคนเลิกรอจริง 14 กลุ่ม ทั้ง In-house และ Walk-in")
st.info("❌ Task 2 Action 3: Walk-away เป็น Walk-in 7 กลุ่ม เท่ากับ In-house → queue skip ไม่ได้แก้ครึ่งหนึ่งของปัญหา")

# Comment 2
st.header("Comment 2 — ยุ่งทุกวัน ไม่ยั่งยืน")

fig3 = px.bar(daily_pax, x='day', y='pax', color='Guest_type',
              barmode='group', title='Total Pax per Day by Guest Type')
st.plotly_chart(fig3)
st.caption("✅ Task 1: Walk-in เพิ่มขึ้นทุกวัน In-house คงที่ — ยุ่งจริงทุกวัน")
st.info("❌ Task 2 Action 2: Walk-in พุ่งขึ้นจาก TikTok viral ไม่ใช่เพราะราคาถูก ขึ้นราคาไม่ลด demand")

# Comment 3
st.header("Comment 3 — Walk-in นั่งนานกว่า In-house")

fig4 = px.box(has_meal, x='Guest_type', y='meal_dur_min',
              color='Guest_type', title='Meal Duration by Guest Type')
st.plotly_chart(fig4)
st.caption("✅ Task 1: Walk-in นั่งเฉลี่ย 73 นาที vs In-house 46 นาที ต่างกัน 27 นาที")
st.info("❌ Task 2 Action 1: Walk-in นั่งแค่ 66 นาที (median) ไม่ใช่ 5 ชั่วโมง → ลดเวลานั่งไม่ได้แก้ปัญหา demand เกิน capacity")
