"""
Real-time translation service with speech recognition and text-to-speech using LiveKit.
"""
import asyncio
import json
import base64
import io
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from backend.models.user import User, TranslationSettings
from backend.models.database import get_db
from backend.config.settings import get_config

logger = logging.getLogger(__name__)
config = get_config()

# LiveKit Agents will handle STT, Translation, and TTS
# This service coordinates the translation workflow

class SpeechRecognitionService:
    """Google Speech-to-Text integration for real-time recognition."""
    
    def __init__(self):
        self.client = speech.SpeechClient()
        self.active_streams: Dict[str, Any] = {}
        
    def create_recognition_config(self, language_code: str = 'ja-JP') -> speech.RecognitionConfig:
        """Create speech recognition configuration."""
        return speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True,
            model='latest_long',
            use_enhanced=True
        )
    
    def create_streaming_config(self, language_code: str = 'ja-JP') -> speech.StreamingRecognitionConfig:
        """Create streaming recognition configuration."""
        config = self.create_recognition_config(language_code)
        return speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False
        )
    
    async def start_recognition_stream(self, user_id: str, language_code: str = 'ja-JP'):
        """Start a new speech recognition stream for a user."""
        try:
            streaming_config = self.create_streaming_config(language_code)
            
            # Create bidirectional stream
            audio_generator = self._audio_generator(user_id)
            requests = (speech.StreamingRecognizeRequest(audio_content=chunk)
                       for chunk in audio_generator)
            
            # Start streaming recognition
            responses = self.client.streaming_recognize(streaming_config, requests)
            
            self.active_streams[user_id] = {
                'responses': responses,
                'language': language_code,
                'audio_queue': asyncio.Queue()
            }
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to start recognition stream for user {user_id}: {e}")
            raise
    
    def _audio_generator(self, user_id: str):
        """Generate audio chunks from user's audio queue."""
        while user_id in self.active_streams:
            try:
                # Get audio data from queue (this would be populated by WebSocket)
                audio_queue = self.active_streams[user_id]['audio_queue']
                chunk = audio_queue.get_nowait()
                if chunk is None:  # Termination signal
                    break
                yield chunk
            except asyncio.QueueEmpty:
                continue
            except Exception as e:
                logger.error(f"Error in audio generator for user {user_id}: {e}")
                break
    
    async def add_audio_chunk(self, user_id: str, audio_data: bytes):
        """Add audio chunk to user's recognition stream."""
        if user_id in self.active_streams:
            await self.active_streams[user_id]['audio_queue'].put(audio_data)
    
    def stop_recognition_stream(self, user_id: str):
        """Stop recognition stream for a user."""
        if user_id in self.active_streams:
            # Send termination signal
            asyncio.create_task(
                self.active_streams[user_id]['audio_queue'].put(None)
            )
            del self.active_streams[user_id]
            logger.info(f"Stopped recognition stream for user {user_id}")

