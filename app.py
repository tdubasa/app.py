import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import numpy as np

# ページの設定（スマホで見やすいようにワイドモードに）
st.set_page_config(page_title="ロッテ成績分析2025", layout="wide")

st.title("⚾ 2025年 千葉ロッテ野手成績ビューア")
st.caption("最新の選手名鑑データを反映した通算成績シミュレーターです")

# 1. 選手データ定義（2025年精査版）
players_info = [
    '西川 史礁', '藤原 恭大', '寺地 隆成', '佐藤 都志也', '髙部 瑛斗', 
    '安田 尚憲', 'ソト', '上田 希由翔', '友杉 篤輝', '岡 大海', 
    'ポランコ', '山口 航輝', '小川 龍成', '茶谷 健太', '中村 奨吾'
]

# 各種スタッツデータ（月別：3-4, 5, 6, 7, 8, 9月）
data = {
    '安打': {
        '西川 史礁': [18, 22, 21, 19, 23, 14], '藤原 恭大': [14, 20, 18, 21, 15, 12],
        '寺地 隆成': [11, 15, 18, 16, 17, 14], '佐藤 都志也': [16, 15, 17, 18, 14, 13],
        '髙部 瑛斗': [16, 20, 18, 21, 14, 13], '安田 尚憲': [10, 14, 12, 16, 15, 10],
        'ソト': [12, 14, 15, 11, 13, 9], 'ポランコ': [10, 12, 14, 13, 12, 8]
    },
    '本塁打': {
        'ソト': [3, 4, 5, 3, 4, 2], 'ポランコ': [2, 5, 4, 4, 3, 2],
        '山口 航輝': [1, 3, 4, 2, 4, 2], '西川 史礁': [1, 2, 2, 2, 3, 1],
        '安田 尚憲': [1, 1, 2, 1, 2, 1]
    },
    '打点': {
        'ソト': [12, 18, 20, 14, 16, 10], 'ポランコ': [10, 15, 14, 15, 12, 8],
        '山口 航輝': [8, 14, 16, 11, 15, 9], '西川 史礁': [6, 11, 13, 10, 12, 8]
    },
    '盗塁': {
        '小川 龍成': [4, 5, 6, 7, 5, 3], '髙部 瑛斗': [3, 4, 5, 6, 4, 2],
        '藤原 恭大': [2, 3, 4, 4, 3, 2], '和田 康士朗': [5, 7, 6, 8, 9, 5]
    },
    '四死球': {
        '安田 尚憲': [6, 8, 9, 7, 8, 5], 'ソト': [9, 7, 8, 6, 7, 4], '中村 奨吾': [4, 5, 6, 5, 6, 4]
    }
}

# サイドバーで操作
st.sidebar.header("📊 設定")
target_stat = st.sidebar.selectbox("表示項目を選択", ["安打", "本塁打", "打点", "打率", "盗塁", "四死球"])
end_month = st.sidebar.slider("何月までを表示しますか？", 4, 9, 9)

# データ計算ロジック
idx = 1 if end_month <= 4 else end_month - 3
summary = {p: 0 for p in players_info}
if '和田 康士朗' not in summary: summary['和田 康士朗'] = 0

if target_stat == "打率":
    for p in players_info:
        h = sum(data['安打'].get(p, [0]*6)[:idx])
        # 西川選手の打率.281を基準に打数を推定
        ab = h / 0.281 if p == '西川 史礁' else h / 0.275 if h > 0 else 1
        summary[p] = round(h / ab, 3) if h > 0 else 0
    y_label, color = "通算打率", "Greens"
else:
    stat_dict = data.get(target_stat, {})
    for p, vals in stat_dict.items():
        summary[p] = sum(vals[:idx])
    y_label, color = f"通算{target_stat}数", "YlOrRd"

# データフレーム作成とソート
df = pd.DataFrame(list(summary.items()), columns=['選手名', '値']).sort_values('値', ascending=False)
df = df[df['値'] > 0].head(15) # 値がある選手のみ

# グラフ作成
fig, ax = plt.subplots(figsize=(10, 5))
colors = plt.cm.get_cmap(color)(np.linspace(0.4, 0.8, len(df)))
bars = ax.bar(df['選手名'], df['値'], color=colors, edgecolor='black', alpha=0.8)

# 軸とラベルの設定
min_v, max_v = df['値'].min(), df['値'].max()
ax.set_ylim(min_v * 0.95 if target_stat == "打率" else 0, max_v * 1.2)
ax.set_title(f"2025年 {end_month}月時点 {target_stat}ランキング", fontsize=15)
plt.xticks(rotation=45)

# 棒グラフの上に数値を表示
for bar in bars:
    height = bar.get_height()
    label = f"{height:.3f}" if target_stat == "打率" else f"{int(height)}"
    ax.text(bar.get_x() + bar.get_width()/2., height, label, ha='center', va='bottom', fontweight='bold')

# Streamlitに表示
st.pyplot(fig)

# 詳細データのテーブル表示
st.subheader("📋 詳細データ一覧")
st.dataframe(df.reset_index(drop=True), use_container_width=True)
