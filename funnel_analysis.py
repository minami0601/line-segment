import pandas as pd
import plotly.graph_objects as go

# セグメントマッピング
segment_mappings = {
    "職業別": ["会社員", "フリーランス"],
    "経験年数別": ["未経験", "1年未満", "1年~2年", "2年~3年", "3年~4年", "4年以上"],
    "収入帯別": ["20万円以下", "20万円~40万円", "40万円~60万円", "60万円~80万円", "80万円~100万円", "100万円以上"]
}

# セグメントごとの色を定義
color_mappings = {
    "職業別": {
        "会社員": "#1f77b4",  # 青
        "フリーランス": "#ff7f0e",  # オレンジ
    },
    "経験年数別": {
        "未経験": "#377eb8",    # 青
        "1年未満": "#ff7f00",   # オレンジ
        "1年~2年": "#4daf4a",   # 緑
        "2年~3年": "#e41a1c",   # 赤
        "3年~4年": "#984ea3",   # 紫
        "4年以上": "#f781bf",   # ピンク
    },
    "収入帯別": {
        "20万円以下": "#1f77b4",      # 青
        "20万円~40万円": "#ff7f0e",   # オレンジ
        "40万円~60万円": "#2ca02c",   # 緑
        "60万円~80万円": "#d62728",   # 赤
        "80万円~100万円": "#9467bd",  # 紫
        "100万円以上": "#f781bf",   # ピンク
    }
}

# ファネルステージ
funnel_stages = ["回答数", "特典受取", "コンサル申込", "コンサル日程調整済", "コンサル実施", "紹介", "成約"]


def create_segment_data(df, segment_type, target_date):
    """セグメントデータを作成する関数"""
    segments = segment_mappings[segment_type]
    result_data = []

    # 指定された日付のデータを取得
    target_df = df[df['日付'].dt.date == target_date].copy()

    if len(target_df) == 0:
        return pd.DataFrame()

    for stage in funnel_stages:
        stage_data = {}
        total = 0
        for segment in segments:
            col_name = f"{segment}{stage}"
            value = target_df[col_name].iloc[0]
            stage_data[segment] = value
            total += value

        # パーセント計算
        if total > 0:
            for segment in segments:
                stage_data[f"{segment}_percent"] = (stage_data[segment] / total) * 100

        result_data.append({
            "stage": stage,
            **stage_data
        })

    return pd.DataFrame(result_data)


def create_funnel_chart(segment_data, segment_type):
    """ファネルチャートを作成する関数"""
    if segment_data.empty:
        return None

    # 全てのグラフを1つのFigureにまとめる
    fig = go.Figure()

    # グラフの位置を設定
    y_positions_graph = list(range(len(funnel_stages)))
    # ラベルの位置を設定（グラフより少し上に配置）
    y_positions_labels = [pos + 0.25 for pos in y_positions_graph]

    # セグメントの取得
    segments = segment_mappings[segment_type]

    for i, stage in enumerate(reversed(funnel_stages)):
        stage_data = segment_data[segment_data['stage'] == stage].iloc[0]

        # 総数を計算
        total_value = sum(stage_data[segment] for segment in segments)

        # 累積パーセントの計算
        cumulative = 0
        for segment in segments:
            percent = stage_data[f"{segment}_percent"]
            value = stage_data[segment]

            fig.add_trace(go.Bar(
                y=[y_positions_graph[i]],  # グラフの位置
                x=[percent],
                name=f"{segment} ({value:,.0f})",
                orientation='h',
                text=f"{percent:.1f}%",
                textposition='auto',
                offset=0,
                base=cumulative,
                marker_color=color_mappings[segment_type][segment],
                showlegend=True if i == len(funnel_stages)-1 else False
            ))
            cumulative += percent

    # Y軸のラベルに総数を追加
    y_labels = [f"{stage} (計: {int(sum(segment_data[segment_data['stage'] == stage][segment].iloc[0] for segment in segments)):,}人)"
                for stage in reversed(funnel_stages)]

    # レイアウトの設定
    fig.update_layout(
        height=600,
        margin=dict(l=200, r=20, t=0, b=40),
        showlegend=True,
        xaxis_range=[0, 100],
        xaxis_title="割合 (%)",
        yaxis=dict(
            ticktext=y_labels,
            tickvals=y_positions_labels,  # ラベルの位置
            tickmode="array",
            tickfont=dict(size=13),
            range=[-0.2, len(funnel_stages) - 0.3],  # グラフ全体の表示範囲
            ticksuffix="  ",
            side='left',
            ticklabelposition="outside left",
            tickangle=0,
            automargin=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="right",
            x=1
        ),
        bargap=0.5,
        plot_bgcolor='white',
        uniformtext=dict(mode='hide', minsize=10),
    )

    # バーの高さと位置を調整
    fig.update_traces(
        width=0.6,
        offset=0,
    )

    return fig
