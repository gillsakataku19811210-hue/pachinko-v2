import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

st.set_page_config(layout="wide")

f = st.file_uploader("Excelファイルをアップロード", type=["xlsx"])

if f:
    try:
        # 1. タイトル取得（D4セル）
        title_df = pd.read_excel(f, header=None, nrows=5, usecols="D", engine='openpyxl')
        graph_title = str(title_df.iloc[3, 0])

        # 2. データ本体の読み込み（A4=header=3から）
        df = pd.read_excel(f, header=3, engine='openpyxl')
        
        def to_pure_num(s):
            val = re.sub(r'[^0-9.\-]', '', str(s))
            try:
                return float(val) if val else 0.0
            except:
                return 0.0

        d = pd.DataFrame()
        d['Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        
        # F列(5): 稼働 / M列(12): 売上 / N列(13): 粗利
        kado_val = df.iloc[:, 5].apply(to_pure_num)
        sales_val = df.iloc[:, 12].apply(to_pure_num)
        profit_val = df.iloc[:, 13].apply(to_pure_num)

        d['Out'] = kado_val * 1980
        s_out = d['Out'].replace(0, 1)
        d['Price'] = sales_val / s_out
        d['Profit'] = profit_val / s_out

        # 平均期間の選択
        st.sidebar.header("表示設定")
        days = st.sidebar.radio("平均期間を選択", [7, 14, 30], format_func=lambda x: f"{x}日間平均 ({x}D)")

        d['Out_MA'] = d['Out'].rolling(window=days, center=True, min_periods=1).mean()
        d['Price_MA'] = d['Price'].rolling(window=days, center=True, min_periods=1).mean()
        d['Profit_MA'] = d['Profit'].rolling(window=days, center=True, min_periods=1).mean()

        st.markdown(f"### {graph_title}")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(go.Scatter(x=d['Date'], y=d['Out_MA'], name=f"アウト({days}D)", 
                                 line=dict(color="blue", width=4)), secondary_y=False)
        fig.add_trace(go.Scatter(x=d['Date'], y=d['Price_MA'], name=f"単価({days}D)", 
                                 line=dict(color="green", dash='dot')), secondary_y=True)
        fig.add_trace(go.Scatter(x=d['Date'], y=d['Profit_MA'], name=f"粗利({days}D)", 
                                 line=dict(color="red", width=3)), secondary_y=True)

        fig.update_layout(
            height=650, 
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=20)
        )

        # 左軸：0〜30,000に固定
        fig.update_yaxes(title_text="アウト（枚）", tickformat=",d", secondary_y=False, range=[0, 30000])
        
        # 右軸：-6.0 〜 6.0 固定
        fig.update_yaxes(title_text="単価・粗利", tickformat=".2f", secondary_y=True, range=[-6.0, 6.0], dtick=1.0)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")