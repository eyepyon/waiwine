# Design Document

## Overview

ワインラベル認識機能を持つLiveKitビデオチャットアプリケーションの設計。ユーザーはカメラでワインラベルを撮影し、AI画像認識により銘柄を特定、同じワインを飲んでいる他のユーザーとリアルタイムビデオチャットを楽しめる。複数のソーシャルログインプラットフォームをサポートし、シームレスなユーザー体験を提供する。

## Architecture

### システム全体構成

```mermaid
graph TB
    subgraph "Frontend (Vue.js)"
        A[Camera Interface]
        B[Login Interface]
        C[Wine Room Interface]
        D[User Settings]
    end
    
    subgraph "Backend (Python/Streamlit)"
        E[Authentication Service]
        F[Wine Recognition Service]
        G[Room Management Service]
        H[User Management Service]
    end
    
    subgraph "External Services"
        I[Google Vision API]
        J[Wine Database API]
        K[LiveKit Server]
        L[OAuth Providers]
    end
    
    subgraph "Database"
        M[User Profiles]
        N[Wine Data]
        O[Room Sessions]
    end
    
    A --> F
    B --> E
    C --> G
    E --> L
    F --> I
    F --> J
    G --> K
    E --> M
    F --> N
    G --> O
```

### 技術スタック

**フロントエンド:**
- Vue.js 3 (Composition API)
- Vue I18n (国際化)
- LiveKit Client SDK
- Camera API (WebRTC)
- Vite (ビルドツール)

**バックエンド:**
- Python 3.9+
- Streamlit (メインアプリケーション)
- FastAPI (API エンドポイント)
- SQLAlchemy (ORM)
- LiveKit Python SDK
- Babel (国際化サポート)

**外部サービス:**
- Google Vision API (画像認識)
- Google Cloud Translation API (リアルタイム翻訳)
- Google Cloud Speech-to-Text API (音声認識)
- Google Cloud Text-to-Speech API (音声合成)
- OpenFoodFacts API / Wine.com API (ワイン情報)
- LiveKit Cloud (ビデオチャット)
- OAuth プロバイダー (Google, Twitter, LINE)

**データベース:**
- SQLite (開発環境)
- PostgreSQL (本番環境推奨)

## Components and Interfaces

### 1. Authentication Service

**責任:**
- 複数のOAuthプロバイダーとの認証処理
- ユーザーセッション管理
- アカウントリンク機能

**主要メソッド:**
```python
class AuthenticationService:
    def authenticate_with_provider(provider: str, auth_code: str) -> User
    def link_provider_to_user(user_id: str, provider: str, provider_data: dict) -> bool
    def get_user_by_provider_id(provider: str, provider_id: str) -> User
    def create_user_session(user: User) -> str
    def validate_session(session_token: str) -> User
```

**OAuth設定:**
```python
# config.py - 環境変数の一元管理
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LiveKit設定
    LIVEKIT_API_KEY = os.getenv('LIVEKIT_API_KEY')
    LIVEKIT_API_SECRET = os.getenv('LIVEKIT_API_SECRET')
    LIVEKIT_URL = os.getenv('LIVEKIT_URL')
    
    # OAuth プロバイダー設定
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    TWITTER_CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
    TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    
    LINE_CLIENT_ID = os.getenv('LINE_CLIENT_ID')
    LINE_CLIENT_SECRET = os.getenv('LINE_CLIENT_SECRET')
    
    # 画像認識API設定
    GOOGLE_VISION_API_KEY = os.getenv('GOOGLE_VISION_API_KEY')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # ワインデータベースAPI設定
    WINE_API_KEY = os.getenv('WINE_API_KEY')
    WINE_API_BASE_URL = os.getenv('WINE_API_BASE_URL', 'https://api.wine.com')
    
    # セキュリティ設定
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # データベース設定
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///wine_chat.db')
    
    # アプリケーション設定
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

OAUTH_PROVIDERS = {
    'google': {
        'client_id': Config.GOOGLE_CLIENT_ID,
        'client_secret': Config.GOOGLE_CLIENT_SECRET,
        'scope': ['openid', 'email', 'profile'],
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo'
    },
    'twitter': {
        'client_id': Config.TWITTER_CLIENT_ID,
        'client_secret': Config.TWITTER_CLIENT_SECRET,
        'bearer_token': Config.TWITTER_BEARER_TOKEN,
        'scope': ['tweet.read', 'users.read'],
        'authorize_url': 'https://twitter.com/i/oauth2/authorize',
        'token_url': 'https://api.twitter.com/2/oauth2/token',
        'userinfo_url': 'https://api.twitter.com/2/users/me'
    },
    'line': {
        'client_id': Config.LINE_CLIENT_ID,
        'client_secret': Config.LINE_CLIENT_SECRET,
        'scope': ['profile', 'openid'],
        'authorize_url': 'https://access.line.me/oauth2/v2.1/authorize',
        'token_url': 'https://api.line.me/oauth2/v2.1/token',
        'userinfo_url': 'https://api.line.me/v2/profile'
    }
}
```

