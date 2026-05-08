import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# 1. ページ全体の横幅を広げる設定
st.set_page_config(layout="wide")

f = st.file_uploader("Excelファイルをアップロード", type=["xlsx"])

if f:
    try:
        # --- データの読み込み ---
        # グラフタイトル用にD4(行3,列3)をピンポイントで取得
        title_df = pd.read_excel(f, header=None, nrows=5, usecols="D", engine='openpyxl')
        graph_title = str(title_df.iloc[3, 0]) # D4セルの値

        # 本体データ（A4=header=3から）
        df = pd.read_excel(f, header=3, engine='openpyxl')
        
        # 【重要】記号を消して数値化する関数
        def to_pure_num(s):
            # 文字列にしてから数字・小数点・マイナス以外を削除
            val = re.sub(r'[^0-9.\-]', '', str(s))
            try:
                return float(val) if val else 0.0
            except:
                return 0.0

        d = pd.DataFrame()
        # A列(0): 日付
        d['Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        
        # 列の指定（F列:5=稼働, M列:12=売上, N列:13=粗利）
        kado_val = df.iloc[:, 5].apply(to_pure_num)
        sales_val = df.iloc[:, 12].apply(to_pure_num) # M列
        profit_val = df.iloc[:, 13].apply(to_pure_num) # N列

        # 枚数・単価・粗利の計算
        d['Out'] = kado_val * 1980 # アウト（枚）
        s_out = d['Out'].replace(0, 1) # 0除算防止
        d['Price'] = sales_val / s_out # 玉単価
        d['Profit'] = profit_val / s_out # 玉粗利

        # --- サイドバーで平均期間を選択 ---
        st.sidebar.header("表示設定")
        days = st.sidebar.radio(
            "平均期間を選択", 
            [7, 14, 30], 
            index=0, 
            format_func=lambda x: f"{x}日間平均 ({x}D)"
        )

        # 移動平均の計算
        d['Out_MA'] = d['Out'].rolling(window=days, center=True, min_periods=1).mean()
        d['Price_MA'] = d['Price'].rolling(window=days, center=True, min_periods=1).mean()
        d['Profit_MA'] = d['Profit'].rolling(window=days, center=True, min_periods=1).mean()

        # --- グラフの描画 ---
        # タイトルを左上に大きく表示
        st.markdown(f"## {graph_title}")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # アウト（左軸：青）
        fig.add_trace(go.Scatter(
            x=d['Date'], y=d['Out_MA'], 
            name=f"アウト({days}D)", 
            line=dict(color="blue", width=4)
        ), secondary_y=False)

        # 玉単価（右軸：緑）
        fig.add_trace(go.Scatter(
            x=d['Date'], y=d['Price_MA'], 
            name=f"玉単価({days}D)", 
            line=dict(color="green", dash='dot', width=2)
        ), secondary_y=True)

        # 玉粗利（右軸：赤）
        fig.add_trace(go.Scatter(
            x=d['Date'], y=d['Profit_MA'], 
            name=f"玉粗利({days}D)", 
            line=dict(color="red", width=3)
        ), secondary_y=True)

        # 軸の詳細設定
        fig.update_layout(
            height=700, 
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=30, b=50)
        )

        # 左軸：0〜30,000に完全固定
        fig.update_yaxes(
            title_text="アウト（枚）", 
            tickformat=",d", 
            secondary_y=False, 
            range=[0, 30000]
        )
        
        # 右軸：-6.0 〜 6.0 に完全固定
        fig.update_yaxes(
            title_text="単価・粗利（円）", 
            tickformat=".2f", 
            secondary_y=True, 
            range=[-6.0, 6.0], 
            dtick=1.0
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"データの処理中にエラーが発生しました: {e}")