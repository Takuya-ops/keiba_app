import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from sample_data import generate_sample_horse_data
import os

# ページ設定
st.set_page_config(
    page_title="競馬予測ダッシュボード",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# カスタムCSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2E7D32;
    }
    .horse-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    """データを読み込む"""
    csv_path = "horse_performance_data.csv"

    if not os.path.exists(csv_path):
        # CSVファイルが存在しない場合は新しく生成
        df = generate_sample_horse_data()
        df.to_csv(csv_path, index=False, encoding="utf-8")
    else:
        df = pd.read_csv(csv_path, encoding="utf-8")

    # データ型の調整
    df["レース日"] = pd.to_datetime(df["レース日"])
    return df


def calculate_horse_stats(df, horse_name):
    """指定した馬の統計情報を計算"""
    horse_data = df[df["馬名"] == horse_name].copy()

    if len(horse_data) == 0:
        return None

    stats = {
        "出走回数": len(horse_data),
        "勝利数": len(horse_data[horse_data["着順"] == 1]),
        "2着以内": len(horse_data[horse_data["着順"] <= 2]),
        "3着以内": len(horse_data[horse_data["着順"] <= 3]),
        "平均着順": round(horse_data["着順"].mean(), 2),
        "勝率": round(
            len(horse_data[horse_data["着順"] == 1]) / len(horse_data) * 100, 1
        ),
        "連対率": round(
            len(horse_data[horse_data["着順"] <= 2]) / len(horse_data) * 100, 1
        ),
        "複勝率": round(
            len(horse_data[horse_data["着順"] <= 3]) / len(horse_data) * 100, 1
        ),
        "総賞金": horse_data["賞金"].sum(),
        "平均オッズ": round(horse_data["オッズ"].mean(), 1),
    }

    return stats


def main():
    # ヘッダー
    st.markdown(
        '<h1 class="main-header">🏇 競馬予測ダッシュボード</h1>', unsafe_allow_html=True
    )

    # データ読み込み
    try:
        df = load_data()
        st.success(f"✅ データ読み込み完了: {len(df)}件のレース記録")
    except Exception as e:
        st.error(f"❌ データ読み込みエラー: {e}")
        return

    # サイドバー
    st.sidebar.header("🔍 フィルター設定")

    # 馬名選択
    horse_names = sorted(df["馬名"].unique())
    selected_horses = st.sidebar.multiselect(
        "馬名を選択", horse_names, default=horse_names[:5]
    )

    # 期間選択
    date_range = st.sidebar.date_input(
        "期間選択",
        value=(df["レース日"].min().date(), df["レース日"].max().date()),
        min_value=df["レース日"].min().date(),
        max_value=df["レース日"].max().date(),
    )

    # 競馬場選択
    race_courses = st.sidebar.multiselect(
        "競馬場を選択",
        sorted(df["競馬場"].unique()),
        default=sorted(df["競馬場"].unique()),
    )

    # データフィルタリング
    if len(date_range) == 2:
        filtered_df = df[
            (df["馬名"].isin(selected_horses))
            & (df["レース日"].dt.date >= date_range[0])
            & (df["レース日"].dt.date <= date_range[1])
            & (df["競馬場"].isin(race_courses))
        ]
    else:
        filtered_df = df[
            (df["馬名"].isin(selected_horses)) & (df["競馬場"].isin(race_courses))
        ]

    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。")
        return

    # メインコンテンツ
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 統計サマリー", "🏆 成績詳細", "📈 パフォーマンス分析", "📋 レース履歴"]
    )

    with tab1:
        st.subheader("📊 選択した馬の統計サマリー")

        if len(selected_horses) > 0:
            cols = st.columns(min(len(selected_horses), 3))

            for i, horse_name in enumerate(selected_horses):
                with cols[i % 3]:
                    stats = calculate_horse_stats(filtered_df, horse_name)
                    if stats:
                        st.markdown(
                            f"""
                        <div class="horse-card">
                            <h4>🐎 {horse_name}</h4>
                            <p><strong>出走回数:</strong> {stats['出走回数']}回</p>
                            <p><strong>勝率:</strong> {stats['勝率']}%</p>
                            <p><strong>連対率:</strong> {stats['連対率']}%</p>
                            <p><strong>複勝率:</strong> {stats['複勝率']}%</p>
                            <p><strong>平均着順:</strong> {stats['平均着順']}</p>
                            <p><strong>総賞金:</strong> {stats['総賞金']:,}万円</p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

    with tab2:
        st.subheader("🏆 馬別成績比較")

        # 勝率比較グラフ
        horse_stats_list = []
        for horse_name in selected_horses:
            stats = calculate_horse_stats(filtered_df, horse_name)
            if stats:
                horse_stats_list.append(
                    {
                        "馬名": horse_name,
                        "勝率": stats["勝率"],
                        "連対率": stats["連対率"],
                        "複勝率": stats["複勝率"],
                        "出走回数": stats["出走回数"],
                    }
                )

        if horse_stats_list:
            stats_df = pd.DataFrame(horse_stats_list)

            # 勝率・連対率・複勝率の比較
            fig = px.bar(
                stats_df,
                x="馬名",
                y=["勝率", "連対率", "複勝率"],
                barmode="group",
                title="馬別成績比較（勝率・連対率・複勝率）",
                color_discrete_sequence=["#2E7D32", "#4CAF50", "#81C784"],
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("📈 パフォーマンス分析")

        col1, col2 = st.columns(2)

        with col1:
            # 距離別成績
            distance_performance = (
                filtered_df.groupby(["馬名", "距離"])
                .agg({"着順": "mean"})
                .reset_index()
            )

            fig = px.scatter(
                distance_performance,
                x="距離",
                y="着順",
                color="馬名",
                title="距離別平均着順",
                labels={"着順": "平均着順", "距離": "距離(m)"},
            )
            fig.update_yaxes(autorange="reversed")  # 着順は小さいほど良いので逆順
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 馬場状態別成績
            track_performance = (
                filtered_df.groupby(["馬名", "馬場状態"])
                .agg({"着順": "mean"})
                .reset_index()
            )

            fig = px.box(
                filtered_df,
                x="馬場状態",
                y="着順",
                color="馬名",
                title="馬場状態別着順分布",
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("📋 レース履歴詳細")

        # 馬名でフィルタリング
        selected_horse_detail = st.selectbox("詳細を見る馬を選択", selected_horses)

        if selected_horse_detail:
            horse_detail_df = filtered_df[
                filtered_df["馬名"] == selected_horse_detail
            ].copy()
            horse_detail_df = horse_detail_df.sort_values("レース日", ascending=False)

            # レース履歴テーブル
            st.dataframe(
                horse_detail_df[
                    [
                        "レース日",
                        "競馬場",
                        "距離",
                        "着順",
                        "出走頭数",
                        "タイム",
                        "騎手",
                        "人気",
                        "オッズ",
                        "賞金",
                    ]
                ],
                use_container_width=True,
            )

            # 時系列での着順変化
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=horse_detail_df["レース日"],
                    y=horse_detail_df["着順"],
                    mode="lines+markers",
                    name=selected_horse_detail,
                    line=dict(color="#2E7D32", width=2),
                    marker=dict(size=8),
                )
            )
            fig.update_layout(
                title=f"{selected_horse_detail}の着順推移",
                xaxis_title="レース日",
                yaxis_title="着順",
                yaxis=dict(autorange="reversed"),
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
