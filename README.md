# LINEファネル分析ダッシュボード

Google Spreadsheetsのデータを使用して、LINEのファネル分析を行うダッシュボードアプリケーションです。

## セットアップ

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

2. Google Sheets APIの設定:
   - Google Cloud Consoleで新しいプロジェクトを作成
   - Google Sheets APIを有効化
   - サービスアカウントを作成し、JSONキーをダウンロード
   - スプレッドシートをサービスアカウントのメールアドレスと共有

3. 認証情報の設定:
   - `.streamlit/secrets.toml.example` を `.streamlit/secrets.toml` にコピー
   - ダウンロードしたJSONキーの内容で `secrets.toml` を更新

## 実行方法

```bash
streamlit run app.py
```

## 機能

- Google Spreadsheetsからリアルタイムでデータを取得
- 日付ごとのファネル分析
- セグメント別（職業別、経験年数別、収入帯別）の比率表示
- インタラクティブな可視化