### 2. Wine Recognition Service

**責任:**
- 画像からワインラベルの検出と認識
- ワイン情報の取得と管理
- 認識精度の向上

**主要メソッド:**
```python
class WineRecognitionService:
    def recognize_wine_from_image(image_data: bytes) -> WineRecognitionResult
    def get_wine_info(wine_id: str) -> WineInfo
    def search_wines_by_text(query: str) -> List[WineInfo]
    def update_recognition_feedback(wine_id: str, user_feedback: bool) -> None
```

**認識フロー:**
1. 画像前処理（リサイズ、ノイズ除去）
2. Google Vision APIでテキスト抽出
3. 抽出テキストでワインデータベース検索
4. 信頼度スコア計算
5. 結果返却

### 3. Room Management Service

**責任:**
- ワイン別ルームの作成と管理
- LiveKitトークン生成
- 参加者管理
- リアルタイム翻訳設定管理

**主要メソッド:**
```python
class RoomManagementService:
    def create_or_join_wine_room(wine_id: str, user_id: str) -> RoomInfo
    def generate_livekit_token(user_id: str, room_name: str) -> str
    def get_room_participants(room_name: str) -> List[Participant]
    def leave_room(user_id: str, room_name: str) -> None
    def get_translation_settings(user_id: str) -> TranslationSettings
    def update_translation_settings(user_id: str, settings: TranslationSettings) -> bool
```

### 6. Real-time Translation Service

**責任:**
- 音声のリアルタイム認識と翻訳
- 文字翻訳の表示管理
- 音声翻訳の合成と配信

**主要メソッド:**
```python
class RealtimeTranslationService:
    def start_speech_recognition(user_id: str, audio_stream) -> None
    def translate_text(text: str, source_lang: str, target_lang: str) -> str
    def synthesize_speech(text: str, target_lang: str, voice_id: str) -> bytes
    def get_available_voices(language: str) -> List[Voice]
    def process_audio_translation(audio_data: bytes, user_settings: TranslationSettings) -> TranslationResult
```

**翻訳フロー:**
```mermaid
sequenceDiagram
    participant U1 as User 1 (日本語)
    participant TS as Translation Service
    participant U2 as User 2 (英語)
    
    U1->>TS: 音声データ送信
    TS->>TS: 音声認識 (日本語→テキスト)
    TS->>TS: テキスト翻訳 (日本語→英語)
    
    par 文字翻訳
        TS->>U2: 翻訳テキスト表示
    and 音声翻訳
        TS->>TS: 音声合成 (英語音声)
        TS->>U2: 翻訳音声配信
    end
```

### 4. Camera Interface (Frontend)

**責任:**
- カメラアクセスと制御
- 画像キャプチャ
- プレビュー表示

**Vue.js コンポーネント:**
```vue
<template>
  <div class="camera-interface">
    <video ref="videoElement" autoplay playsinline></video>
    <canvas ref="canvasElement" style="display: none;"></canvas>
    <button @click="capturePhoto" class="capture-btn">
      {{ $t('camera.capture') }}
    </button>
  </div>
</template>

<script>
export default {
  methods: {
    async initCamera() {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      })
      this.$refs.videoElement.srcObject = stream
    },
    
    capturePhoto() {
      const canvas = this.$refs.canvasElement
      const video = this.$refs.videoElement
      canvas.getContext('2d').drawImage(video, 0, 0)
      return canvas.toBlob(blob => this.processWineImage(blob))
    }
  }
}
</script>
```

