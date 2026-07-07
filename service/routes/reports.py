"""
Business Reports (MVP) — Practice Overview, Provider Scorecard, Retention
Funnel, and Revenue Cycle, computed from appointments + billing_records only
(no clinical notes). Owner-facing; synthetic data for now.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from service.database import get_db
from service import models

router = APIRouter()

RESOLVED_STATUSES = {"completed", "no_show", "cancelled"}
NEW_PATIENT_WINDOW_DAYS = 30
ACTIVE_PATIENT_WINDOW_DAYS = 60
AR_THRESHOLD = 100  # flag patient balances over this amount as a leakage signal
SERVICE_AVG_CHARGE = {
    "psychiatry_consultation": 245,
    "therapy_consultation": 175,
}


def _f(x) -> float:
    return float(x) if x is not None else 0.0


@router.get("/reports/dashboard")
def get_business_reports_dashboard(db: Session = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    appts = db.execute(select(models.Appointment)).scalars().all()
    billing = db.execute(select(models.BillingRecord)).scalars().all()
    billing_by_appt = {b.appointment_id: b for b in billing}

    # ── Practice Overview ────────────────────────────────────────────────────
    completed = [a for a in appts if a.status == "completed"]
    no_shows = [a for a in appts if a.status == "no_show"]
    cancelled = [a for a in appts if a.status == "cancelled"]
    resolved = completed + no_shows + cancelled
    scheduled_future = [a for a in appts if a.status == "scheduled" and a.appointment_date and a.appointment_date >= now]
    next_4_weeks = [a for a in scheduled_future if a.appointment_date <= now + timedelta(days=28)]

    # Per-patient completed-visit counts (drives retention + new/active logic)
    completed_by_patient: dict = {}
    first_visit_by_patient: dict = {}
    last_completed_by_patient: dict = {}
    for a in appts:
        if not a.appointment_date:
            continue
        first_visit_by_patient[a.patient_id] = min(first_visit_by_patient.get(a.patient_id, a.appointment_date), a.appointment_date)
        if a.status == "completed":
            completed_by_patient[a.patient_id] = completed_by_patient.get(a.patient_id, 0) + 1
            last_completed_by_patient[a.patient_id] = max(last_completed_by_patient.get(a.patient_id, a.appointment_date), a.appointment_date)

    new_patients = sum(
        1 for pid, first in first_visit_by_patient.items()
        if 0 <= (now - first).days <= NEW_PATIENT_WINDOW_DAYS
    )
    has_future = {a.patient_id for a in scheduled_future}
    active_patients = sum(
        1 for pid in {a.patient_id for a in appts}
        if pid in has_future or (
            pid in last_completed_by_patient and (now - last_completed_by_patient[pid]).days <= ACTIVE_PATIENT_WINDOW_DAYS
        )
    )

    revenue_collected = sum(_f(b.paid_amount) for b in billing)
    revenue_per_visit = revenue_collected / len(completed) if completed else 0.0
    no_show_rate = len(no_shows) / len(resolved) if resolved else 0.0

    intake_patients = set(completed_by_patient.keys())
    second_visit_patients = {pid for pid, c in completed_by_patient.items() if c >= 2}
    fourth_visit_patients = {pid for pid, c in completed_by_patient.items() if c >= 4}
    second_visit_rate = len(second_visit_patients) / len(intake_patients) if intake_patients else 0.0
    fourth_visit_rate = len(fourth_visit_patients) / len(intake_patients) if intake_patients else 0.0

    # Provider utilization: completed / (completed + no_show + cancelled) per provider, averaged
    providers = sorted({a.provider_name for a in appts if a.provider_name})
    util_values = []
    for p in providers:
        p_resolved = [a for a in resolved if a.provider_name == p]
        p_completed = [a for a in p_resolved if a.status == "completed"]
        if p_resolved:
            util_values.append(len(p_completed) / len(p_resolved))
    avg_utilization = sum(util_values) / len(util_values) if util_values else 0.0

    # ── A/R aging (unpaid/partial balances) ──────────────────────────────────
    ar_buckets = {"0_30": 0.0, "31_60": 0.0, "61_90": 0.0, "90_plus": 0.0}
    for b in billing:
        bal = _f(b.patient_balance)
        if bal <= 0:
            continue
        age_days = (now.date() - b.billing_date).days
        if age_days <= 30:
            ar_buckets["0_30"] += bal
        elif age_days <= 60:
            ar_buckets["31_60"] += bal
        elif age_days <= 90:
            ar_buckets["61_90"] += bal
        else:
            ar_buckets["90_plus"] += bal

    denied = [b for b in billing if b.claim_status == "denied"]
    denial_rate = len(denied) / len(billing) if billing else 0.0
    unbilled = [a for a in completed if a.id not in billing_by_appt]
    high_balance_count = sum(1 for b in billing if _f(b.patient_balance) > AR_THRESHOLD)

    gross_charges = sum(_f(b.charge_amount) for b in billing)
    adjustments = sum(_f(b.adjustment_amount) for b in billing)
    net_revenue = sum(_f(b.allowed_amount) for b in billing)
    collection_rate = revenue_collected / net_revenue if net_revenue else 0.0

    unbilled_value = sum(
        _f(SERVICE_AVG_CHARGE.get(a.appointment_type, 175)) for a in unbilled
    )
    no_show_value = sum(
        _f(SERVICE_AVG_CHARGE.get(a.appointment_type, 175)) for a in no_shows
    )
    denied_unpaid_value = sum(_f(b.allowed_amount) for b in denied)
    revenue_leakage_estimate = unbilled_value + no_show_value + denied_unpaid_value

    # ── Provider scorecard ───────────────────────────────────────────────────
    provider_rows = []
    for p in providers:
        p_appts = [a for a in appts if a.provider_name == p]
        p_completed = [a for a in p_appts if a.status == "completed"]
        p_no_show = [a for a in p_appts if a.status == "no_show"]
        p_cancelled = [a for a in p_appts if a.status == "cancelled"]
        p_resolved = p_completed + p_no_show + p_cancelled
        p_scheduled = [a for a in p_appts if a.status == "scheduled" and a.appointment_date and a.appointment_date >= now]
        p_billing = [b for b in billing if b.provider_name == p]
        p_revenue = sum(_f(b.paid_amount) for b in p_billing)
        p_unbilled = [a for a in p_completed if a.id not in billing_by_appt]
        p_patients = {a.patient_id for a in p_appts}
        p_new_intakes = sum(
            1 for pid in p_patients
            if pid in first_visit_by_patient and 0 <= (now - first_visit_by_patient[pid]).days <= NEW_PATIENT_WINDOW_DAYS
        )
        p_active = sum(
            1 for pid in p_patients
            if pid in has_future or (pid in last_completed_by_patient and (now - last_completed_by_patient[pid]).days <= ACTIVE_PATIENT_WINDOW_DAYS)
        )

        provider_rows.append({
            "provider_name": p,
            "completed_visits": len(p_completed),
            "scheduled_visits": len(p_scheduled),
            "new_intakes": p_new_intakes,
            "active_caseload": p_active,
            "revenue_collected": round(p_revenue, 2),
            "revenue_per_visit": round(p_revenue / len(p_completed), 2) if p_completed else 0.0,
            "no_show_rate": round(len(p_no_show) / len(p_resolved), 4) if p_resolved else 0.0,
            "cancellation_rate": round(len(p_cancelled) / len(p_resolved), 4) if p_resolved else 0.0,
            "utilization": round(len(p_completed) / len(p_resolved), 4) if p_resolved else 0.0,
            "unbilled_encounters": len(p_unbilled),
        })
    provider_rows.sort(key=lambda r: r["revenue_collected"], reverse=True)

    # ── Retention funnel ─────────────────────────────────────────────────────
    all_patient_ids = {a.patient_id for a in appts}
    active_30 = sum(1 for pid in intake_patients if pid in last_completed_by_patient and (now - last_completed_by_patient[pid]).days <= 30 or pid in has_future)
    active_90 = sum(1 for pid in intake_patients if pid in last_completed_by_patient and (now - last_completed_by_patient[pid]).days <= 90 or pid in has_future)
    funnel = [
        {"stage": "Intake Scheduled",  "count": len(all_patient_ids)},
        {"stage": "Intake Completed",  "count": len(intake_patients)},
        {"stage": "2nd Visit",         "count": len(second_visit_patients)},
        {"stage": "4th Visit",         "count": len(fourth_visit_patients)},
        {"stage": "Active (30d)",      "count": active_30},
        {"stage": "Active (90d)",      "count": active_90},
    ]

    return {
        "overview": {
            "completed_visits": len(completed),
            "scheduled_next_4_weeks": len(next_4_weeks),
            "new_patients": new_patients,
            "active_patients": active_patients,
            "revenue_collected": round(revenue_collected, 2),
            "revenue_per_visit": round(revenue_per_visit, 2),
            "no_show_rate": round(no_show_rate, 4),
            "provider_utilization": round(avg_utilization, 4),
            "second_visit_retention": round(second_visit_rate, 4),
            "fourth_visit_retention": round(fourth_visit_rate, 4),
            "ar_total": round(sum(ar_buckets.values()), 2),
        },
        "providers": provider_rows,
        "retention_funnel": funnel,
        "revenue_cycle": {
            "gross_charges": round(gross_charges, 2),
            "adjustments": round(adjustments, 2),
            "net_revenue": round(net_revenue, 2),
            "payments_collected": round(revenue_collected, 2),
            "collection_rate": round(collection_rate, 4),
            "ar_aging": {k: round(v, 2) for k, v in ar_buckets.items()},
            "denial_rate": round(denial_rate, 4),
            "unbilled_encounters": len(unbilled),
            "high_balance_accounts": high_balance_count,
            "revenue_leakage_estimate": round(revenue_leakage_estimate, 2),
        },
    }
