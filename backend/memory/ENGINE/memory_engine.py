"""Memory Engine v1.0 — persistent operational memory for the Runtime Manager.

Stores: employers, workers, cases, knowledge.
Features: trust scoring, duplicate detection, append-only history, indexes.
"""

import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field
from collections import defaultdict

MEMORY_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(MEMORY_ROOT, "DATABASE")
INDEX_DIR = os.path.join(MEMORY_ROOT, "INDEX")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _hash_phone(phone: str) -> str:
    digits = ''.join(c for c in phone if c.isdigit())
    return hashlib.sha256(digits.encode()).hexdigest()[:16]


@dataclass
class MemoryContext:
    """What the Brain receives from Memory for a given input."""
    known_employer: dict | None = None
    employer_trust: float | None = None
    employer_complaints: int = 0
    employer_history: list = field(default_factory=list)
    known_worker: dict | None = None
    known_phone: dict | None = None
    duplicate_lead: bool = False
    previous_salary_range: str | None = None
    operator_notes: str = ""


class MemoryEngine:
    """Main memory engine. All operations are append-only. Facts only."""

    def __init__(self, db_dir: str | None = None):
        self.db_dir = db_dir or DB_DIR
        self.index_dir = INDEX_DIR
        os.makedirs(self.db_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
        self._indexes: dict[str, dict] = {}
        self._load_indexes()

    # ── Indexes ─────────────────────────────────────────────────────────

    def _load_indexes(self) -> None:
        for name in ("phone_index", "name_index", "location_index"):
            path = os.path.join(self.index_dir, f"{name}.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self._indexes[name] = json.load(f)
            else:
                self._indexes[name] = {}

    def _save_index(self, name: str) -> None:
        path = os.path.join(self.index_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._indexes[name], f, indent=2, ensure_ascii=False)

    def _index_phone(self, phone: str, entity_type: str, entity_id: str) -> None:
        h = _hash_phone(phone)
        if h not in self._indexes["phone_index"]:
            self._indexes["phone_index"][h] = []
        entry = {"type": entity_type, "id": entity_id, "phone": phone}
        if entry not in self._indexes["phone_index"][h]:
            self._indexes["phone_index"][h].append(entry)
        self._save_index("phone_index")

    def _index_name(self, name: str, entity_type: str, entity_id: str) -> None:
        key = name.lower().strip()
        if key not in self._indexes["name_index"]:
            self._indexes["name_index"][key] = []
        entry = {"type": entity_type, "id": entity_id}
        if entry not in self._indexes["name_index"][key]:
            self._indexes["name_index"][key].append(entry)
        self._save_index("name_index")

    def _index_location(self, location: str, entity_type: str, entity_id: str) -> None:
        key = location.lower().strip()
        if key not in self._indexes["location_index"]:
            self._indexes["location_index"][key] = []
        entry = {"type": entity_type, "id": entity_id}
        if entry not in self._indexes["location_index"][key]:
            self._indexes["location_index"][key].append(entry)
        self._save_index("location_index")

    # ── File I/O ────────────────────────────────────────────────────────

    def _read(self, domain: str, entity_id: str) -> dict | None:
        path = os.path.join(self.db_dir, domain, f"{entity_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, domain: str, entity_id: str, data: dict) -> None:
        domain_dir = os.path.join(self.db_dir, domain)
        os.makedirs(domain_dir, exist_ok=True)
        path = os.path.join(domain_dir, f"{entity_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _list(self, domain: str) -> list[str]:
        domain_dir = os.path.join(self.db_dir, domain)
        if not os.path.exists(domain_dir):
            return []
        return [f.replace(".json", "") for f in os.listdir(domain_dir) if f.endswith(".json")]

    # ── Employer ────────────────────────────────────────────────────────

    def create_employer(self, data: dict) -> str:
        employer_id = data.get("employer_id") or _make_id("emp")
        now = _now()
        record = {
            "employer_id": employer_id,
            "names": data.get("names", []),
            "phones": data.get("phones", []),
            "viber": data.get("viber", []),
            "whatsapp": data.get("whatsapp", []),
            "regions": data.get("regions", []),
            "job_types": data.get("job_types", []),
            "jobs_published": data.get("jobs_published", 1),
            "first_seen": data.get("first_seen", now),
            "last_seen": data.get("last_seen", now),
            "complaints": data.get("complaints", 0),
            "fraud_reports": data.get("fraud_reports", 0),
            "spam_count": data.get("spam_count", 0),
            "operator_decisions": data.get("operator_decisions", []),
            "trust_score": data.get("trust_score", 0.5),
            "trust_signals": data.get("trust_signals", {"positive": [], "negative": []}),
            "verified": data.get("verified", False),
            "source": data.get("source", "unknown"),
            "notes": data.get("notes", ""),
            "created_at": now,
            "updated_at": now,
            "_history": data.get("_history", [{"action": "created", "timestamp": now}]),
        }
        self._write("employers", employer_id, record)
        for phone in record["phones"]:
            self._index_phone(phone, "employer", employer_id)
        for name in record["names"]:
            self._index_name(name, "employer", employer_id)
        for region in record["regions"]:
            self._index_location(region, "employer", employer_id)
        return employer_id

    def update_employer(self, employer_id: str, updates: dict, operator: str = "") -> dict | None:
        record = self._read("employers", employer_id)
        if not record:
            return None
        record["_history"].append({
            "action": "updated",
            "timestamp": _now(),
            "operator": operator,
            "changes": {k: updates.get(k) for k in updates if k != "_history"},
        })
        for key, value in updates.items():
            if key != "_history" and key in record:
                if isinstance(record[key], list) and isinstance(value, list):
                    for item in value:
                        if item not in record[key]:
                            record[key].append(item)
                elif isinstance(record[key], (int, float)) and isinstance(value, (int, float)):
                    record[key] = value
                elif isinstance(record[key], str):
                    record[key] = value
        record["updated_at"] = _now()
        self._write("employers", employer_id, record)
        return record

    def find_employer(self, employer_id: str) -> dict | None:
        return self._read("employers", employer_id)

    # ── Worker ──────────────────────────────────────────────────────────

    def create_worker(self, data: dict) -> str:
        worker_id = data.get("worker_id") or _make_id("wrk")
        now = _now()
        record = {
            "worker_id": worker_id,
            "names": data.get("names", []),
            "phones": data.get("phones", []),
            "group_size": data.get("group_size"),
            "experience": data.get("experience", []),
            "regions": data.get("regions", []),
            "languages": data.get("languages", []),
            "transport": data.get("transport", False),
            "previous_requests": data.get("previous_requests", 1),
            "last_active": data.get("last_active", now),
            "trust_score": data.get("trust_score", 0.5),
            "verified": data.get("verified", False),
            "source": data.get("source", "unknown"),
            "operator_notes": data.get("operator_notes", ""),
            "created_at": now,
            "updated_at": now,
            "_history": [{"action": "created", "timestamp": now}],
        }
        self._write("workers", worker_id, record)
        for phone in record["phones"]:
            self._index_phone(phone, "worker", worker_id)
        return worker_id

    def find_worker(self, worker_id: str) -> dict | None:
        return self._read("workers", worker_id)

    # ── Cases ───────────────────────────────────────────────────────────

    def create_case(self, data: dict) -> str:
        case_id = data.get("case_id") or _make_id("case")
        now = _now()
        record = {
            "case_id": case_id,
            "case_type": data.get("case_type", "complaint"),
            "employer_id": data.get("employer_id"),
            "worker_id": data.get("worker_id"),
            "description": data.get("description", ""),
            "evidence": data.get("evidence", []),
            "status": data.get("status", "open"),
            "resolution": data.get("resolution", ""),
            "operator_actions": data.get("operator_actions", []),
            "risk_level": data.get("risk_level", "medium"),
            "source": data.get("source", "unknown"),
            "created_at": now,
            "updated_at": now,
        }
        self._write("cases", case_id, record)
        return case_id

    def find_cases(self, employer_id: str | None = None, worker_id: str | None = None) -> list[dict]:
        cases = []
        for cid in self._list("cases"):
            case = self._read("cases", cid)
            if case:
                if employer_id and case.get("employer_id") != employer_id:
                    continue
                if worker_id and case.get("worker_id") != worker_id:
                    continue
                cases.append(case)
        return cases

    # ── Knowledge ───────────────────────────────────────────────────────

    def store_knowledge(self, data: dict) -> str:
        entry_id = data.get("entry_id") or _make_id("knw")
        now = _now()
        record = {
            "entry_id": entry_id,
            "category": data.get("category", "terminology"),
            "key": data.get("key", ""),
            "value": data.get("value", ""),
            "region": data.get("region"),
            "season": data.get("season"),
            "confidence": data.get("confidence", 0.5),
            "source": data.get("source", "unknown"),
            "verified": data.get("verified", False),
            "created_at": now,
            "updated_at": now,
        }
        self._write("knowledge", entry_id, record)
        return entry_id

    def query_knowledge(self, category: str | None = None, key: str | None = None) -> list[dict]:
        results = []
        for kid in self._list("knowledge"):
            entry = self._read("knowledge", kid)
            if entry:
                if category and entry.get("category") != category:
                    continue
                if key and key.lower() not in entry.get("key", "").lower():
                    continue
                results.append(entry)
        return results

    # ── Search ──────────────────────────────────────────────────────────

    def search_phone(self, phone: str) -> list[dict]:
        h = _hash_phone(phone)
        return self._indexes.get("phone_index", {}).get(h, [])

    def search_location(self, location: str) -> list[dict]:
        key = location.lower().strip()
        return self._indexes.get("location_index", {}).get(key, [])

    def search_name(self, name: str) -> list[dict]:
        key = name.lower().strip()
        return self._indexes.get("name_index", {}).get(key, [])

    # ── Trust ───────────────────────────────────────────────────────────

    def calculate_trust(self, entity_id: str, entity_type: str = "employer") -> float:
        record = self._read(f"{entity_type}s", entity_id)
        if not record:
            return 0.5

        score = 0.5
        signals = record.get("trust_signals", {})

        positive = len(signals.get("positive", []))
        negative = len(signals.get("negative", []))

        score += positive * 0.05
        score -= negative * 0.10

        if record.get("verified"):
            score += 0.10

        complaints = record.get("complaints", 0) + record.get("fraud_reports", 0)
        score -= complaints * 0.05

        return max(0.0, min(1.0, score))

    # ── Duplicate Detection ─────────────────────────────────────────────

    def detect_duplicate(self, phones: list[str] | None = None,
                         names: list[str] | None = None,
                         location: str | None = None) -> list[dict]:
        """Find potential duplicate records by phone, name, or location."""
        candidates = set()

        if phones:
            for phone in phones:
                for entry in self.search_phone(phone):
                    candidates.add((entry["type"], entry["id"]))

        if names:
            for name in names:
                for entry in self.search_name(name):
                    candidates.add((entry["type"], entry["id"]))

        results = []
        for entity_type, entity_id in candidates:
            record = self._read(f"{entity_type}s", entity_id)
            if record:
                results.append({"type": entity_type, "id": entity_id, "record": record})

        return results

    # ── Memory Context ──────────────────────────────────────────────────

    def get_context(self, phones: list[str] | None = None,
                    employer_name: str | None = None,
                    location: str | None = None) -> MemoryContext:
        """Build a MemoryContext for the Brain to use in decision-making."""
        ctx = MemoryContext()

        # Check phones
        if phones:
            for phone in phones:
                entries = self.search_phone(phone)
                for entry in entries:
                    if entry["type"] == "employer":
                        emp = self.find_employer(entry["id"])
                        if emp:
                            ctx.known_employer = emp
                            ctx.employer_trust = emp.get("trust_score", 0.5)
                            ctx.employer_complaints = emp.get("complaints", 0)
                            ctx.employer_history = emp.get("_history", [])[-5:]
                            ctx.operator_notes = emp.get("notes", "")
                    elif entry["type"] == "worker":
                        wrk = self.find_worker(entry["id"])
                        if wrk:
                            ctx.known_worker = wrk
                    ctx.known_phone = entry

        # Check name
        if employer_name:
            entries = self.search_name(employer_name)
            for entry in entries:
                if entry["type"] == "employer" and not ctx.known_employer:
                    ctx.known_employer = self.find_employer(entry["id"])

        # Check for duplicates
        if phones:
            duplicates = self.detect_duplicate(phones=phones, location=location)
            if duplicates:
                ctx.duplicate_lead = True

        # Knowledge: previous salary
        if location:
            knowledge = self.query_knowledge(category="salary", key=location)
            if knowledge:
                ctx.previous_salary_range = knowledge[0].get("value")

        return ctx