### 5. Internationalization Service

**責任:**
- ユーザーの言語設定に基づくUI言語切り替え
- 多言語コンテンツの管理
- 動的言語変更

**主要メソッド:**
```python
class InternationalizationService:
    def get_user_language(user_id: str) -> str
    def set_user_language(user_id: str, language: str) -> bool
    def get_translated_content(key: str, language: str) -> str
    def get_supported_languages() -> List[Language]
```

**Vue I18n 設定:**
```javascript
// i18n/index.js
import { createI18n } from 'vue-i18n'

const messages = {
  ja: {
    camera: {
      capture: '撮影',
      permission_denied: 'カメラへのアクセスが拒否されました'
    },
    wine: {
      recognition_loading: 'ワインを認識中...',
      not_found: 'ワインが見つかりませんでした'
    },
    room: {
      join: 'ルームに参加',
      participants: '参加者'
    }
  },
  en: {
    camera: {
      capture: 'Capture',
      permission_denied: 'Camera access denied'
    },
    wine: {
      recognition_loading: 'Recognizing wine...',
      not_found: 'Wine not found'
    },
    room: {
      join: 'Join Room',
      participants: 'Participants'
    }
  },
  ko: {
    camera: {
      capture: '촬영',
      permission_denied: '카메라 접근이 거부되었습니다'
    },
    wine: {
      recognition_loading: '와인 인식 중...',
      not_found: '와인을 찾을 수 없습니다'
    },
    room: {
      join: '룸 참가',
      participants: '참가자'
    }
  }
}

export default createI18n({
  locale: 'ja', // デフォルト言語
  fallbackLocale: 'en',
  messages
})
```

## Data Models

### User Model
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    main_language = Column(String, default='ja')  # UI言語設定
    profile_image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth プロバイダー情報
    oauth_providers = relationship("OAuthProvider", back_populates="user")
    
    def get_localized_content(self, content_key: str) -> str:
        """ユーザーの言語設定に基づいてローカライズされたコンテンツを取得"""
        return get_translation(content_key, self.main_language)
```

### OAuth Provider Model
```python
class OAuthProvider(Base):
    __tablename__ = 'oauth_providers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    provider_name = Column(String)  # 'google', 'twitter', 'line'
    provider_user_id = Column(String)
    provider_email = Column(String)
    linked_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="oauth_providers")
```

### Wine Model
```python
class Wine(Base):
    __tablename__ = 'wines'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    vintage = Column(Integer)
    region = Column(String)
    producer = Column(String)
    wine_type = Column(String)  # 'red', 'white', 'sparkling', etc.
    alcohol_content = Column(Float)
    image_url = Column(String)
    
    # 多言語対応
    name_translations = Column(JSON)  # {'ja': '日本語名', 'en': 'English name'}
    tasting_notes_translations = Column(JSON)  # 多言語テイスティングノート
    region_translations = Column(JSON)  # 地域名の多言語対応
    
    # 認識関連
    recognition_keywords = Column(JSON)  # 認識用キーワード
    recognition_count = Column(Integer, default=0)
    
    def get_localized_name(self, language: str) -> str:
        """指定言語でのワイン名を取得"""
        return self.name_translations.get(language, self.name)
    
    def get_localized_tasting_notes(self, language: str) -> str:
        """指定言語でのテイスティングノートを取得"""
        return self.tasting_notes_translations.get(language, '')
```

### Room Session Model
```python
class RoomSession(Base):
    __tablename__ = 'room_sessions'
    
    id = Column(String, primary_key=True)
    wine_id = Column(String, ForeignKey('wines.id'))
    room_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    active_participants = Column(Integer, default=0)
    
    wine = relationship("Wine")

