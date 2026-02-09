"""Feedback model - user ratings (thumbs up/down) on answers."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text

from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # 1 = thumbs up, -1 = thumbs down
    created_at = Column(DateTime, default=datetime.utcnow)
