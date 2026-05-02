from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Dict, List
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cc_ai.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DBCreator(Base):
    __tablename__ = "creators"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    gender = Column(String)
    niche = Column(String)
    appearance = Column(JSON)
    voice_profile = Column(String)
    personality_traits = Column(JSON)
    social_media_handles = Column(JSON)
    subscription_tiers = Column(JSON)
    is_online = Column(Boolean, default=False)
    last_active = Column(DateTime, default=datetime.utcnow)
    revenue = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    subscribers = relationship("DBSubscriber", back_populates="creator")
    content_posts = relationship("DBContentPost", back_populates="creator")

class DBSubscriber(Base):
    __tablename__ = "subscribers"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    tier = Column(String)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    preferences = Column(JSON, default=dict)
    creator_id = Column(String, ForeignKey("creators.id"))

    creator = relationship("DBCreator", back_populates="subscribers")

class DBContentPost(Base):
    __tablename__ = "content_posts"

    id = Column(String, primary_key=True, index=True)
    creator_id = Column(String, ForeignKey("creators.id"))
    type = Column(String)
    title = Column(String)
    description = Column(Text)
    content_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False)
    required_tier = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    comments = Column(JSON, default=list)

    creator = relationship("DBCreator", back_populates="content_posts")

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()