### Translation Settings Model
```python
class TranslationSettings(Base):
    __tablename__ = 'translation_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    
    # 翻訳機能の有効/無効
    text_translation_enabled = Column(Boolean, default=True)
    voice_translation_enabled = Column(Boolean, default=False)
    
    # 音声設定
    original_voice_volume = Column(Float, default=0.3)  # 元の音声のボリューム (0.0-1.0)
    translated_voice_volume = Column(Float, default=0.8)  # 翻訳音声のボリューム
    
    # 音声の種類設定
    preferred_voice_id = Column(String)  # ユーザーが選択した音声ID
    voice_speed = Column(Float, default=1.0)  # 音声の速度
    
    # 表示設定
    subtitle_position = Column(String, default='bottom')  # 'top', 'bottom', 'overlay'
    subtitle_font_size = Column(Integer, default=16)
    subtitle_background_opacity = Column(Float, default=0.7)
    
    user = relationship("User")

### Voice Profile Model
```python
class VoiceProfile(Base):
    __tablename__ = 'voice_profiles'
    
    id = Column(String, primary_key=True)
    language = Column(String)  # 'ja', 'en', 'ko', etc.
    voice_name = Column(String)  # 'ja-JP-Wavenet-A'
    gender = Column(String)  # 'male', 'female', 'neutral'
    description = Column(String)  # '若い女性の声', 'Deep male voice'
    sample_audio_url = Column(String)  # サンプル音声のURL
    
    # 言語別の説明
    description_translations = Column(JSON)
```

## Error Handling

### 認証エラー
- OAuth認証失敗時のリトライ機能
- プロバイダー別エラーメッセージ
- セッション期限切れの自動処理

### 画像認識エラー
- 認識失敗時の手動選択オプション
- 低品質画像の再撮影促進
- オフライン時のキャッシュ機能

### ビデオチャットエラー
- LiveKit接続失敗時の再接続
- メディアデバイスアクセス拒否の処理
- ネットワーク不安定時の品質調整

## Testing Strategy

### ユニットテスト
- 各サービスクラスの個別機能テスト
- モックを使用した外部API依存の分離
- データモデルのバリデーションテスト

### 統合テスト
- OAuth認証フローの端到端テスト
- 画像認識パイプラインのテスト
- LiveKit統合のテスト

### E2Eテスト
- ユーザージャーニー全体のテスト
- 複数ブラウザでの同時接続テスト
- モバイルデバイスでのカメラ機能テスト

### パフォーマンステスト
- 画像認識の応答時間測定
- 同時接続ユーザー数の負荷テスト
- データベースクエリの最適化検証

## Security Considerations

### 認証セキュリティ
- OAuth state パラメータによるCSRF防止
- セッショントークンの適切な有効期限設定
- プロバイダー別のスコープ最小化

### 画像処理セキュリティ
- アップロード画像のサイズ制限
- 悪意のあるファイル形式の検証
- 個人情報を含む画像の自動検出

### データ保護
- 個人情報の暗号化保存
- GDPR準拠のデータ削除機能
- アクセスログの監査機能
### Lan
guage Translation Model
```python
class Translation(Base):
    __tablename__ = 'translations'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, index=True)  # 'wine.type.red', 'ui.button.join'
    language = Column(String, index=True)  # 'ja', 'en', 'ko', etc.
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('key', 'language'),)
```

## Language Switching Flow

### フロントエンド言語切り替え
1. ユーザーログイン時にmain_languageを取得
2. Vue I18nのlocaleを動的に設定
3. 全てのUIコンポーネントが自動的に切り替わる
4. ユーザーが言語を変更した場合、即座に反映

### バックエンド多言語対応
1. Streamlitアプリでユーザーの言語設定を読み込み
2. 表示テキストを動的に翻訳
3. ワイン情報も言語に応じて表示

**言語切り替えコンポーネント例:**
```vue
<template>
  <select @change="changeLanguage" v-model="currentLanguage">
    <option value="ja">日本語</option>
    <option value="en">English</option>
    <option value="ko">한국어</option>
    <option value="zh">中文</option>
    <option value="es">Español</option>
    <option value="fr">Français</option>
    <option value="de">Deutsch</option>
  </select>
</template>

<script>
export default {
  data() {
    return {
      currentLanguage: this.$i18n.locale
    }
  },
  methods: {
    async changeLanguage(event) {
      const newLanguage = event.target.value
      this.$i18n.locale = newLanguage
      
      // バックエンドにも言語設定を保存
      await this.updateUserLanguage(newLanguage)
      
      // ページ全体を再レンダリング
      this.$forceUpdate()
    },
    
    async updateUserLanguage(language) {
      // API呼び出しでユーザーの言語設定を更新
      await fetch('/api/user/language', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language })
      })
    }
  }
}
</script>
```

## Environment Variables Configuration

### .env ファイル構成

```env
# =================================
# LiveKit Configuration
# =================================
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here
LIVEKIT_URL=wss://your-livekit-server.com