class TextTranslationService:
    """Google Translate API integration."""
    
    def __init__(self):
        self.client = translate.Client()
        self.supported_languages = {
            'ja': 'Japanese',
            'en': 'English', 
            'ko': 'Korean',
            'zh': 'Chinese',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict[str, Any]:
        """Translate text to target language."""
        try:
            result = self.client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            return {
                'translated_text': result['translatedText'],
                'detected_source_language': result.get('detectedSourceLanguage', source_language),
                'confidence': 1.0  # Google Translate doesn't provide confidence scores
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    def detect_language(self, text: str) -> str:
        """Detect the language of input text."""
        try:
            result = self.client.detect_language(text)
            return result['language']
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'  # Default to English
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.supported_languages

class TextToSpeechService:
    """Google Text-to-Speech integration."""
    
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        self.voice_profiles = self._load_voice_profiles()
    
    def _load_voice_profiles(self) -> Dict[str, List[Dict]]:
        """Load available voice profiles for each language."""
        return {
            'ja': [
                {'id': 'ja-JP-Wavenet-A', 'name': 'Japanese Female 1', 'gender': 'FEMALE'},
                {'id': 'ja-JP-Wavenet-B', 'name': 'Japanese Male 1', 'gender': 'MALE'},
                {'id': 'ja-JP-Wavenet-C', 'name': 'Japanese Female 2', 'gender': 'FEMALE'},
                {'id': 'ja-JP-Wavenet-D', 'name': 'Japanese Male 2', 'gender': 'MALE'}
            ],
            'en': [
                {'id': 'en-US-Wavenet-A', 'name': 'English Female 1', 'gender': 'FEMALE'},
                {'id': 'en-US-Wavenet-B', 'name': 'English Male 1', 'gender': 'MALE'},
                {'id': 'en-US-Wavenet-C', 'name': 'English Female 2', 'gender': 'FEMALE'},
                {'id': 'en-US-Wavenet-D', 'name': 'English Male 2', 'gender': 'MALE'}
            ],
            'ko': [
                {'id': 'ko-KR-Wavenet-A', 'name': 'Korean Female 1', 'gender': 'FEMALE'},
                {'id': 'ko-KR-Wavenet-B', 'name': 'Korean Female 2', 'gender': 'FEMALE'},
                {'id': 'ko-KR-Wavenet-C', 'name': 'Korean Male 1', 'gender': 'MALE'},
                {'id': 'ko-KR-Wavenet-D', 'name': 'Korean Male 2', 'gender': 'MALE'}
            ]
        }
    
    def synthesize_speech(self, text: str, voice_id: str, speed: float = 1.0) -> bytes:
        """Convert text to speech audio."""
        try:
            # Parse voice ID to get language and voice name
            language_code = voice_id.split('-')[0] + '-' + voice_id.split('-')[1]
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_id
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed
            )
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise
    
    def get_available_voices(self, language: str) -> List[Dict]:
        """Get available voices for a language."""
        return self.voice_profiles.get(language, [])

class RealtimeTranslationService:
    """Main service coordinating speech recognition, translation, and synthesis."""
    
    def __init__(self):
        self.speech_service = SpeechRecognitionService()
        self.translation_service = TextTranslationService()
        self.tts_service = TextToSpeechService()
        self.active_sessions: Dict[str, Dict] = {}
    
    async def start_translation_session(self, user_id: str, room_id: str, db: Session):
        """Start a translation session for a user in a room."""
        try:
            # Get user's translation settings
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            settings = user.translation_settings
            if not settings:
                # Create default settings
                settings = TranslationSettings(user_id=user_id)
                db.add(settings)
                db.commit()
            
            # Start speech recognition stream
            source_language = self._get_language_code(user.main_language)
            await self.speech_service.start_recognition_stream(user_id, source_language)
            
            # Store session info
            self.active_sessions[user_id] = {
                'room_id': room_id,
                'source_language': source_language,
                'settings': settings,
                'user': user
            }
            
            logger.info(f"Started translation session for user {user_id} in room {room_id}")
            
        except Exception as e:
            logger.error(f"Failed to start translation session: {e}")
            raise
    
    async def process_audio_data(self, user_id: str, audio_data: bytes) -> Optional[Dict]:
        """Process incoming audio data and return translation results."""
        try:
            if user_id not in self.active_sessions:
                return None
            
            # Add audio to recognition stream
            await self.speech_service.add_audio_chunk(user_id, audio_data)
            
            # Process recognition results (this would be handled by the WebSocket)
            # For now, return None as results are processed in the WebSocket handler
            return None
            
        except Exception as e:
            logger.error(f"Error processing audio data for user {user_id}: {e}")
            return None
    
    async def process_recognition_result(self, user_id: str, transcript: str, is_final: bool) -> Optional[Dict]:
        """Process speech recognition result and generate translations."""
        try:
            if user_id not in self.active_sessions or not is_final:
                return None
            
            session = self.active_sessions[user_id]
            settings = session['settings']
            
            if not (settings.text_translation_enabled or settings.voice_translation_enabled):
                return None
            
            # Get target languages for other participants in the room
            target_languages = await self._get_room_target_languages(
                session['room_id'], 
                user_id,
                session['source_language']
            )
            
            results = []
            
            for target_lang in target_languages:
                # Translate text
                translation_result = self.translation_service.translate_text(
                    transcript,
                    target_lang,
                    session['source_language']
                )
                
                result = {
                    'speaker_id': user_id,
                    'original_text': transcript,
                    'translated_text': translation_result['translated_text'],
                    'source_language': session['source_language'],
                    'target_language': target_lang,
                    'type': 'text_translation'
                }
                
                # Generate voice if enabled
                if settings.voice_translation_enabled:
                    voice_id = settings.preferred_voice_id or self._get_default_voice(target_lang)
                    audio_content = self.tts_service.synthesize_speech(
                        translation_result['translated_text'],
                        voice_id,
                        settings.voice_speed
                    )
                    
                    result.update({
                        'type': 'voice_translation',
                        'audio_data': base64.b64encode(audio_content).decode('utf-8'),
                        'voice_id': voice_id
                    })
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing recognition result: {e}")
            return None
    
    def stop_translation_session(self, user_id: str):
        """Stop translation session for a user."""
        try:
            if user_id in self.active_sessions:
                self.speech_service.stop_recognition_stream(user_id)
                del self.active_sessions[user_id]
                logger.info(f"Stopped translation session for user {user_id}")
        except Exception as e:
            logger.error(f"Error stopping translation session: {e}")
    
    def get_available_voices(self, language: str) -> List[Dict]:
        """Get available voices for a language."""
        return self.tts_service.get_available_voices(language)
    
    async def update_translation_settings(self, user_id: str, settings_data: Dict, db: Session):
        """Update user's translation settings."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            settings = user.translation_settings
            if not settings:
                settings = TranslationSettings(user_id=user_id)
                db.add(settings)
            
            # Update settings
            for key, value in settings_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            db.commit()
            
            # Update active session if exists
            if user_id in self.active_sessions:
                self.active_sessions[user_id]['settings'] = settings
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating translation settings: {e}")
            return False
    
    def _get_language_code(self, language: str) -> str:
        """Convert language code to Google API format."""
        language_map = {
            'ja': 'ja-JP',
            'en': 'en-US',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE'
        }
        return language_map.get(language, 'en-US')
    
    def _get_default_voice(self, language: str) -> str:
        """Get default voice ID for a language."""
        default_voices = {
            'ja-JP': 'ja-JP-Wavenet-A',
            'en-US': 'en-US-Wavenet-A',
            'ko-KR': 'ko-KR-Wavenet-A'
        }
        return default_voices.get(language, 'en-US-Wavenet-A')
    
    async def _get_room_target_languages(self, room_id: str, speaker_id: str, source_language: str) -> List[str]:
        """Get target languages for other participants in the room."""
        # This would query the room participants and their language preferences
        # For now, return common languages excluding the source
        all_languages = ['ja-JP', 'en-US', 'ko-KR']
        return [lang for lang in all_languages if lang != source_language]

# Global service instances
translation_service = RealtimeTranslationService()