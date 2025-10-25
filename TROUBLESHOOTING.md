# トラブルシューティングガイド

## "Failed to get google auth URL" エラー

このエラーは、Google OAuth認証情報が正しく設定されていない場合に発生します。

### 解決手順

#### 1. 環境変数の確認

```bash
cd backend
python check_env.py
```

このスクリプトは以下を確認します：
- `.env`ファイルが正しく読み込まれているか
- `GOOGLE_CLIENT_ID`と`GOOGLE_CLIENT_SECRET`が設定されているか
- OAuth設定が正しく初期化されているか

#### 2. `.env`ファイルの確認

プロジェクトルートの`.env`ファイルを開いて、以下が正しく設定されているか確認：

```env
GOOGLE_CLIENT_ID=your_actual_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
```

**注意点：**
- `=`の前後にスペースを入れない
- 値を引用符で囲まない
- プレースホルダー（`your_google_client_id`など）のままになっていないか確認

#### 3. Google Cloud Consoleで認証情報を確認

1. [Google Cloud Console](https://console.developers.google.com/)にアクセス
2. プロジェクトを選択
3. 「APIとサービス」→「認証情報」
4. OAuth 2.0 クライアントIDをクリック
5. クライアントIDとクライアントシークレットをコピー
6. `.env`ファイルに貼り付け

#### 4. リダイレクトURIの確認

Google Cloud Consoleで、以下のリダイレクトURIが登録されているか確認：

```
http://localhost:8000/api/auth/google/callback
```

本番環境の場合：
```
https://yourdomain.com/api/auth/google/callback
```

#### 5. バックエンドサーバーの再起動

環境変数を変更した後は、必ずバックエンドサーバーを再起動：

```bash
# 現在のサーバーを停止（Ctrl+C）
cd backend
python api_app.py
```

#### 6. デバッグエンドポイントで確認

ブラウザまたはcurlで以下にアクセス：

```bash
curl http://localhost:8000/api/auth/providers/debug
```

レスポンス例（正常な場合）：
```json
{
  "google_client_id_set": true,
  "google_client_secret_set": true,
  "google_client_id_length": 72,
  "google_config_exists": true,
  "google_config_enabled": true,
  "all_providers": ["google", "twitter", "line"],
  "enabled_providers": ["google"]
}
```

レスポンス例（問題がある場合）：
```json
{
  "google_client_id_set": false,
  "google_client_secret_set": false,
  "google_client_id_length": 0,
  "google_config_exists": false,
  "google_config_enabled": false
}
```

### よくある問題

#### 問題1: `.env`ファイルが読み込まれない

**原因:** `.env`ファイルの場所が間違っている

**解決策:** `.env`ファイルがプロジェクトのルートディレクトリ（`backend/`の親ディレクトリ）にあることを確認

#### 問題2: 環境変数が空文字列

**原因:** `.env`ファイルの書式が間違っている

**解決策:** 以下の書式を確認
```env
# ❌ 間違い
GOOGLE_CLIENT_ID = "your_id"
GOOGLE_CLIENT_ID='your_id'
GOOGLE_CLIENT_ID = your_id

# ✅ 正しい
GOOGLE_CLIENT_ID=your_id
```

#### 問題3: サーバーを再起動していない

**原因:** 環境変数の変更後にサーバーを再起動していない

**解決策:** 必ずサーバーを再起動する

#### 問題4: プレースホルダーのまま

**原因:** `.env`ファイルの値が`your_google_client_id`などのプレースホルダーのまま

**解決策:** 実際のGoogle Cloud Consoleから取得した値に置き換える

## その他のエラー

### "Camera permission denied"

ブラウザのカメラ権限を確認してください。

### "LiveKit connection failed"

1. `.env`の`LIVEKIT_API_KEY`、`LIVEKIT_API_SECRET`、`LIVEKIT_URL`を確認
2. LiveKitサーバーが起動しているか確認

### "Translation service error"

1. `.env`の`DEEPGRAM_API_KEY`と`OPENAI_API_KEY`を確認
2. APIキーの利用制限を確認

## サポート

問題が解決しない場合は、以下の情報を含めて報告してください：

1. `python check_env.py`の出力
2. `curl http://localhost:8000/api/auth/providers/debug`の出力
3. ブラウザのコンソールエラー
4. バックエンドサーバーのログ