# =================================
# OAuth Provider Configuration
# =================================

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Twitter/X OAuth 2.0
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# LINE Login
LINE_CLIENT_ID=your_line_channel_id
LINE_CLIENT_SECRET=your_line_channel_secret

# =================================
# AI/ML Service Configuration
# =================================

# Google Vision API
GOOGLE_VISION_API_KEY=your_google_vision_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Google Translation APIs
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
GOOGLE_SPEECH_TO_TEXT_API_KEY=your_google_speech_api_key
GOOGLE_TEXT_TO_SPEECH_API_KEY=your_google_tts_api_key

# Wine Database API
WINE_API_KEY=your_wine_api_key
WINE_API_BASE_URL=https://api.wine.com

# =================================
# Security Configuration
# =================================
SECRET_KEY=your_super_secret_key_for_sessions
JWT_SECRET_KEY=your_jwt_secret_key_for_tokens

# =================================
# Database Configuration
# =================================
DATABASE_URL=sqlite:///wine_chat.db
# For production: postgresql://user:password@localhost/wine_chat

# =================================
# Application Configuration
# =================================
DEBUG=False
ENVIRONMENT=production
# Options: development, staging, production

# =================================
# Optional: Additional Services
# =================================

# Redis for caching (optional)
REDIS_URL=redis://localhost:6379/0

# Email service (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Monitoring (optional)
SENTRY_DSN=your_sentry_dsn_here
```

### 環境変数検証

```python
# config_validator.py
import os
import sys
from typing import List, Optional

