import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from funnel_analysis import (
    create_segment_funnel_data,
    create_individual_funnel_chart,
    segment_mappings
)

# ページ設定
st.set_page_config(page_title="LINEファネル分析", layout="wide")
st.title("ファネル分析")


@st.cache_data
def load_data():
    try:
        # Google Sheets APIの認証情報
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # 認証情報の取得（サービスアカウントのJSONファイルが必要）
        if "GOOGLE_SHEETS_CREDS" not in st.secrets:
            st.error("Google Sheets認証情報が設定されていません。")
            return pd.DataFrame()

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GOOGLE_SHEETS_CREDS"], scope
        )

        # Google Sheetsに接続
        gc = gspread.authorize(credentials)

        # スプレッドシートを開く
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1fKsBoOxSeP0LaPiqEdtAwZfT-9tbDXv5jR50ItTlG4U/edit?usp=sharing"
        sheet = gc.open_by_url(spreadsheet_url).worksheet("DB")

        # データをDataFrameに変換
        data = sheet.get_all_values()
        headers = data[0]
        df = pd.DataFrame(data[1:], columns=headers)

        # 日付列を datetime に変換
        df["日付"] = pd.to_datetime(df["日付"])

        # 数値列を数値型に変換
        numeric_columns = df.columns.difference(["日付"])
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")

        return df

    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {str(e)}")
        return pd.DataFrame()


# データを読み込む
df = load_data()

if df.empty:
    st.warning("データを読み込めませんでした。")
else:
    # フィルター設定（2列レイアウト）
    col1, col2 = st.columns(2)

    with col1:
        # 日付選択
        target_date = st.date_input(
            "日付を選択",
            value=df["日付"].max().date(),
            min_value=df["日付"].min().date(),
            max_value=df["日付"].max().date(),
        )

    with col2:
        # セグメント選択
        segment_type = st.selectbox(
            "セグメント種別を選択",
            ["全体", "ユーザー属性", "職業別", "経験年数別", "収入帯別"],
        )

    # フータ作成とグラフ表示
    segment_data = create_segment_funnel_data(df, segment_type, target_date)

    if segment_data is not None:
        segments = segment_mappings[segment_type]

        # セグメントごとに個別のグラフを表示
        for segment in segments:
            fig = create_individual_funnel_chart(segment_data, segment_type, segment)
            st.plotly_chart(fig, use_container_width=True)

        # 各セグメントのCVR詳細を表示
        st.markdown("### セグメント別コンバージョン分析")

        for segment in segments:
            st.markdown(f"#### {segment}")
            segment_values = segment_data[segment]

            for i, data in enumerate(segment_values):
                if i > 0:  # 最初のステージ以外
                    prev_value = segment_values[i - 1]["value"]
                    current_value = data["value"]
                    cvr = data["cvr"]
                    st.write(
                        f"**{data['stage']}**: {int(current_value):,}人 (CVR: {cvr:.1f}%)"
                    )
                else:  # 最初のステージ
                    st.write(f"**{data['stage']}**: {int(data['value']):,}人")
    else:
        st.warning(f"{target_date}のデータは存在しません。")
