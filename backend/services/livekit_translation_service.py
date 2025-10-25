"""
LiveKit Agents-based translation service with STT, TTS, and translation.
Uses LiveKit's built-in AI capabilities for real-time translation.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    stt,
    tts,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero
from sqlalchemy.orm import Session

from backend.models.user import User, TranslationSettings
from backend.config.settings import get_config

logger = logging.getLogger(__name__)
config = get_config()


class LiveKitTranslationAgent:
    """LiveKit Agent for real-time speech translation."""
    
    def __init__(self):
        self.active_agents: Dict[str, VoicePipelineAgent] = {}
        self.room_contexts: Dict[str, JobContext] = {}
        
    async def create_translation_agent(
        self,
        ctx: JobContext,
        user_id: str,
        source_language: str = "ja",
        target_languages: List[str] = None
    ) -> VoicePipelineAgent:
        """Create a voice pipeline agent for translation."""
        
        # Configure STT (Speech-to-Text) using Deepgram
        stt_provider = deepgram.STT(
            model="nova-2",
            language=self._get_deepgram_language_code(source_language),
            detect_language=False,
            interim_results=True,
            smart_format=True,
            punctuate=True,
        )
        
        # Configure TTS (Text-to-Speech) using OpenAI
        tts_provider = openai.TTS(
            model="tts-1",
            voice=self._get_openai_voice(source_language),
        )
        
        # Configure LLM for translation
        llm_provider = openai.LLM(model="gpt-4-turbo-preview")
        
        # Create initial context for translation
        initial_ctx = self._create_translation_context(source_language, target_languages)
        
        # Create voice pipeline agent
        agent = VoicePipelineAgent(
            vad=silero.VAD.load(),
            stt=stt_provider,
            llm=llm_provider,
            tts=tts_provider,
            chat_ctx=initial_ctx,
        )
        
        # Store agent reference
        self.active_agents[user_id] = agent
        
        return agent
    
    def _create_translation_context(
        self,
        source_language: str,
        target_languages: List[str]
    ) -> llm.ChatContext:
        """Create chat context with translation instructions."""
        
        target_langs_str = ", ".join([self._get_language_name(lang) for lang in target_languages or ["en"]])
        
        system_prompt = f"""You are a real-time translation assistant for a wine tasting video chat.
Your role is to:
1. Listen to speech in {self._get_language_name(source_language)}
2. Translate it accurately to {target_langs_str}
3. Maintain the speaker's tone and context about wine
4. Preserve wine-specific terminology correctly

When translating:
- Keep wine names and technical terms accurate
- Maintain conversational tone
- Respond quickly for real-time communication
- If multiple target languages are requested, provide all translations clearly labeled

