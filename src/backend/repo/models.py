import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from src.backend.repo.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    postcode = Column(String, nullable=True)
    
    call_sessions = relationship("CallSession", back_populates="customer")


class CallSession(Base):
    __tablename__ = "call_sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    status = Column(String, nullable=False, default="WAITING") # WAITING, LIVE, COMPLETED
    current_node = Column(String, nullable=False, default="greeting_node")
    escalation_reason = Column(String, nullable=True)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="call_sessions")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")
    journey_data = relationship("JourneyData", back_populates="session", uselist=False, cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("call_sessions.session_id"), nullable=False)
    speaker = Column(String, nullable=False)  # 'ai' or 'customer'
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("CallSession", back_populates="messages")


class JourneyData(Base):
    __tablename__ = "journey_data"

    session_id = Column(String, ForeignKey("call_sessions.session_id"), primary_key=True)
    moving = Column(Boolean, nullable=True)
    address = Column(String, nullable=True)
    fuel_type = Column(String, nullable=True)
    solar = Column(Boolean, nullable=True)
    life_support = Column(Boolean, nullable=True)
    concession = Column(Boolean, nullable=True)
    
    session = relationship("CallSession", back_populates="journey_data")

