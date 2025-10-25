"""
Wine and room-related models.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base

class Wine(Base):
    """Wine model with multilingual support."""
    __tablename__ = 'wines'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    vintage = Column(Integer)
    region = Column(String)
    producer = Column(String)
    wine_type = Column(String)  # 'red', 'white', 'sparkling', etc.
    alcohol_content = Column(Float)
    image_url = Column(String)
    
    # Multilingual support
    name_translations = Column(JSON)  # {'ja': '日本語名', 'en': 'English name'}
    tasting_notes_translations = Column(JSON)  # Multilingual tasting notes
    region_translations = Column(JSON)  # Region names in multiple languages
    
    # Recognition related
    recognition_keywords = Column(JSON)  # Keywords for recognition
    recognition_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    room_sessions = relationship("RoomSession", back_populates="wine")
    
    def get_localized_name(self, language: str) -> str:
        """Get wine name in specified language."""
        if self.name_translations and language in self.name_translations:
            return self.name_translations[language]
        return self.name
    
    def get_localized_tasting_notes(self, language: str) -> str:
        """Get tasting notes in specified language."""
        if self.tasting_notes_translations and language in self.tasting_notes_translations:
            return self.tasting_notes_translations[language]
        return ''
    
    def __repr__(self):
        return f"<Wine(id='{self.id}', name='{self.name}', vintage={self.vintage})>"

class RoomSession(Base):
    """Video chat room sessions."""
    __tablename__ = 'room_sessions'
    
    id = Column(String, primary_key=True)
    wine_id = Column(String, ForeignKey('wines.id'), nullable=False)
    room_name = Column(String, nullable=False)
    active_participants = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    
    # Relationships
    wine = relationship("Wine", back_populates="room_sessions")
    
    def __repr__(self):
        return f"<RoomSession(id='{self.id}', room_name='{self.room_name}', participants={self.active_participants})>"

class VoiceProfile(Base):
    """Available voice profiles for text-to-speech."""
    __tablename__ = 'voice_profiles'
    
    id = Column(String, primary_key=True)
    language = Column(String, nullable=False)  # 'ja', 'en', 'ko', etc.
    voice_name = Column(String, nullable=False)  # 'ja-JP-Wavenet-A'
    gender = Column(String)  # 'male', 'female', 'neutral'
    description = Column(String)  # Voice description
    sample_audio_url = Column(String)  # Sample audio URL
    
    # Multilingual descriptions
    description_translations = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    
    def get_localized_description(self, language: str) -> str:
        """Get voice description in specified language."""
        if self.description_translations and language in self.description_translations:
            return self.description_translations[language]
        return self.description or ''
    
    def __repr__(self):
        return f"<VoiceProfile(id='{self.id}', language='{self.language}', voice_name='{self.voice_name}')>"

class Translation(Base):
    """Translation key-value pairs for internationalization."""
    __tablename__ = 'translations'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False, index=True)  # 'wine.type.red', 'ui.button.join'
    language = Column(String, nullable=False, index=True)  # 'ja', 'en', 'ko', etc.
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<Translation(key='{self.key}', language='{self.language}')>"