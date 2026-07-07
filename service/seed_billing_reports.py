"""
Seeds a synthetic billing/revenue-cycle history for the Business Reports MVP
(Practice Overview, Provider Scorecard, Retention Funnel, Revenue Cycle).

Builds out ~90 days of recurring visit history per patient (completed /
no-show / cancelled, weighted realistically) on top of whatever appointments
already exist, then creates a BillingRecord for most completed visits —
deliberately skipping a few to simulate "unbilled encounter" leakage.

No real PHI/financials — everything here is synthetic. Safe to re-run; it
only adds history, it never touches the appointments other seed scripts rely
on for the Patient Registry / Clinical Chart demos.

Run AFTER seed.py, seed_synthetic_patients.py, and seed_upcoming_appointments.py,
from elevia-AlanBehrman/:
    python service/seed_billing_reports.py
"""
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal, ROUND_HALF_UP

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from sqlalchemy import select

from service.database import engine, SessionLocal
from service import models

SERVICE_CATALOG = {
    "psychiatry_consultation": {"category": "Psychiatric Medication Management", "cpt": "99214", "base_charge": 245},
    "therapy_consultation":    {"category": "Individual Psychotherapy",          "cpt": "90837", "base_charge": 175},
}
DEFAULT_SERVICE = {"category": "Individual Psychotherapy", "cpt": "90837", "base_charge": 175}

DENIAL_REASONS = [
    "Prior authorization required",
    "Timely filing limit exceeded",
    "Non-covered service for plan",
    "Missing/invalid diagnosis code",
    "Duplicate claim",
]

TODAY = datetime.now(timezone.utc)


def _seed(*parts) -> int:
    """Stable pseudo-random seed from strings — no reliance on Python's
    randomized hash() so reseeding is reproducible run to run."""
    return sum(ord(c) for p in parts for c in str(p))


def _money(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def visit_status(seed: int) -> str:
    r = seed % 100
    if r < 78:
        return "completed"
    if r < 90:
        return "no_show"
    return "cancelled"


def make_billing_record(db, appt, seed: int):
    svc = SERVICE_CATALOG.get(appt.appointment_type, DEFAULT_SERVICE)
    charge = _money(svc["base_charge"] * (0.9 + (seed % 21) / 100))  # +/-10% jitter
    allowed_factor = 0.65 + (seed % 21) / 100  # 0.65 - 0.85
    allowed = _money(charge * Decimal(str(allowed_factor)))
    adjustment = _money(charge - allowed)

    billing_date = appt.appointment_date.date() + timedelta(days=1 + seed % 3)
    status_roll = seed % 100

    if status_roll < 68:
        claim_status, paid, balance, denial_reason = "paid", allowed, _money(0), None
        payment_date = billing_date + timedelta(days=15 + seed % 31)
    elif status_roll < 82:
        claim_status, paid, balance, denial_reason = "pending", _money(0), allowed, None
        payment_date = None
    elif status_roll < 92:
        claim_status = "denied"
        paid, balance = _money(0), allowed
        denial_reason = DENIAL_REASONS[seed % len(DENIAL_REASONS)]
        payment_date = None
    else:
        claim_status, denial_reason = "partial", None
        paid = _money(allowed * Decimal(str(0.3 + (seed % 41) / 100)))
        balance = _money(allowed - paid)
        payment_date = billing_date + timedelta(days=20 + seed % 31)

    db.add(models.BillingRecord(
        appointment_id=appt.id,
        patient_id=appt.patient_id,
        provider_name=appt.provider_name,
        service_category=svc["category"],
        cpt_code=svc["cpt"],
        charge_amount=charge,
        allowed_amount=allowed,
        adjustment_amount=adjustment,
        paid_amount=paid,
        patient_balance=balance,
        claim_status=claim_status,
        denial_reason=denial_reason,
        billing_date=billing_date,
        payment_date=payment_date,
    ))


HISTORY_MARKER = "​"  # zero-width space prefix — invisible in the UI, marks script-generated rows for safe re-seeding


def backfill_visit_history(db, patient, primary_appt):
    """Generate additional past visits so retention/volume metrics have real
    signal instead of a single data point per patient. Patients whose only
    real visit is recent are left alone, so "new patient" volume stays a
    meaningful, non-zero signal instead of every patient looking established."""
    if primary_appt.appointment_date < TODAY and (TODAY - primary_appt.appointment_date).days <= 20:
        return []

    n_visits = 2 + _seed(patient.email, "n") % 5  # 2-6 additional past visits
    cadence_days = 12 + _seed(patient.email, "cadence") % 10  # ~12-21 days apart
    anchor = min(primary_appt.appointment_date, TODAY - timedelta(days=cadence_days))

    created = []
    for i in range(n_visits):
        visit_date = anchor - timedelta(days=cadence_days * (i + 1))
        if visit_date >= TODAY:
            continue
        seed = _seed(patient.email, "visit", i)
        status = visit_status(seed)
        appt = models.Appointment(
            id=uuid.uuid4(),
            patient_id=patient.id,
            appointment_type=primary_appt.appointment_type,
            appointment_date=visit_date,
            provider_name=primary_appt.provider_name,
            clinic_location=primary_appt.clinic_location,
            appointment_description=HISTORY_MARKER + (primary_appt.appointment_description or ""),
            patient_type="returning_recent",
            status=status,
            intake_link_token=str(uuid.uuid4()),
        )
        db.add(appt)
        created.append((appt, seed))
    return created


def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear any previously-seeded billing records + backfilled history visits
    # so this script is safely re-runnable without accumulating duplicates.
    db.query(models.BillingRecord).delete()
    history_rows = db.execute(
        select(models.Appointment).where(models.Appointment.appointment_description.like(f"{HISTORY_MARKER}%"))
    ).scalars().all()
    for a in history_rows:
        db.delete(a)
    db.commit()

    patients = db.execute(select(models.Patient)).scalars().all()
    total_billed = 0
    total_history_visits = 0

    for patient in patients:
        appts = db.execute(
            select(models.Appointment)
            .where(models.Appointment.patient_id == patient.id)
            .order_by(models.Appointment.appointment_date.asc())
        ).scalars().all()
        if not appts:
            continue

        past_appts = [a for a in appts if a.appointment_date and a.appointment_date < TODAY]
        reference_appt = past_appts[0] if past_appts else appts[0]

        # 1) Assign a realistic status to any already-past appointment still
        #    sitting at the "scheduled" default.
        for a in past_appts:
            if a.status == "scheduled":
                a.status = visit_status(_seed(patient.email, a.id))

        # 2) Backfill a recurring visit history behind the earliest past visit.
        new_appts = backfill_visit_history(db, patient, reference_appt)
        total_history_visits += len(new_appts)
        db.flush()

        # 3) Bill every completed visit (existing + newly backfilled), skipping
        #    ~1 in 12 to simulate unbilled-encounter leakage.
        all_completed = [a for a in past_appts if a.status == "completed"]
        all_completed += [a for a, _ in new_appts if a.status == "completed"]

        for a in all_completed:
            seed = _seed(patient.email, "bill", a.id)
            if seed % 12 == 0:
                continue  # deliberately unbilled
            make_billing_record(db, a, seed)
            total_billed += 1

    db.commit()
    print(f"Backfilled {total_history_visits} historical visits across {len(patients)} patients")
    print(f"Created {total_billed} billing records")
    db.close()


if __name__ == "__main__":
    seed()
