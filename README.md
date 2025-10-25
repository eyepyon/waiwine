# LiveKit Video Chat App

LiveKitを使用したWebビデオチャットアプリケーションです。

DEMO  
http://wai.wine:3000/  

LP  
https://www.wai.wine/  

Documents  
https://www.wai.wine/wine20251025.pdf  


## 機能

- 🔐 Googleログイン認証
- 🌍 多言語対応（メイン言語設定）
- 🎥 リアルタイムビデオチャット
- 👥 複数参加者対応
- ⚙️ ユーザー設定管理

## 技術スタック

### バックエンド
- Python + Streamlit
- LiveKit Python SDK
- SQLite データベース
- Google OAuth認証

### フロントエンド
- Vue.js 3
- LiveKit Client SDK
- Vite

## セットアップ

### 1. 環境変数の設定

`.env` ファイルを編集して、必要な情報を設定してください：

```env
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
LIVEKIT_URL=wss://your-livekit-server.com
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key_for_sessions
```

### 2. バックエンドの起動

```bash
# 依存関係のインストール
pip install -r requirements.txt

# Streamlitアプリの起動
streamlit run backend/app.py
```

### 3. フロントエンドの起動

```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

## 使用方法

1. **バックエンド (Streamlit)** でユーザー登録・ログインを行う
2. ビデオチャットタブでルーム名を入力し、「ルームに参加」をクリック
3. 表示される接続情報（URL、トークン、ルーム名）をコピー
4. **フロントエンド (Vue.js)** でコピーした情報を入力
5. 「ルームに参加」でビデオチャット開始

## LiveKit サーバーについて

このアプリを使用するには、LiveKitサーバーが必要です：

- [LiveKit Cloud](https://cloud.livekit.io/) を使用（推奨）
- または自分でLiveKitサーバーをホスティング

## 開発メモ

- 現在のGoogleログインは簡易実装です。本番環境では適切なOAuth実装が必要
- データベースはSQLiteを使用していますが、本番環境ではPostgreSQLなどを推奨
- フロントエンドとバックエンドは分離されており、独立して動作します

## ライセンス

MIT License