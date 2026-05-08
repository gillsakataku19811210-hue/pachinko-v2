import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# 画面設定
st.set_page_config(layout="wide")
st.title("Trend Analysis")

f = st.file_uploader("Upload Excel", type=["xlsx"])

if f:
    try:
        # Excel読み込み
        df = pd.read_excel(f, header=3, engine='openpyxl')
        
        # 数値変換
        def clean(s):
            return pd.to_numeric(s.astype(str).str.replace('[\\,円]', '', regex=True), errors='coerce').fillna(0)

        d = pd.DataFrame()
        d['Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        out_raw = clean(df.iloc[:, 5]) * 1980
        uri_raw = clean(df.iloc[:, 8])
        ari_raw = clean(df.iloc[:, 10])

        # 計算
        safe_out = out_raw.replace(0, 1)
        d['Price'] = uri_raw / safe_out
        d['Profit'] = ari_raw / safe_out

        # 移動平均
        for col in ['Price', 'Profit']:
            d[f'{col}_MA'] = d[col].rolling(7, center=True, min_periods=1).mean()

        # グラフ作成
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 玉単価（右軸）
        fig.add_trace(go.Scatter(x=d['Date'], y=d['Price_MA'], name="玉単価", line=dict(color="green", dash='dot')), secondary_y=True)
        # 玉粗利（右軸）
        fig.add_trace(go.Scatter(x=d['Date'], y=d['Profit_MA'], name="玉粗利", line=dict(color="red", width=3)), secondary_y=True)

        # 【修正】0のライン（基準線）を追加
        fig.add_shape(
            type="line",
            x0=d['Date'].min(), x1=d['Date'].max(),
            y0=0, y1=0,
            yref="y2", # 右軸（secondary_y=True）を基準にする
            line=dict(color="black", width=3), # 濃い黒色、太さ3
        )

        # レイアウト設定
        fig.update_layout(height=600, hovermode="x unified", legend=dict(orientation="h", y=1.1, x=1))
        
        # 右軸：単価・粗利（-2.0 〜 +2.0、0.5刻み）
        fig.update_yaxes(title_text="単価・粗利（円）", tickformat=".2f", secondary_y=True, range=[-2.0, 2.0], dtick=0.5)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")