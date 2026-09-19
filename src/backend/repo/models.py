import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.backend.repo.database import Base


class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    last_completed_step = Column(String, nullable=False)
    
    call_sessions = relationship("CallSession", back_populates="lead")


class CallSession(Base):
    __tablename__ = "call_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(String, ForeignKey("leads.lead_id"), nullable=False)
    current_node = Column(String, nullable=False, default="start")
    status = Column(String, nullable=False, default="ACTIVE")
    retry_count = Column(Integer, nullable=False, default=0)
    sentiment = Column(String, nullable=True, default="neutral")
    
    lead = relationship("Lead", back_populates="call_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("call_sessions.session_id"), nullable=False)
    speaker = Column(String, nullable=False)  # 'AI' or 'Customer'
    transcript = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("CallSession", back_populates="messages")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("call_sessions.session_id"), nullable=False)
    field_name = Column(String, nullable=False)
    field_value = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    
    session = relationship("CallSession", back_populates="extracted_fields")
