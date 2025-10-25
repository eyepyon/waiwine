# LiveKit Agents翻訳機能セットアップガイド

このドキュメントでは、LiveKit Agentsを使用したリアルタイム翻訳機能の設定方法を説明します。

## 概要

LiveKit Agentsを使用することで、以下の機能が統合されます：

- **Speech-to-Text (STT)**: Deepgram APIを使用した音声認識
- **Translation**: OpenAI GPT-4を使用した翻訳
- **Text-to-Speech (TTS)**: OpenAI TTSを使用した音声合成

Google Cloud APIの代わりに、LiveKitのエコシステム内で全て完結します。

## 必要なAPIキー

### 1. Deepgram API（Speech-to-Text用）

1. [Deepgram Console](https://console.deepgram.com/)にアクセス
2. アカウントを作成（無料プランあり）
3. 新しいプロジェクトを作成
4. APIキーを生成
5. `.env`ファイルに設定：

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

**料金**: 
- 無料プラン: $200分のクレジット
- 従量課金: $0.0043/分（Nova-2モデル）

### 2. OpenAI API（Translation & TTS用）

1. [OpenAI Platform](https://platform.openai.com/)にアクセス
2. アカウントを作成
3. APIキーを生成
4. `.env`ファイルに設定：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**料金**:
- GPT-4 Turbo: $0.01/1K tokens (入力), $0.03/1K tokens (出力)
- TTS: $0.015/1K文字

## インストール

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

これにより、以下がインストールされます：
- `livekit-agents`: LiveKit Agentsフレームワーク
- `livekit-plugins-deepgram`: Deepgram STTプラグイン
- `livekit-plugins-openai`: OpenAI LLM & TTSプラグイン
- `livekit-plugins-silero`: VAD (Voice Activity Detection)

### 2. 環境変数の設定

`.env`ファイルに以下を追加：

```env
# LiveKit Configuration
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.com

# LiveKit Agents - AI Services
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 使い方

### バックエンドサーバーの起動

```bash
cd backend
python api_app.py
```

### 翻訳セッションの開始

フロントエンドから以下のAPIを呼び出します：

```javascript
// 翻訳セッションを開始
const response = await fetch('http://localhost:8000/api/translation/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    room_name: 'wine-123',
    source_language: 'ja',
    target_languages: ['en', 'ko']
  })
});
```

### サポートされている言語

- 日本語 (ja)
- 英語 (en)
- 韓国語 (ko)
- 中国語 (zh)
- スペイン語 (es)
- フランス語 (fr)
- ドイツ語 (de)

## アーキテクチャ

```
┌─────────────┐
│   User A    │ (日本語)
│  (Browser)  │
└──────┬──────┘
       │ Audio Stream
       ▼
┌─────────────────────────────────┐
│      LiveKit Room               │
│  ┌──────────────────────────┐  │
│  │  LiveKit Agent           │  │
│  │  ┌────────────────────┐  │  │
│  │  │ 1. STT (Deepgram)  │  │  │
│  │  │    音声 → テキスト    │  │  │
│  │  └────────┬───────────┘  │  │
│  │           │              │  │
│  │  ┌────────▼───────────┐  │  │
│  │  │ 2. Translation     │  │  │
│  │  │    (OpenAI GPT-4)  │  │  │
│  │  │    日本語 → 英語    │  │  │
│  │  └────────┬───────────┘  │  │
│  │           │              │  │
│  │  ┌────────▼───────────┐  │  │
│  │  │ 3. TTS (OpenAI)    │  │  │
│  │  │    テキスト → 音声   │  │  │
│  │  └────────────────────┘  │  │
│  └──────────────────────────┘  │
└─────────────┬───────────────────┘
              │ Translated Audio
              ▼
       ┌─────────────┐
       │   User B    │ (英語)
       │  (Browser)  │
       └─────────────┘
```

## 機能

### リアルタイム音声認識
- Deepgram Nova-2モデルを使用
- 低レイテンシー（~300ms）
- 高精度な音声認識
- 句読点の自動挿入

### 高品質な翻訳
- OpenAI GPT-4 Turboを使用
- コンテキストを理解した翻訳
- ワイン用語の正確な翻訳
- 会話のトーンを維持

### 自然な音声合成
- OpenAI TTSを使用
- 複数の音声プロファイル
- 調整可能な速度
- 自然な発音

## トラブルシューティング

### "Deepgram API key not found"エラー

`.env`ファイルに`DEEPGRAM_API_KEY`が正しく設定されているか確認してください。

### "OpenAI API key not found"エラー

`.env`ファイルに`OPENAI_API_KEY`が正しく設定されているか確認してください。

### 音声が認識されない

1. マイクの権限が許可されているか確認
2. LiveKitルームに正しく接続されているか確認
3. ブラウザのコンソールでエラーを確認

### 翻訳が遅い

1. インターネット接続を確認
2. OpenAI APIの利用制限を確認
3. より高速なモデル（gpt-3.5-turbo）への切り替えを検討

## コスト見積もり

### 1時間のビデオチャット（2人）の場合

**Speech-to-Text (Deepgram)**:
- 60分 × $0.0043/分 = $0.26

**Translation (OpenAI GPT-4)**:
- 約10,000トークン × $0.01/1K = $0.10

**Text-to-Speech (OpenAI)**:
- 約5,000文字 × $0.015/1K = $0.075

**合計**: 約$0.44/時間/人

## 従来のGoogle Cloud APIとの比較

| 機能 | Google Cloud | LiveKit Agents |
|------|--------------|----------------|
| STT | Google Speech-to-Text | Deepgram |
| Translation | Google Translate | OpenAI GPT-4 |
| TTS | Google Text-to-Speech | OpenAI TTS |
| 統合 | 個別のAPI | 統合されたエージェント |
| レイテンシー | 中程度 | 低い |
| コスト | 中程度 | やや高い |
| 翻訳品質 | 良い | 優れている |

## 次のステップ

1. APIキーを取得して`.env`に設定
2. バックエンドサーバーを起動
3. フロントエンドから翻訳機能をテスト
4. 必要に応じて音声プロファイルや速度を調整

## サポート

問題が発生した場合は、以下を確認してください：

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Deepgram Documentation](https://developers.deepgram.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
