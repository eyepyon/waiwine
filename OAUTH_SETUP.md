# OAuth設定ガイド

このドキュメントでは、Wai WineアプリケーションでOAuth認証を設定する方法を説明します。

## Google OAuth 2.0の設定

### 1. Google Cloud Consoleでプロジェクトを作成

1. [Google Cloud Console](https://console.developers.google.com/)にアクセス
2. 新しいプロジェクトを作成、または既存のプロジェクトを選択

### 2. OAuth同意画面の設定

1. 左メニューから「APIとサービス」→「OAuth同意画面」を選択
2. ユーザータイプを選択（テスト用は「外部」でOK）
3. アプリ情報を入力：
   - アプリ名: `Wai Wine`
   - ユーザーサポートメール: あなたのメールアドレス
   - デベロッパーの連絡先情報: あなたのメールアドレス
4. スコープの設定：
   - `openid`
   - `email`
   - `profile`
5. 保存して続行

### 3. 認証情報の作成

1. 左メニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuthクライアントID」をクリック
3. アプリケーションの種類：「ウェブアプリケーション」を選択
4. 名前: `Wai Wine Web Client`
5. 承認済みのリダイレクトURIを追加：
   ```
   http://localhost:8000/api/auth/google/callback
   ```
   本番環境の場合は、実際のドメインも追加：
   ```
   https://yourdomain.com/api/auth/google/callback
   ```
6. 「作成」をクリック

### 4. 認証情報を.envファイルに設定

作成されたクライアントIDとクライアントシークレットをコピーして、`.env`ファイルに設定：

```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwx
```

## Twitter/X OAuth 2.0の設定（オプション）

### 1. Twitter Developer Portalでアプリを作成

1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)にアクセス
2. 「Projects & Apps」→「Create App」をクリック
3. アプリ名を入力して作成

### 2. OAuth 2.0設定

1. アプリの設定画面で「OAuth 2.0」セクションを開く
2. 「Type of App」: `Web App`
3. 「Callback URI」を追加：
   ```
   http://localhost:8000/api/auth/twitter/callback
   ```
4. 「Website URL」を入力（必須）

### 3. 認証情報を取得

1. 「Keys and tokens」タブを開く
2. Client IDとClient Secretを生成
3. `.env`ファイルに設定：

```env
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
```

## LINE Loginの設定（オプション）

### 1. LINE Developersでチャネルを作成

1. [LINE Developers Console](https://developers.line.biz/console/)にアクセス
2. プロバイダーを作成（または既存のものを選択）
3. 「新規チャネル作成」→「LINEログイン」を選択
4. チャネル情報を入力：
   - チャネル名: `Wai Wine`
   - チャネル説明: ワインラベル認識ビデオチャットアプリ

### 2. コールバックURLの設定

1. チャネル基本設定で「コールバックURL」を設定：
   ```
   http://localhost:8000/api/auth/line/callback
   ```

### 3. 認証情報を取得

1. チャネル基本設定から「Channel ID」と「Channel Secret」をコピー
2. `.env`ファイルに設定：

```env
LINE_CLIENT_ID=1234567890
LINE_CLIENT_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

## セキュリティキーの生成

開発環境用のランダムなセキュリティキーを生成：

```bash
# Pythonで生成
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

生成されたキーを`.env`に設定：

```env
SECRET_KEY=生成されたキー1
JWT_SECRET_KEY=生成されたキー2
```

## 設定の確認

1. `.env`ファイルを保存
2. バックエンドサーバーを再起動：
   ```bash
   cd backend
   python app.py
   ```
3. ブラウザで`http://localhost:3000`にアクセス
4. ログインボタンをクリックして、設定したOAuthプロバイダーが表示されることを確認

## トラブルシューティング

### "Failed to get google auth URL"エラー

- `.env`ファイルに`GOOGLE_CLIENT_ID`と`GOOGLE_CLIENT_SECRET`が正しく設定されているか確認
- バックエンドサーバーを再起動したか確認
- Google Cloud Consoleで認証情報が有効になっているか確認

### リダイレクトURIのエラー

- Google Cloud Consoleの「承認済みのリダイレクトURI」に正確なURLが登録されているか確認
- プロトコル（http/https）、ポート番号、パスが完全に一致しているか確認

### 本番環境への移行

本番環境では以下を変更してください：

```env
DEBUG=False
ENVIRONMENT=production
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

また、各OAuthプロバイダーのコールバックURLも本番環境のURLに更新してください。
