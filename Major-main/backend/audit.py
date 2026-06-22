"""
Audit Module
────────────
Immutable append-only audit trail for all broker events.
Every compliance check, cost evaluation, provisioning action, and decision
is recorded with a version stamp so historical decisions can be reproduced.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session
from models import AuditLog

RULE_VERSION = "2026-v1"


def log_event(
    db: Session,
    event_type: str,
    payload: dict[str, Any],
    decision_id: str | None = None,
    actor: str = "system",
) -> AuditLog:
    entry = AuditLog(
        id=str(uuid.uuid4()),
        decision_id=decision_id,
        event_type=event_type,
        actor=actor,
        payload=payload,
        rule_version=RULE_VERSION,
        timestamp=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


EVENT_TYPES = {
    "BROKER_REQUEST_RECEIVED": "broker_request_received",
    "COMPLIANCE_CHECK_COMPLETED": "compliance_check_completed",
    "COST_ANALYSIS_COMPLETED": "cost_analysis_completed",
    "DECISION_CREATED": "decision_created",
    "DECISION_APPROVED": "decision_approved",
    "DECISION_REJECTED": "decision_rejected",
    "PROVISIONING_STARTED": "provisioning_started",
    "PROVISIONING_DRY_RUN": "provisioning_dry_run",
    "PROVISIONING_APPROVED": "provisioning_approved",
    "PROVISIONING_COMPLETED": "provisioning_completed",
    "PROVISIONING_FAILED": "provisioning_failed",
    "REPORT_EXPORTED": "report_exported",
}
