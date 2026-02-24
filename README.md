# Chef AI Recipe Generator

食材の写真からAI（Gemini API）がレシピを提案するNuxt.jsアプリケーション。

## 機能

- 食材画像の自動解析（複数枚対応）
- カメラ直接撮影・複数枚連続撮影・EXIF向き補正
- 一般料理 / 離乳食（月齢別）の切り替え
- 3つの異なるレシピ案を提案
- 冷蔵庫の定番食材を足した「ちょい足しモード」
- スマホ最適化UI

## セットアップ

```bash
pnpm install
```

`.env` ファイルを作成:

```
GEMINI_API_KEY=your_api_key_here
```

## 開発サーバー起動

| コマンド | 用途 |
|---|---|
| `pnpm dev` | 通常の開発（localhost のみ） |
| `pnpm dev:host` | LAN 内スマホからアクセス可（カメラ不可） |
| `pnpm dev:mobile` | **スマホでカメラも使う場合**（ngrok 経由 HTTPS） |

## スマホ開発環境 (カメラ含む)

`getUserMedia`（カメラ API）は **HTTPS または localhost** でのみ動作するため、
スマホからカメラ機能をテストするには ngrok を使って HTTPS トンネルを張る必要がある。

### 前提条件

**ngrok のインストール（初回のみ）:**

```bash
winget install ngrok.ngrok
```

**ngrok アカウント認証（初回のみ）:**

1. [https://ngrok.com](https://ngrok.com) で無料アカウント作成
2. ダッシュボード → "Your Authtoken" でトークンをコピー
3. 以下を実行:

```bash
ngrok config add-authtoken <YOUR_TOKEN>
```

### 起動

```bash
pnpm dev:mobile
```

ターミナルに表示される ngrok の HTTPS URL をスマホで開く:

```
[ngrok] Forwarding  https://xxxx-xxxx.ngrok-free.app -> http://localhost:3000
```

> 初回アクセス時に ngrok の警告画面が表示される場合は「Visit Site」をタップして進む。

### PC の IP アドレス（参考）

このプロジェクトの開発機: `192.168.3.7`
スマホとPCが同じ Wi-Fi の場合、カメラ不要なら `http://192.168.3.7:3000` でも可（`pnpm dev:host` 使用）。

## ビルド・デプロイ

```bash
pnpm build
```

Cloud Run へのデプロイは `.github/workflows/` の CI/CD を参照。
