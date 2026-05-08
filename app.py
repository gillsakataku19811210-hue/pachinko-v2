import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("Trend Analysis")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx", "csv"])
period = st.sidebar.radio("MA Period", [7, 14, 30], index=1)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        df['日付'] = pd.to_datetime(df['日付'])
        
        # Calculation logic
        df['out'] = df['稼働時間'] * 1980
        df['玉単価'] = df['売上金額'] / df['out']
        df['玉粗利'] = df['粗利金額'] / df['out']

        # Moving Average
        for col in ['out', '玉単価', '玉粗利']:
            df[f'{col}_MA'] = df[col].rolling(window=period, center=True).mean()

        # Plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df['日付'], y=df['out_MA'], name="Out", line=dict(color="blue", width=4)), secondary_y=False)
        fig.add_trace(go.Scatter(x=df['日付'], y=df['玉単価_MA'], name="Price", line=dict(color="green", dash='dot')), secondary_y=True)
        fig.add_trace(go.Scatter(x=df['日付'], y=df['玉粗利_MA'], name="Profit", line=dict(color="red")), secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload a file.")