class ConfigValidator:
    """環境変数の存在と有効性を検証"""
    
    REQUIRED_VARS = [
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET', 
        'LIVEKIT_URL',
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    OAUTH_REQUIRED_VARS = {
        'google': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'],
        'twitter': ['TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET'],
        'line': ['LINE_CLIENT_ID', 'LINE_CLIENT_SECRET']
    }
    
    @classmethod
    def validate_required_vars(cls) -> List[str]:
        """必須環境変数の存在確認"""
        missing_vars = []
        
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        return missing_vars
    
    @classmethod
    def validate_oauth_providers(cls) -> dict:
        """OAuth プロバイダー設定の確認"""
        provider_status = {}
        
        for provider, vars_needed in cls.OAUTH_REQUIRED_VARS.items():
            missing = [var for var in vars_needed if not os.getenv(var)]
            provider_status[provider] = {
                'enabled': len(missing) == 0,
                'missing_vars': missing
            }
        
        return provider_status
    
    @classmethod
    def validate_all(cls) -> bool:
        """全体的な設定検証"""
        missing_required = cls.validate_required_vars()
        oauth_status = cls.validate_oauth_providers()
        
        if missing_required:
            print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
            return False
        
        enabled_providers = [p for p, status in oauth_status.items() if status['enabled']]
        
        if not enabled_providers:
            print("❌ No OAuth providers are properly configured")
            return False
        
        print(f"✅ Configuration valid. Enabled OAuth providers: {', '.join(enabled_providers)}")
        return True

# アプリケーション起動時の検証
if __name__ == "__main__":
    if not ConfigValidator.validate_all():
        sys.exit(1)
```

### 開発環境用 .env.example

```env
# Copy this file to .env and fill in your actual values

# =================================
# LiveKit Configuration
# =================================
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret  
LIVEKIT_URL=ws://localhost:7880

# =================================
# OAuth Provider Configuration
# =================================
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

LINE_CLIENT_ID=your_line_channel_id
LINE_CLIENT_SECRET=your_line_channel_secret

# =================================
# AI/ML Service Configuration  
# =================================
GOOGLE_VISION_API_KEY=your_google_vision_api_key
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

WINE_API_KEY=demo_key
WINE_API_BASE_URL=https://api.wine.com

# =================================
# Security Configuration
# =================================
SECRET_KEY=dev_secret_key_change_in_production
JWT_SECRET_KEY=dev_jwt_secret_change_in_production

# =================================
# Database Configuration
# =================================
DATABASE_URL=sqlite:///wine_chat_dev.db

# =================================
# Application Configuration
# =================================
DEBUG=True
ENVIRONMENT=development
```

## Real-time Translation Implementation

### フロントエンド翻訳コンポーネント

```vue
<template>
  <div class="translation-overlay">
    <!-- 文字翻訳表示 -->
    <div 
      v-if="translationSettings.textTranslationEnabled && currentTranslation"
      :class="['subtitle-overlay', `position-${translationSettings.subtitlePosition}`]"
      :style="subtitleStyles"
    >
      <div class="original-text">{{ currentTranslation.originalText }}</div>
      <div class="translated-text">{{ currentTranslation.translatedText }}</div>
    </div>
    
    <!-- 翻訳設定パネル -->
    <div v-if="showSettings" class="translation-settings">
      <h3>{{ $t('translation.settings') }}</h3>
      
      <!-- 文字翻訳設定 -->
      <div class="setting-group">
        <label>
          <input 
            type="checkbox" 
            v-model="translationSettings.textTranslationEnabled"
            @change="updateSettings"
          />
          {{ $t('translation.enable_text') }}
        </label>
      </div>
      
      <!-- 音声翻訳設定 -->
      <div class="setting-group">
        <label>
          <input 
            type="checkbox" 
            v-model="translationSettings.voiceTranslationEnabled"
            @change="updateSettings"
          />
          {{ $t('translation.enable_voice') }}
        </label>
      </div>
      
      <!-- 音声ボリューム設定 -->
      <div v-if="translationSettings.voiceTranslationEnabled" class="setting-group">
        <label>{{ $t('translation.original_volume') }}</label>
        <input 
          type="range" 
          min="0" 
          max="1" 
          step="0.1"
          v-model="translationSettings.originalVoiceVolume"
          @change="updateSettings"
        />
        
        <label>{{ $t('translation.translated_volume') }}</label>
        <input 
          type="range" 
          min="0" 
          max="1" 
          step="0.1"
          v-model="translationSettings.translatedVoiceVolume"
          @change="updateSettings"
        />
      </div>
      
      <!-- 音声選択 -->
      <div v-if="translationSettings.voiceTranslationEnabled" class="setting-group">
        <label>{{ $t('translation.voice_selection') }}</label>
        <select v-model="translationSettings.preferredVoiceId" @change="updateSettings">
          <option 
            v-for="voice in availableVoices" 
            :key="voice.id" 
            :value="voice.id"
          >
            {{ voice.description }}
          </option>
        </select>
        
        <!-- 音声プレビュー -->
        <button @click="playVoicePreview" class="preview-btn">
          {{ $t('translation.preview_voice') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TranslationOverlay',
  
  data() {
    return {
      translationSettings: {
        textTranslationEnabled: true,
        voiceTranslationEnabled: false,
        originalVoiceVolume: 0.3,
        translatedVoiceVolume: 0.8,
        preferredVoiceId: null,
        subtitlePosition: 'bottom'
      },
      currentTranslation: null,
      availableVoices: [],
      showSettings: false,
      audioContext: null,
      translationWebSocket: null
    }
  },
  
  computed: {
    subtitleStyles() {
      return {
        fontSize: `${this.translationSettings.subtitleFontSize}px`,
        backgroundColor: `rgba(0, 0, 0, ${this.translationSettings.subtitleBackgroundOpacity})`
      }
    }
  },
  
  async mounted() {
    await this.initializeTranslation()
    await this.loadAvailableVoices()
  },
  
  methods: {
    async initializeTranslation() {
      // WebSocket接続でリアルタイム翻訳
      this.translationWebSocket = new WebSocket('ws://localhost:8000/ws/translation')
      
      this.translationWebSocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'text_translation') {
          this.currentTranslation = {
            originalText: data.original,
            translatedText: data.translated,
            speakerId: data.speaker_id
          }
          
          // 3秒後に字幕を消す
          setTimeout(() => {
            this.currentTranslation = null
          }, 3000)
        }
        
        if (data.type === 'voice_translation') {
          this.playTranslatedAudio(data.audio_data, data.speaker_id)
        }
      }
      
      // 音声認識の開始
      if (this.translationSettings.textTranslationEnabled || 
          this.translationSettings.voiceTranslationEnabled) {
        await this.startSpeechRecognition()
      }
    },
    
    async startSpeechRecognition() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        
        // Web Audio APIで音声データを処理
        this.audioContext = new AudioContext()
        const source = this.audioContext.createMediaStreamSource(stream)
        const processor = this.audioContext.createScriptProcessor(4096, 1, 1)
        
        processor.onaudioprocess = (event) => {
          const audioData = event.inputBuffer.getChannelData(0)
          
          // 音声データをWebSocketで送信
          if (this.translationWebSocket.readyState === WebSocket.OPEN) {
            this.translationWebSocket.send(JSON.stringify({
              type: 'audio_data',
              data: Array.from(audioData),
              user_language: this.$i18n.locale,
              settings: this.translationSettings
            }))
          }
        }
        
        source.connect(processor)
        processor.connect(this.audioContext.destination)
        
      } catch (error) {
        console.error('音声認識の開始に失敗:', error)
      }
    },
    
    async playTranslatedAudio(audioData, speakerId) {
      if (!this.translationSettings.voiceTranslationEnabled) return
      
      try {
        // Base64音声データをデコード
        const audioBuffer = this.base64ToArrayBuffer(audioData)
        const decodedAudio = await this.audioContext.decodeAudioData(audioBuffer)
        
        // 音声を再生
        const source = this.audioContext.createBufferSource()
        const gainNode = this.audioContext.createGain()
        
        source.buffer = decodedAudio
        gainNode.gain.value = this.translationSettings.translatedVoiceVolume
        
        source.connect(gainNode)
        gainNode.connect(this.audioContext.destination)
        
        source.start()
        
        // 元の音声のボリュームを下げる（他の参加者の音声）
        this.adjustOriginalAudioVolume(speakerId, this.translationSettings.originalVoiceVolume)
        
      } catch (error) {
        console.error('翻訳音声の再生に失敗:', error)
      }
    },
    
    adjustOriginalAudioVolume(speakerId, volume) {
      // LiveKitの音声トラックのボリュームを調整
      const audioTrack = this.getAudioTrackBySpeaker(speakerId)
      if (audioTrack) {
        audioTrack.setVolume(volume)
      }
    },
    
    async loadAvailableVoices() {
      try {
        const response = await fetch(`/api/voices/${this.$i18n.locale}`)
        this.availableVoices = await response.json()
        
        // デフォルト音声を設定
        if (this.availableVoices.length > 0 && !this.translationSettings.preferredVoiceId) {
          this.translationSettings.preferredVoiceId = this.availableVoices[0].id
        }
      } catch (error) {
        console.error('音声リストの取得に失敗:', error)
      }
    },
    
    async playVoicePreview() {
      const sampleText = this.$t('translation.sample_text')
      
      try {
        const response = await fetch('/api/tts/preview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: sampleText,
            voice_id: this.translationSettings.preferredVoiceId,
            language: this.$i18n.locale
          })
        })
        
        const audioBlob = await response.blob()
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)
        audio.play()
        
      } catch (error) {
        console.error('音声プレビューの再生に失敗:', error)
      }
    },
    
    async updateSettings() {
      // 設定をバックエンドに保存
      try {
        await fetch('/api/user/translation-settings', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.translationSettings)
        })
      } catch (error) {
        console.error('翻訳設定の保存に失敗:', error)
      }
    },
    
    base64ToArrayBuffer(base64) {
      const binaryString = window.atob(base64)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      return bytes.buffer
    }
  }
}
</script>

