"""
Data models for the Seasonal Work Aggregator.
Uses dataclasses for the MVP — migrate to SQLAlchemy/ORM in production.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional


# ── Enums ───────────────────────────────────────────────────────────────────

class SourceType(str, Enum):
    PUBLIC_WEB = "public_web"
    FACEBOOK_OPERATOR_SCREENSHOT = "facebook_operator_screenshot"
    FACEBOOK_VISIBLE_CAPTURE = "facebook_visible_capture"
    TELEGRAM_SUBMISSION = "telegram_submission"
    EMPLOYER_FORM = "employer_form"
    WORKER_FORM = "worker_form"
    OWN_GROUP_COMMENT = "own_group_comment"
    OWN_GROUP_POST = "own_group_post"
    MANUAL_ADMIN_ENTRY = "manual_admin_entry"


class CaptureMethod(str, Enum):
    WEB_SEARCH = "web_search"
    OPERATOR_SCREENSHOT = "operator_screenshot"
    OPERATOR_COPY_PASTE = "operator_copy_paste"
    BROWSER_CAPTURE = "browser_capture"
    TELEGRAM_BOT = "telegram_bot"
    DIRECT_FORM = "direct_form"


class Language(str, Enum):
    SR = "sr"
    RU = "ru"
    UK = "uk"
    HU = "hu"
    RO = "ro"
    EN = "en"
    OTHER = "other"


class PayType(str, Enum):
    DAILY = "daily"
    HOURLY = "hourly"
    PER_KG = "per_kg"
    PER_UNIT = "per_unit"
    MONTHLY = "monthly"


class PayFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    END_OF_SEASON = "end_of_season"


class FreshnessStatus(str, Enum):
    FRESH_TODAY = "fresh_today"
    FRESH_1_3_DAYS = "fresh_1_3_days"
    FRESH_4_7_DAYS = "fresh_4_7_days"
    STALE_OVER_7_DAYS = "stale_over_7_days"
    UNKNOWN_DATE = "unknown_date"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    REJECT = "reject"


class RiskFlag(str, Enum):
    ASKS_FOR_PAYMENT = "asks_for_payment"
    ASKS_FOR_DOCUMENTS = "asks_for_documents"
    ASKS_FOR_JMBG = "asks_for_jmbg"
    ASKS_FOR_PASSPORT_PHOTO = "asks_for_passport_photo"
    NO_CONTACT = "no_contact"
    TOO_GOOD_TO_BE_TRUE = "too_good_to_be_true"
    UNCLEAR_MIDDLEMAN = "unclear_middleman"
    UNKNOWN_LOCATION = "unknown_location"
    NO_PAY_INFO = "no_pay_info"
    FOREIGN_COUNTRY = "foreign_country"
    SPAM_KEYWORDS = "spam_keywords"
    UNREADABLE_SOURCE = "unreadable_source"


class Classification(str, Enum):
    GOOD_LEAD = "good_lead"
    LOW_INFO_LEAD = "low_info_lead"
    CONTACT_ONLY_LEAD = "contact_only_lead"
    MARKET_CONTEXT = "market_context"
    WORKER_LOOKING_FOR_JOB = "worker_looking_for_job"
    EMPLOYER_LOOKING_FOR_WORKERS = "employer_looking_for_workers"
    NEEDS_CLARIFICATION = "needs_clarification"
    DUPLICATE_FROM_PREVIOUS_DIGEST = "duplicate_from_previous_digest"
    REPEAT_CANDIDATE = "repeat_candidate"
    SUSPICIOUS = "suspicious"
    REJECT = "reject"


class DuplicateStatus(str, Enum):
    NEW = "new"
    POSSIBLE_DUPLICATE = "possible_duplicate"
    DUPLICATE = "duplicate"
    DUPLICATE_FROM_PREVIOUS_DIGEST = "duplicate_from_previous_digest"
    REPEAT_CANDIDATE = "repeat_candidate"
    CLOSED = "closed"


class ModerationStatus(str, Enum):
    NEW = "new"
    APPROVED_FOR_DIGEST = "approved_for_digest"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class GenderRequirement(str, Enum):
    MALE = "male"
    FEMALE = "female"
    COUPLE = "couple"
    ANY = "any"


class ReviewType(str, Enum):
    WORKER_REVIEW = "worker_review"
    EMPLOYER_REVIEW = "employer_review"


class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    GROUP_ONLY = "group_only"
    PRIVATE = "private"


# ── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class JobLead:
    lead_id: UUID = field(default_factory=uuid4)
    source_type: SourceType = SourceType.MANUAL_ADMIN_ENTRY
    source_name: str = ""
    source_url: Optional[str] = None
    source_group: Optional[str] = None
    source_post_url: Optional[str] = None
    source_captured_at: datetime = field(default_factory=datetime.utcnow)
    source_capture_method: CaptureMethod = CaptureMethod.OPERATOR_COPY_PASTE
    raw_text: Optional[str] = None
    raw_image_path: Optional[str] = None
    language: Language = Language.SR
    job_type: str = ""
    location: str = ""
    region: Optional[str] = None
    country: str = "Srbija"
    workers_needed: Optional[int] = None
    gender_requirement: Optional[GenderRequirement] = None
    start_date: Optional[date] = None
    pay_amount: Optional[str] = None
    pay_currency: Optional[str] = "RSD"
    pay_type: Optional[PayType] = None
    payment_frequency: Optional[PayFrequency] = None
    accommodation: Optional[bool] = None
    accommodation_details: Optional[str] = None
    food: Optional[bool] = None
    food_details: Optional[str] = None
    transport: Optional[bool] = None
    transport_details: Optional[str] = None
    working_hours: Optional[str] = None
    registered_work: Optional[bool] = None
    employer_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_viber: bool = False
    contact_whatsapp: bool = False
    contact_facebook: bool = False
    contact_inbox_only: bool = False
    missing_info: list[str] = field(default_factory=list)
    freshness_status: FreshnessStatus = FreshnessStatus.UNKNOWN_DATE
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_flags: list[RiskFlag] = field(default_factory=list)
    classification: Classification = Classification.NEEDS_CLARIFICATION
    duplicate_status: DuplicateStatus = DuplicateStatus.NEW
    duplicate_of: Optional[UUID] = None
    moderation_status: ModerationStatus = ModerationStatus.NEW
    public_digest_allowed: bool = False
    operator_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def can_go_to_digest(self) -> bool:
        return (
            self.classification
            in (
                Classification.GOOD_LEAD,
                Classification.LOW_INFO_LEAD,
                Classification.CONTACT_ONLY_LEAD,
            )
            and self.moderation_status == ModerationStatus.APPROVED_FOR_DIGEST
            and self.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM)
            and self.duplicate_status != DuplicateStatus.DUPLICATE
        )


@dataclass
class EmployerProfile:
    employer_id: UUID = field(default_factory=uuid4)
    display_name: str = ""
    known_names: list[str] = field(default_factory=list)
    phone_numbers: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    job_types: list[str] = field(default_factory=list)
    source_count: int = 0
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    active_jobs_count: int = 0
    reviews_count: int = 0
    average_worker_rating: Optional[float] = None
    rating_breakdown: dict = field(default_factory=dict)
    risk_flags: list[RiskFlag] = field(default_factory=list)
    moderation_status: ModerationStatus = ModerationStatus.NEW
    right_of_reply_notes: Optional[str] = None


@dataclass
class WorkerProfile:
    worker_id: UUID = field(default_factory=uuid4)
    display_name: str = ""
    phone_numbers: list[str] = field(default_factory=list)
    preferred_jobs: list[str] = field(default_factory=list)
    preferred_locations: list[str] = field(default_factory=list)
    available_from: Optional[date] = None
    languages: list[Language] = field(default_factory=list)
    experience_tags: list[str] = field(default_factory=list)
    worker_reviews_count: int = 0
    employer_feedback_count: int = 0
    moderation_status: ModerationStatus = ModerationStatus.NEW
    privacy_level: PrivacyLevel = PrivacyLevel.GROUP_ONLY


@dataclass
class Review:
    review_id: UUID = field(default_factory=uuid4)
    review_type: ReviewType = ReviewType.WORKER_REVIEW
    target_type: str = "employer"
    target_id: Optional[UUID] = None
    author_type: str = "worker"
    author_id: Optional[UUID] = None
    job_lead_id: Optional[UUID] = None
    rating_overall: int = 0
    rating_pay_accuracy: int = 0
    rating_accommodation: int = 0
    rating_food: int = 0
    rating_working_hours: int = 0
    rating_payment_timeliness: int = 0
    rating_respect: int = 0
    text: str = ""
    evidence_files: list[str] = field(default_factory=list)
    right_of_reply_status: str = "pending"
    right_of_reply_text: Optional[str] = None
    moderation_status: ModerationStatus = ModerationStatus.NEW
    public_allowed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def average_rating(self) -> float:
        categories = [
            self.rating_pay_accuracy,
            self.rating_accommodation,
            self.rating_food,
            self.rating_working_hours,
            self.rating_payment_timeliness,
            self.rating_respect,
        ]
        valid = [r for r in categories if r > 0]
        return sum(valid) / len(valid) if valid else 0.0