Format your response as:
[Language]: Translation text
"""
        
        return llm.ChatContext().append(
            role="system",
            text=system_prompt,
        )
    
    async def start_room_translation(
        self,
        ctx: JobContext,
        room_name: str,
        participants: List[Dict[str, Any]]
    ):
        """Start translation for all participants in a room."""
        
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        
        # Create agents for each participant based on their language preferences
        for participant_info in participants:
            user_id = participant_info["user_id"]
            source_lang = participant_info.get("language", "ja")
            target_langs = participant_info.get("target_languages", ["en"])
            
            agent = await self.create_translation_agent(
                ctx=ctx,
                user_id=user_id,
                source_language=source_lang,
                target_languages=target_langs
            )
            
            # Start the agent
            agent.start(ctx.room)
            
            logger.info(f"Started translation agent for user {user_id} in room {room_name}")
        
        # Store room context
        self.room_contexts[room_name] = ctx
    
    async def handle_participant_speech(
        self,
        user_id: str,
        audio_frame: rtc.AudioFrame
    ):
        """Handle incoming speech from a participant."""
        
        if user_id not in self.active_agents:
            logger.warning(f"No active agent for user {user_id}")
            return
        
        agent = self.active_agents[user_id]
        # The agent automatically processes audio through its pipeline
        # No manual handling needed - LiveKit handles this internally
    
    async def stop_room_translation(self, room_name: str):
        """Stop translation for a room."""
        
        if room_name in self.room_contexts:
            ctx = self.room_contexts[room_name]
            await ctx.disconnect()
            del self.room_contexts[room_name]
            
            logger.info(f"Stopped translation for room {room_name}")
    
    async def stop_user_translation(self, user_id: str):
        """Stop translation for a specific user."""
        
        if user_id in self.active_agents:
            del self.active_agents[user_id]
            logger.info(f"Stopped translation for user {user_id}")
    
    def _get_deepgram_language_code(self, language: str) -> str:
        """Convert language code to Deepgram format."""
        language_map = {
            "ja": "ja",
            "en": "en-US",
            "ko": "ko",
            "zh": "zh-CN",
            "es": "es",
            "fr": "fr",
            "de": "de",
        }
        return language_map.get(language, "en-US")
    
    def _get_openai_voice(self, language: str) -> str:
        """Get appropriate OpenAI TTS voice for language."""
        voice_map = {
            "ja": "nova",
            "en": "alloy",
            "ko": "nova",
            "zh": "nova",
            "es": "nova",
            "fr": "nova",
            "de": "nova",
        }
        return voice_map.get(language, "alloy")
    
    def _get_language_name(self, code: str) -> str:
        """Get full language name from code."""
        names = {
            "ja": "Japanese",
            "en": "English",
            "ko": "Korean",
            "zh": "Chinese",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
        }
        return names.get(code, "English")


class LiveKitTranslationService:
    """Service for managing LiveKit-based translation sessions."""
    
    def __init__(self):
        self.agent = LiveKitTranslationAgent()
        self.active_sessions: Dict[str, Dict] = {}
    
    async def start_translation_session(
        self,
        room_name: str,
        user_id: str,
        source_language: str,
        target_languages: List[str],
        db: Session
    ):
        """Start a translation session for a user."""
        
        try:
            # Get user settings
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            settings = user.translation_settings
            if not settings:
                settings = TranslationSettings(user_id=user_id)
                db.add(settings)
                db.commit()
            
            # Store session info
            if room_name not in self.active_sessions:
                self.active_sessions[room_name] = {
                    "participants": []
                }
            
            participant_info = {
                "user_id": user_id,
                "language": source_language,
                "target_languages": target_languages,
                "settings": settings,
            }
            
            self.active_sessions[room_name]["participants"].append(participant_info)
            
            logger.info(f"Started translation session for user {user_id} in room {room_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start translation session: {e}")
            raise
    
    async def stop_translation_session(self, room_name: str, user_id: str):
        """Stop translation session for a user."""
        
        try:
            if room_name in self.active_sessions:
                participants = self.active_sessions[room_name]["participants"]
                self.active_sessions[room_name]["participants"] = [
                    p for p in participants if p["user_id"] != user_id
                ]
                
                # Remove room if no participants left
                if not self.active_sessions[room_name]["participants"]:
                    await self.agent.stop_room_translation(room_name)
                    del self.active_sessions[room_name]
                else:
                    await self.agent.stop_user_translation(user_id)
                
                logger.info(f"Stopped translation session for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error stopping translation session: {e}")
    
    async def update_translation_settings(
        self,
        user_id: str,
        settings_data: Dict,
        db: Session
    ):
        """Update user's translation settings."""
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            settings = user.translation_settings
            if not settings:
                settings = TranslationSettings(user_id=user_id)
                db.add(settings)
            
            for key, value in settings_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating translation settings: {e}")
            return False
    
    def get_room_participants(self, room_name: str) -> List[Dict]:
        """Get participants in a room."""
        
        if room_name in self.active_sessions:
            return self.active_sessions[room_name]["participants"]
        return []


# Global service instance
livekit_translation_service = LiveKitTranslationService()