<style scoped>
.translation-overlay {
  position: relative;
  width: 100%;
  height: 100%;
}

.subtitle-overlay {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  text-align: center;
  max-width: 80%;
  z-index: 1000;
}

.subtitle-overlay.position-top {
  top: 20px;
}

.subtitle-overlay.position-bottom {
  bottom: 20px;
}

.original-text {
  font-size: 0.9em;
  opacity: 0.8;
  margin-bottom: 5px;
}

.translated-text {
  font-weight: bold;
}

.translation-settings {
  position: absolute;
  top: 10px;
  right: 10px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  z-index: 1001;
}

.setting-group {
  margin-bottom: 15px;
}

.setting-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
}

.setting-group input[type="range"] {
  width: 100%;
}

.preview-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
```

### バックエンド翻訳サービス

```python
# translation_service.py
import asyncio
import websockets
import json
import base64
from google.cloud import speech
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
import io

class RealtimeTranslationService:
    def __init__(self):
        self.speech_client = speech.SpeechClient()
        self.translate_client = translate.Client()
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # 音声認識の設定
        self.speech_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="ja-JP",  # 動的に変更
            enable_automatic_punctuation=True,
        )
    
    async def process_audio_stream(self, websocket, path):
        """WebSocket経由で音声データを処理"""
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data['type'] == 'audio_data':
                    await self.handle_audio_data(websocket, data)
                    
            except Exception as e:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))
    
    async def handle_audio_data(self, websocket, data):
        """音声データの処理と翻訳"""
        audio_data = data['data']
        user_language = data['user_language']
        settings = data['settings']
        
        # 音声認識
        recognized_text = await self.recognize_speech(audio_data, user_language)
        
        if recognized_text:
            # 他の参加者の言語に翻訳
            target_languages = await self.get_room_languages(websocket)
            
            for target_lang in target_languages:
                if target_lang != user_language:
                    # 文字翻訳
                    translated_text = self.translate_text(
                        recognized_text, user_language, target_lang
                    )
                    
                    await websocket.send(json.dumps({
                        'type': 'text_translation',
                        'original': recognized_text,
                        'translated': translated_text,
                        'source_language': user_language,
                        'target_language': target_lang,
                        'speaker_id': data.get('speaker_id')
                    }))
                    
                    # 音声翻訳（有効な場合）
                    if settings.get('voiceTranslationEnabled'):
                        audio_data = await self.synthesize_speech(
                            translated_text, target_lang, settings.get('preferredVoiceId')
                        )
                        
                        await websocket.send(json.dumps({
                            'type': 'voice_translation',
                            'audio_data': base64.b64encode(audio_data).decode(),
                            'speaker_id': data.get('speaker_id'),
                            'target_language': target_lang
                        }))
    
    async def recognize_speech(self, audio_data, language):
        """音声認識"""
        try:
            # 音声データをGoogle Speech-to-Textに送信
            audio = speech.RecognitionAudio(content=bytes(audio_data))
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=self.get_language_code(language),
                enable_automatic_punctuation=True,
            )
            
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                return response.results[0].alternatives[0].transcript
            
        except Exception as e:
            print(f"音声認識エラー: {e}")
            
        return None
    
    def translate_text(self, text, source_lang, target_lang):
        """テキスト翻訳"""
        try:
            result = self.translate_client.translate(
                text,
                source_language=source_lang,
                target_language=target_lang
            )
            return result['translatedText']
            
        except Exception as e:
            print(f"翻訳エラー: {e}")
            return text
    
    async def synthesize_speech(self, text, language, voice_id=None):
        """音声合成"""
        try:
            # 音声設定
            voice = texttospeech.VoiceSelectionParams(
                language_code=self.get_language_code(language),
                name=voice_id or self.get_default_voice(language)
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"音声合成エラー: {e}")
            return b''
    
    def get_language_code(self, language):
        """言語コードの変換"""
        language_codes = {
            'ja': 'ja-JP',
            'en': 'en-US',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE'
        }
        return language_codes.get(language, 'en-US')
    
    def get_default_voice(self, language):
        """デフォルト音声の取得"""
        default_voices = {
            'ja': 'ja-JP-Wavenet-A',
            'en': 'en-US-Wavenet-D',
            'ko': 'ko-KR-Wavenet-A',
            'zh': 'zh-CN-Wavenet-A',
            'es': 'es-ES-Wavenet-A',
            'fr': 'fr-FR-Wavenet-A',
            'de': 'de-DE-Wavenet-A'
        }
        return default_voices.get(language, 'en-US-Wavenet-D')

# WebSocketサーバーの起動
if __name__ == "__main__":
    translation_service = RealtimeTranslationService()
    
    start_server = websockets.serve(
        translation_service.process_audio_stream,
        "localhost",
        8000
    )
    
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
```