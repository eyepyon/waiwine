"""
User and OAuth provider models.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class User(Base):
    """User model with multi-language support."""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    main_language = Column(String, default='ja')  # UI language setting
    profile_image_url = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    oauth_providers = relationship("OAuthProvider", back_populates="user", cascade="all, delete-orphan")
    translation_settings = relationship("TranslationSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', name='{self.name}')>"

class OAuthProvider(Base):
    """OAuth provider information for users."""
    __tablename__ = 'oauth_providers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    provider_name = Column(String, nullable=False)  # 'google', 'twitter', 'line'
    provider_user_id = Column(String, nullable=False)
    provider_email = Column(String)
    linked_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="oauth_providers")
    
    __table_args__ = (UniqueConstraint('provider_name', 'provider_user_id'),)
    
    def __repr__(self):
        return f"<OAuthProvider(provider='{self.provider_name}', user_id='{self.user_id}')>"

class TranslationSettings(Base):
    """User translation preferences and settings."""
    __tablename__ = 'translation_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Translation feature toggles
    text_translation_enabled = Column(Boolean, default=True)
    voice_translation_enabled = Column(Boolean, default=False)
    
    # Audio settings
    original_voice_volume = Column(Float, default=0.3)  # Original audio volume (0.0-1.0)
    translated_voice_volume = Column(Float, default=0.8)  # Translated audio volume
    
    # Voice configuration
    preferred_voice_id = Column(String)  # User selected voice ID
    voice_speed = Column(Float, default=1.0)  # Voice playback speed
    
    # Display settings
    subtitle_position = Column(String, default='bottom')  # 'top', 'bottom', 'overlay'
    subtitle_font_size = Column(Integer, default=16)
    subtitle_background_opacity = Column(Float, default=0.7)
    
    # Relationships
    user = relationship("User", back_populates="translation_settings")
    
    def __repr__(self):
        return f"<TranslationSettings(user_id='{self.user_id}')>"