"""
Database Models and Session Management - COMPLETE IMPLEMENTATION
SQLAlchemy setup with all required tables.
"""

import os
from datetime import datetime
from typing import Generator
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import enum

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./confirmations.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Enums
class ConfirmationStatus(enum.Enum):
    """Status of a trade confirmation"""

    PENDING = "pending"
    PROCESSING = "processing"
    VALIDATION_FAILED = "validation_failed"
    REQUIRES_REVIEW = "requires_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ReviewTaskStatus(enum.Enum):
    """Status of a human review task"""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class AliasStatus(enum.Enum):
    """Status of a pending alias"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Models
class Confirmation(Base):
    """
    Main confirmation tracking table.
    Stores the complete state and history of each confirmation.
    """

    __tablename__ = "confirmations"

    id = Column(String, primary_key=True, index=True)
    status = Column(
        SQLEnum(ConfirmationStatus), default=ConfirmationStatus.PENDING, nullable=False
    )
    confidence = Column(Float, default=0.0, nullable=False)
    final_data = Column(JSON, nullable=True)  # The final reconciled trade data
    agent_history = Column(JSON, default=list)  # List of all agent steps
    decisions = Column(JSON, default=list)  # List of all agent decisions
    validation_issues = Column(JSON, default=list)  # List of validation issues found
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    pdf_filename = Column(String, nullable=False)

    # Relationships
    review_tasks = relationship(
        "HumanReviewTask", back_populates="confirmation", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Confirmation(id={self.id}, status={self.status.value}, confidence={self.confidence})>"


class HumanReviewTask(Base):
    """
    Tasks that require human review and approval.
    Created when agents encounter issues they can't resolve.
    """

    __tablename__ = "human_review_tasks"

    id = Column(Integer, primary_key=True, index=True)
    confirmation_id = Column(
        String, ForeignKey("confirmations.id"), nullable=False, index=True
    )
    field = Column(String, nullable=False)  # Which field needs review
    extracted_value = Column(String, nullable=True)  # What was extracted from PDF
    expected_value = Column(String, nullable=True)  # What trade suite expects
    agent_reasoning = Column(String, nullable=True)  # Why agent flagged this
    status = Column(
        SQLEnum(ReviewTaskStatus), default=ReviewTaskStatus.PENDING, nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(
        JSON, nullable=True
    )  # Contains: {action, approved_value, notes}

    # Relationships
    confirmation = relationship("Confirmation", back_populates="review_tasks")

    def __repr__(self):
        return f"<HumanReviewTask(id={self.id}, field={self.field}, status={self.status.value})>"


class PendingAlias(Base):
    """
    Aliases suggested by agents awaiting approval.
    High-confidence aliases are auto-applied but still need human approval.
    """

    __tablename__ = "pending_aliases"

    id = Column(Integer, primary_key=True, index=True)
    field = Column(String, nullable=False, index=True)  # e.g., 'counterparty', 'rate'
    from_value = Column(String, nullable=False)  # Original value
    to_value = Column(String, nullable=False)  # Target canonical value
    counterparty_id = Column(
        String, nullable=True, index=True
    )  # Null = global alias
    confidence = Column(Float, nullable=False)  # Agent's confidence in this alias
    status = Column(
        SQLEnum(AliasStatus), default=AliasStatus.PENDING, nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    created_by_confirmation_id = Column(
        String, nullable=True
    )  # Which confirmation created this

    def __repr__(self):
        return f"<PendingAlias(id={self.id}, field={self.field}, from='{self.from_value}', to='{self.to_value}')>"


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI routes to get database session.

    Yields:
        Database session

    Example:
        @app.get("/confirmations/{id}")
        async def get_confirmation(id: str, db: Session = Depends(get_db)):
            return db.query(Confirmation).filter(Confirmation.id == id).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all tables. USE WITH CAUTION!

    Only for development/testing purposes.
    """
    Base.metadata.drop_all(bind=engine)
