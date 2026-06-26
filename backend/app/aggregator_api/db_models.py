"""SQLAlchemy ORM models for the aggregator database."""

import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _json_list(value: list | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _json_dict(value: dict | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


class JobLeadDB(Base):
    __tablename__ = "job_leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(String, unique=True, nullable=False, index=True)
    source_type = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    source_group = Column(String, nullable=True)
    source_post_url = Column(String, nullable=True)
    source_captured_at = Column(DateTime, default=datetime.utcnow)
    source_capture_method = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)
    raw_image_path = Column(String, nullable=True)
    language = Column(String, default="sr")
    job_type = Column(String, default="")
    location = Column(String, default="")
    region = Column(String, nullable=True)
    country = Column(String, default="Srbija")
    workers_needed = Column(Integer, nullable=True)
    gender_requirement = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    pay_amount = Column(String, nullable=True)
    pay_currency = Column(String, default="RSD")
    pay_type = Column(String, nullable=True)
    payment_frequency = Column(String, nullable=True)
    accommodation = Column(Integer, nullable=True)
    accommodation_details = Column(String, nullable=True)
    food = Column(Integer, nullable=True)
    food_details = Column(String, nullable=True)
    transport = Column(Integer, nullable=True)
    transport_details = Column(String, nullable=True)
    working_hours = Column(String, nullable=True)
    registered_work = Column(Integer, nullable=True)
    employer_name = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_viber = Column(Boolean, default=False)
    contact_whatsapp = Column(Boolean, default=False)
    contact_facebook = Column(Boolean, default=False)
    contact_inbox_only = Column(Boolean, default=False)
    missing_info_json = Column(Text, default="[]")
    freshness_status = Column(String, default="unknown_date")
    risk_level = Column(String, default="medium")
    risk_flags_json = Column(Text, default="[]")
    classification = Column(String, default="needs_clarification")
    duplicate_status = Column(String, default="new")
    duplicate_of = Column(String, nullable=True)
    moderation_status = Column(String, default="pending_review")
    public_digest_allowed = Column(Integer, default=0)
    operator_verified = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployerDB(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employer_id = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, default="")
    known_names_json = Column(Text, default="[]")
    phone_numbers_json = Column(Text, default="[]")
    locations_json = Column(Text, default="[]")
    job_types_json = Column(Text, default="[]")
    source_count = Column(Integer, default=0)
    first_seen_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    active_jobs_count = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)
    average_worker_rating = Column(Float, nullable=True)
    rating_breakdown_json = Column(Text, default="{}")
    risk_flags_json = Column(Text, default="[]")
    moderation_status = Column(String, default="new")
    right_of_reply_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkerDB(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, default="")
    phone_numbers_json = Column(Text, default="[]")
    preferred_jobs_json = Column(Text, default="[]")
    preferred_locations_json = Column(Text, default="[]")
    available_from = Column(String, nullable=True)
    languages_json = Column(Text, default="[]")
    experience_tags_json = Column(Text, default="[]")
    worker_reviews_count = Column(Integer, default=0)
    employer_feedback_count = Column(Integer, default=0)
    moderation_status = Column(String, default="new")
    privacy_level = Column(String, default="group_only")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReviewDB(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String, unique=True, nullable=False, index=True)
    review_type = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=True)
    author_type = Column(String, nullable=False)
    author_id = Column(String, nullable=True)
    job_lead_id = Column(String, nullable=True)
    rating_overall = Column(Integer, default=0)
    rating_pay_accuracy = Column(Integer, default=0)
    rating_accommodation = Column(Integer, default=0)
    rating_food = Column(Integer, default=0)
    rating_working_hours = Column(Integer, default=0)
    rating_payment_timeliness = Column(Integer, default=0)
    rating_respect = Column(Integer, default=0)
    rating_safety = Column(Integer, default=0)
    text = Column(Text, default="")
    evidence_files_json = Column(Text, default="[]")
    right_of_reply_status = Column(String, default="pending")
    moderation_status = Column(String, default="new")
    public_allowed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModerationEventDB(Base):
    __tablename__ = "moderation_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    old_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    reason = Column(Text, default="")
    operator = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
