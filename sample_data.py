import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_sample_horse_data():
    """競走馬の過去成績サンプルデータを生成"""

    # 馬名のサンプル
    horse_names = [
        "ディープインパクト",
        "オルフェーヴル",
        "アーモンドアイ",
        "ジェンティルドンナ",
        "キタサンブラック",
        "サトノダイヤモンド",
        "ウオッカ",
        "ダイワスカーレット",
        "ブエナビスタ",
        "ゴールドシップ",
        "トーセンラー",
        "フェノーメノ",
        "モーリス",
        "リスグラシュー",
        "クロノジェネシス",
        "コントレイル",
        "デアリングタクト",
        "グランアレグリア",
        "タイトルホルダー",
        "イクイノックス",
    ]

    # レース場のサンプル
    race_courses = ["東京", "中山", "京都", "阪神", "中京", "新潟", "福島", "小倉"]

    # 距離のサンプル
    distances = [1200, 1400, 1600, 1800, 2000, 2200, 2400, 2500, 3000, 3200]

    # 馬場状態
    track_conditions = ["良", "稍重", "重", "不良"]

    # 天気
    weather_conditions = ["晴", "曇", "雨", "小雨"]

    all_data = []

    for horse_name in horse_names:
        # 各馬に10-20レースの成績を生成
        num_races = random.randint(10, 20)
        horse_age = random.randint(3, 7)  # 3-7歳

        for i in range(num_races):
            # レース日付（過去2年間）
            days_ago = random.randint(0, 730)
            race_date = datetime.now() - timedelta(days=days_ago)

            # レース結果を生成（強い馬ほど良い成績を出しやすくする）
            horse_strength = random.random()  # 0-1の馬の強さ指標

            if horse_strength > 0.8:  # 強い馬
                finish_position = np.random.choice(
                    [1, 2, 3, 4, 5], p=[0.4, 0.25, 0.15, 0.1, 0.1]
                )
            elif horse_strength > 0.6:  # 中程度の馬
                finish_position = np.random.choice(
                    [1, 2, 3, 4, 5, 6, 7, 8],
                    p=[0.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.05, 0.1],
                )
            else:  # 弱い馬
                finish_position = random.randint(5, 18)

            # 出走頭数
            num_horses = random.randint(max(8, finish_position), 18)

            # タイム生成（距離に基づく）
            distance = random.choice(distances)
            base_time = distance * 0.065 + random.uniform(-5, 5)  # 基本タイム
            race_time = f"{int(base_time // 60)}:{int(base_time % 60):02d}.{random.randint(0, 9)}"

            # 騎手名
            jockeys = [
                "武豊",
                "福永祐一",
                "川田将雅",
                "ルメール",
                "デムーロ",
                "戸崎圭太",
                "岩田康誠",
                "池添謙一",
            ]

            race_data = {
                "馬名": horse_name,
                "レース日": race_date.strftime("%Y-%m-%d"),
                "競馬場": random.choice(race_courses),
                "距離": distance,
                "着順": finish_position,
                "出走頭数": num_horses,
                "タイム": race_time,
                "馬場状態": random.choice(track_conditions),
                "天気": random.choice(weather_conditions),
                "騎手": random.choice(jockeys),
                "斤量": round(random.uniform(52.0, 58.0), 1),
                "人気": random.randint(1, num_horses),
                "オッズ": round(random.uniform(1.2, 50.0), 1),
                "賞金": random.randint(0, 20000) if finish_position <= 5 else 0,
            }

            all_data.append(race_data)

    return pd.DataFrame(all_data)


def save_sample_data():
    """サンプルデータをCSVファイルに保存"""
    df = generate_sample_horse_data()
    df.to_csv("horse_performance_data.csv", index=False, encoding="utf-8")
    print(f"サンプルデータを生成しました: {len(df)}件のレース記録")
    return df


if __name__ == "__main__":
    save_sample_data()
