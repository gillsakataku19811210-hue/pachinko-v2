import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- ページ設定 ---
st.set_page_config(layout="wide", page_title="パチンコデータ分析アプリ")

# --- 計算設定 ---
# 1時間あたりのアウト個数（定数）
OUT_PER_HOUR = 1980 

# --- データ処理関数 ---
def process_data():
    # 本来はここでCSV読み込みなどを行う想定
    # 現時点ではシミュレーションデータを作成
    dates = pd.date_range(start="2026-01-01", periods=130, freq='D')
    
    # 稼働時間のサンプルデータ（例：平均10〜20時間）
    working_hours = [10 + (i % 11) for i in range(130)]
    
    # 【重要】計算式：稼働時間 × 1980
    calculated_outs = [h * OUT_PER_HOUR for h in working_hours]
    
    df = pd.DataFrame({
        '日付': dates,
        '稼働時間': working_hours,
        'アウト': calculated_outs,
        '玉単価': [3.0 + (0.1 * (i % 10)) for i in range(130)],
        '玉粗利': [0.1 + (0.02 * (i % 5)) for i in range(130)]
    })
    return df

df = process_data()

# --- サイドバー設定 ---
st.sidebar.header("分析条件")
window_choice = st.sidebar.selectbox(
    "移動平均の期間", 
    ["7D", "14D", "30D"], 
    index=1
)

# 移動平均の計算
roll_map = {"7D": 7, "14D": 14, "30D": 30}
roll_num = roll_map[window_choice]

df['アウト_MA'] = df['アウト'].rolling(window=roll_num).mean()
df['玉単価_MA'] = df['玉単価'].rolling(window=roll_num).mean()
df['玉粗利_MA'] = df['玉粗利'].rolling(window=roll_num).mean()

# --- グラフ描画 ---
fig = make_subplots(specs=[[{"secondary_y": True}]])

# アウト（左軸：実数）
fig.add_trace(
    go.Scatter(x=df['日付'], y=df['アウト_MA'], name=f"アウト({window_choice}平均)", 
               line=dict(color="#0066CC", width=3)),
    secondary_y=False,
)

# 玉単価（右軸）
fig.add_trace(
    go.Scatter(x=df['日付'], y=df['玉単価_MA'], name="玉単価", 
               line=dict(color="#339933", dash='dot')),
    secondary_y=True,
)

# 玉粗利（右軸）
fig.add_trace(
    go.Scatter(x=df['日付'], y=df['玉粗利_MA'], name="玉粗利", 
               line=dict(color="#CC0000", width=2)),
    secondary_y=True,
)

# --- レイアウト ---
fig.update_layout(
    title=dict(text="機種別トレンド分析（汎用版）", font=dict(size=22)),
    margin=dict(t=100, b=50, l=60, r=60),
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
    hovermode="x unified",
    template="simple_white",
    height=700
)

# 軸のフォーマット
fig.update_yaxes(title_text="アウト（個）", tickformat=",d", secondary_y=False)
fig.update_yaxes(title_text="単価/粗利 (円)", tickformat=".2f", secondary_y=True, zeroline=True)

st.plotly_chart(fig, use_container_width=True)
