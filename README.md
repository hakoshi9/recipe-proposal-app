# Chef AI Recipe Generator 🍳

食材の写真からAI（Gemini API）がレシピを提案するStreamlitアプリケーションです。

## 機能
- 食材画像の自動解析（複数枚対応）
- 一般料理 / 離乳食（月齢別）の切り替え
- 3つの異なるレシピ案を提案
- 冷蔵庫の定番食材を足した「ちょい足しモード」
- スマホ最適化UI

## セットアップ
1. リポジトリをクローン
2. `pip install -r requirements.txt`
3. `.env` ファイルに `GOOGLE_API_KEY` を設定
4. `streamlit run app.py` で起動
