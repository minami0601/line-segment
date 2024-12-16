import pandas as pd
import plotly.graph_objects as go

# セグメントマッピング
segment_mappings = {
    "全体": ["全体"],
    "ユーザー属性": ["新規", "既存"],
    "職業別": ["会社員", "フリーランス"],
    "経験年数別": ["未経験", "1年未満", "1年~2年", "2年~3年", "3年~4年", "4年以上"],
    "収入帯別": ["20万円以下", "20万円~40万円", "40万円~60万円", "60万円~80万円", "80万円~100万円", "100万円以上"]
}

# セグメントごとの色を定義
color_mappings = {
    "全体": {
        "全体": "#2ecc71",  # 緑
    },
    "ユーザー属性": {
        "新規": "#3498db",  # 青
        "既存": "#e74c3c",  # 赤
    },
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

# 通常のファネルステージ
funnel_stages = ["回答数", "特典受取", "コンサル申込", "コンサル日程調整済", "コンサル実施", "紹介", "成約"]

# ユーザー属性用のファネルステージ
user_type_funnel_stages = ["友だち数", "回答数", "特典受取", "コンサル申込", "コンサル日程調整済", "コンサル実施", "紹介", "成約"]

def get_funnel_stages(segment_type):
    """セグメントタイプに応じたファネルステージを返す"""
    if segment_type in ["ユーザー属性", "全体"]:
        return user_type_funnel_stages
    return funnel_stages

def create_segment_data(df, segment_type, target_date):
    """セグメントデータを作成する関数"""
    segments = segment_mappings[segment_type]
    result_data = []
    stages = get_funnel_stages(segment_type)

    # ��定された日付のデータを取得
    target_df = df[df['日付'].dt.date == target_date].copy()

    if len(target_df) == 0:
        return pd.DataFrame()

    for stage in stages:
        stage_data = {}
        total = 0
        for segment in segments:
            if segment == "全体":
                # 新規/既存の合計を計算
                if stage == "友だち数":
                    value = sum(target_df[f"{seg}友だち数"].iloc[0] for seg in ["新規", "既存"])
                else:
                    value = sum(target_df[f"{seg}{stage}"].iloc[0] for seg in ["新規", "既存"])
            elif segment in ["新規", "既存"]:
                # 新規/既存の値を取得（友だち数の場合は特別な処理）
                if stage == "友だち数":
                    value = target_df[f"{segment}友だち数"].iloc[0]
                else:
                    value = target_df[f"{segment}{stage}"].iloc[0]
            else:
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
    """ファネルチャートを作成する関数（セグメント比率分析用）"""
    if segment_data.empty:
        return None

    fig = go.Figure()
    stages = get_funnel_stages(segment_type)
    y_positions_graph = list(range(len(stages)))
    y_positions_labels = [pos + 0.25 for pos in y_positions_graph]
    segments = segment_mappings[segment_type]

    for i, stage in enumerate(reversed(stages)):
        stage_data = segment_data[segment_data['stage'] == stage].iloc[0]
        total_value = sum(stage_data[segment] for segment in segments)
        cumulative = 0

        for segment in segments:
            percent = stage_data[f"{segment}_percent"]
            value = stage_data[segment]

            fig.add_trace(go.Bar(
                y=[y_positions_graph[i]],
                x=[percent],
                name=f"{segment} ({value:,.0f})",
                orientation='h',
                text=f"{percent:.1f}%",
                textposition='auto',
                offset=0,
                base=cumulative,
                marker_color=color_mappings[segment_type][segment],
                showlegend=True if i == len(stages)-1 else False
            ))
            cumulative += percent

    y_labels = [f"{stage} (計: {int(sum(segment_data[segment_data['stage'] == stage][segment].iloc[0] for segment in segments)):,}人)"
                for stage in reversed(stages)]

    fig.update_layout(
        height=600,
        margin=dict(l=200, r=20, t=0, b=40),
        showlegend=True,
        xaxis_range=[0, 100],
        xaxis_title="割合 (%)",
        yaxis=dict(
            ticktext=y_labels,
            tickvals=y_positions_labels,
            tickmode="array",
            tickfont=dict(size=13),
            range=[-0.2, len(stages) - 0.3],
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

    fig.update_traces(
        width=0.6,
        offset=0,
    )

    return fig

def create_segment_funnel_data(df, segment_type, target_date):
    """セグメントごとのファネルデータを作成する関数"""
    segments = segment_mappings[segment_type]
    result_data = {}
    stages = get_funnel_stages(segment_type)

    # 指定された日付のデータを取得
    target_df = df[df['日付'].dt.date == target_date].copy()

    if len(target_df) == 0:
        return None

    for segment in segments:
        segment_values = []
        prev_value = None

        for stage in stages:
            if segment == "全体":
                # 新規/既存の合計を計算
                if stage == "友だち数":
                    value = sum(target_df[f"{seg}友だち数"].iloc[0] for seg in ["新規", "既存"])
                else:
                    value = sum(target_df[f"{seg}{stage}"].iloc[0] for seg in ["新規", "既存"])
            elif segment in ["新規", "既存"]:
                # 新規/既存の値を取得（友だち数の場合は特別な処理）
                if stage == "友だち数":
                    value = target_df[f"{segment}友だち数"].iloc[0]
                else:
                    value = target_df[f"{segment}{stage}"].iloc[0]
            else:
                col_name = f"{segment}{stage}"
                value = target_df[col_name].iloc[0]

            # 遷移率の計算
            if prev_value is not None and prev_value > 0:
                cvr = (value / prev_value) * 100
            else:
                cvr = 100  # 最初のステージは100%

            segment_values.append({
                'stage': stage,
                'value': value,
                'cvr': cvr
            })

            prev_value = value

        result_data[segment] = segment_values

    return result_data

def create_individual_funnel_chart(segment_data, segment_type, segment):
    """個別のセグメントのファネルチャートを作成する関数"""
    if segment_data is None:
        return None

    fig = go.Figure()
    stages = get_funnel_stages(segment_type)
    values = [d['value'] for d in segment_data[segment]]
    cvrs = [d['cvr'] for d in segment_data[segment]]

    # ステージの位置を設定（上から下へ）
    y_positions = list(range(len(stages)))
    y_positions.reverse()  # 上から下へ表示するために反転

    # バーの追加
    fig.add_trace(go.Bar(
        x=values,
        y=stages,
        orientation='h',
        marker=dict(
            color=color_mappings[segment_type][segment],
        ),
        text=[f"{int(val):,}人" for val in values],
        textposition='outside',
        name=segment,
    ))

    # CVRの表示を追加
    for i, (val, cvr) in enumerate(zip(values, cvrs)):
        if i > 0:  # 最初のステージ以外
            fig.add_annotation(
                x=max(values) * 1.1,
                y=stages[i],
                text=f"CVR: {cvr:.1f}%",
                showarrow=False,
                xanchor="left",
                font=dict(size=12)
            )

    fig.update_layout(
        title=dict(
            text=f"{segment}のファネル分析",
            x=0.5,
            y=0.95,
            xanchor="center",
            yanchor="top",
            font=dict(size=20)
        ),
        height=400,
        margin=dict(l=20, r=150, t=80, b=20),
        showlegend=False,
        hovermode='x',
        xaxis=dict(
            title="人数",
            showgrid=True,
            gridcolor='lightgray',
        ),
        yaxis=dict(
            autorange="reversed",  # 上から下へ表示
            showgrid=True,
            gridcolor='lightgray',
        ),
        plot_bgcolor='white',
    )

    return fig
