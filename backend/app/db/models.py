"""
backend/app/db/models.py - SQLAlchemy 2.0 Database Models
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Numeric
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    ticker = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    sector = Column(String(50), nullable=False)
    yf_symbol = Column(String(30), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(String(50), primary_key=True) # e.g. 'meena', 'arjun', 'rohan'
    display_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
    behavior_events = relationship("BehaviorEvent", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(String(50), ForeignKey("users.id"), primary_key=True)
    persona_label = Column(String(100), nullable=False)
    risk_tolerance = Column(String(20), nullable=False) # conservative, moderate, aggressive
    horizon_years = Column(Integer, default=3)
    max_single_stock_pct = Column(Float, default=10.0)
    sector_limits = Column(JSON, default=dict) # e.g. {"Banking": 40.0, "FMCG": 30.0}
    loss_aversion = Column(Float, default=0.5) # 0.0 - 1.0
    overtrading_score = Column(Float, default=0.1) # 0.0 - 1.0
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), ForeignKey("stocks.ticker"), nullable=False)
    qty = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="holdings")
    stock = relationship("Stock")

class Watchlist(Base):
    __tablename__ = "watchlist"
    user_id = Column(String(50), ForeignKey("users.id"), primary_key=True)
    ticker = Column(String(20), ForeignKey("stocks.ticker"), primary_key=True)

class BehaviorEvent(Base):
    __tablename__ = "behavior_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), ForeignKey("stocks.ticker"), nullable=False)
    action = Column(String(10), nullable=False) # buy, sell
    price = Column(Float, nullable=False)
    qty = Column(Float, nullable=False)
    event_ts = Column(DateTime, default=datetime.utcnow)
    context = Column(Text, default="")
    tag = Column(String(20), default="normal") # panic_sell, fomo_buy, normal

    user = relationship("User", back_populates="behavior_events")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String(50), primary_key=True)
    ticker = Column(String(20), ForeignKey("stocks.ticker"), nullable=False)
    doc_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    doc_date = Column(String(20), nullable=False)
    source_label = Column(String(30), default="SYNTHETIC")
    url = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocChunk", back_populates="document", cascade="all, delete-orphan")

class DocChunk(Base):
    __tablename__ = "doc_chunks"
    id = Column(String(80), primary_key=True)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=False)
    ticker = Column(String(20), ForeignKey("stocks.ticker"), nullable=False)
    chunk_index = Column(Integer, default=0)
    page = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True) # List of 384 floats stored as JSON (portable SQLite & Postgres)
    meta_info = Column(JSON, default=dict)

    document = relationship("Document", back_populates="chunks")

class AnalysisSession(Base):
    __tablename__ = "sessions"
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), ForeignKey("stocks.ticker"), nullable=False)
    data_mode = Column(String(20), default="cached")
    flags = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    agent = Column(String(50), nullable=False)
    signal = Column(String(20), nullable=False)
    confidence = Column(Float, default=0.0)
    status = Column(String(20), default="ok")
    latency_ms = Column(Integer, default=0)
    reasoning = Column(Text, default="")
    output_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class EvidenceRecord(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=True)
    doc_chunk_id = Column(String(80), nullable=True)
    source_type = Column(String(20), nullable=False) # filing, news, price, flow
    title = Column(String(255), nullable=False)
    snippet = Column(Text, nullable=False)
    url = Column(String(500), nullable=True)
    page = Column(Integer, nullable=True)
    relevance_score = Column(Float, nullable=True)

class RecommendationRecord(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    action = Column(String(20), nullable=False) # accumulate, hold, avoid, wait, reduce
    position_size_pct = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    summary = Column(Text, nullable=False)
    reasoning_chain = Column(JSON, default=dict)
    concentration_before = Column(Float, default=0.0)
    concentration_after = Column(Float, default=0.0)
    conflict_flag = Column(Boolean, default=False)
    degraded_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SessionMetric(Base):
    __tablename__ = "session_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class BacktestResult(Base):
    __tablename__ = "backtest_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(50), nullable=False)
    ticker = Column(String(20), nullable=False)
    horizon_days = Column(Integer, default=30)
    n_signals = Column(Integer, default=0)
    hit_rate = Column(Float, default=0.0)
    avg_fwd_return = Column(Float, default=0.0)
    run_at = Column(DateTime, default=datetime.utcnow)

