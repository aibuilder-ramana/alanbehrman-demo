"""
Generates synthetic test patients + appointments covering multiple scenarios.

Run from elevia-1medicalservices/:
    python service/gen_test_users.py

Prints intake URLs for each scenario.
"""
import os, sys
from datetime import datetime, timezone, timedelta, date

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from service.database import engine, SessionLocal
from service import models, crud, schemas
from sqlalchemy import select, text

BASE_URL = "http://localhost:8020"


def migrate_schema(engine):
    """Add new columns to appointments if they don't exist yet."""
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS appointment_description TEXT",
            "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS patient_type VARCHAR(30) NOT NULL DEFAULT 'new'",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()


def add_forms_if_missing(db):
    """Ensure PHQ-9, GAD-7 and all form definitions exist."""
    new_forms = [
        models.FormDefinition(
            id="phq9",
            title="PHQ-9 Depression Screening",
            description="9-item Patient Health Questionnaire for depression. Flags moderate-to-severe risk for clinical follow-up.",
            appointment_types=None,
            category="required",
            is_required=True,
            estimated_minutes=2,
            sort_order=9,
            file_template="Knowledge/forms/phq9_rag_elevia.md",
        ),
        models.FormDefinition(
            id="gad7",
            title="GAD-7 Anxiety Screening",
            description="7-item Generalized Anxiety Disorder questionnaire. Scores ≥10 trigger clinical review.",
            appointment_types=None,
            category="required",
            is_required=True,
            estimated_minutes=2,
            sort_order=10,
            file_template="Knowledge/forms/gad7_rag_elevia.md",
        ),
    ]
    added = 0
    for f in new_forms:
        if not db.get(models.FormDefinition, f.id):
            db.add(f)
            added += 1
    db.commit()
    if added:
        print(f"  ✓ Added {added} new form definitions (PHQ-9, GAD-7)")


def make_patient(db, first, last, dob_year, dob_month, dob_day, gender, email):
    return crud.create_patient(db, schemas.PatientCreate(
        full_name=f"{first} {last}",
        first_name=first,
        dob=date(dob_year, dob_month, dob_day),
        gender=gender,
        email=email,
        phone="(425) 555-0100",
    ))


def make_appointment(db, patient_id, appt_type, days_from_now, provider, location, description=None):
    appt_date = datetime.now(timezone.utc) + timedelta(days=days_from_now)
    return crud.create_appointment(db, schemas.AppointmentCreate(
        patient_id=patient_id,
        appointment_type=appt_type,
        appointment_date=appt_date,
        provider_name=provider,
        clinic_location=location,
        appointment_description=description,
    ))


def mark_forms_completed(db, appointment_id, form_ids: list):
    """Pre-complete specific forms to simulate a returning patient."""
    from datetime import datetime, timezone
    rows = db.execute(
        select(models.PatientForm)
        .where(models.PatientForm.appointment_id == appointment_id)
    ).scalars().all()
    for pf in rows:
        if pf.form_id in form_ids:
            pf.status = "completed"
            pf.started_at = datetime.now(timezone.utc) - timedelta(hours=2)
            pf.completed_at = datetime.now(timezone.utc) - timedelta(hours=1)
            pf.intake_method = "manual"
    db.commit()


def count_forms(db, appointment_id):
    rows = db.execute(
        select(models.PatientForm).where(models.PatientForm.appointment_id == appointment_id)
    ).scalars().all()
    total = len(rows)
    done  = sum(1 for r in rows if r.status == "completed")
    return total, done


def run():
    models.Base.metadata.create_all(bind=engine)
    migrate_schema(engine)   # add new columns if not present
    db = SessionLocal()

    print("\n" + "─" * 65)
    print("  Elevia 1 Stop Medical — Synthetic Test Users")
    print("─" * 65)

    add_forms_if_missing(db)

    scenarios = []

    # ── 1. New patient — Immigration Medical Exam ─────────────────────────
    p1 = make_patient(db, "Amara", "Okafor", 1988, 6, 15, "Female", "amara.okafor@example.com")
    a1 = make_appointment(db, p1.id, "immigration_medical_exam", 7, "Dr. Anjali Desai, MD", "Kent, WA",
                          description="Immigration medical exam for green card adjustment of status (Form I-485). First-time applicant, no prior US medical records.")
    t1, d1 = count_forms(db, a1.id)
    scenarios.append({
        "label": "1. New patient — Immigration Medical Exam",
        "name": p1.full_name,
        "forms": f"{d1}/{t1} completed (brand new)",
        "token": a1.intake_link_token,
    })

    # ── 2. Returning patient — Immigration Medical Exam (3 forms done) ───
    p2 = make_patient(db, "David", "Nguyen", 1995, 3, 22, "Male", "david.nguyen@example.com")
    a2 = make_appointment(db, p2.id, "immigration_medical_exam", 5, "Dr. Anjali Desai, MD", "Kent, WA",
                          description="Immigration medical exam for spousal green card (CR-1 visa). Vaccination records partially available.")
    mark_forms_completed(db, a2.id, ["brief_i693", "hipaa", "vaccine"])
    t2, d2 = count_forms(db, a2.id)
    scenarios.append({
        "label": "2. Returning patient — Immigration (3 forms pre-completed)",
        "name": p2.full_name,
        "forms": f"{d2}/{t2} completed",
        "token": a2.intake_link_token,
    })

    # ── 3. New patient — Primary Care Visit ──────────────────────────────
    p3 = make_patient(db, "Sofia", "Martinez", 1979, 11, 4, "Female", "sofia.martinez@example.com")
    a3 = make_appointment(db, p3.id, "primary_care", 14, "Dr. James Thornton, MD", "Bellevue, WA",
                          description="New patient establishing primary care. Reports chronic lower back pain, fatigue, and occasional headaches. Last saw a doctor 2 years ago.")
    t3, d3 = count_forms(db, a3.id)
    scenarios.append({
        "label": "3. New patient — Primary Care Visit",
        "name": p3.full_name,
        "forms": f"{d3}/{t3} completed (brand new)",
        "token": a3.intake_link_token,
    })

    # ── 4. Returning patient — Primary Care (most forms done) ────────────
    p4 = make_patient(db, "Marcus", "Johnson", 1962, 8, 30, "Male", "marcus.johnson@example.com")
    a4 = make_appointment(db, p4.id, "primary_care", 3, "Dr. James Thornton, MD", "Bellevue, WA",
                          description="Follow-up for hypertension and Type 2 diabetes management. Patient reports improved BP readings. Medication refill needed for metformin and lisinopril.")
    mark_forms_completed(db, a4.id, ["full_intake", "vaccine", "hipaa", "phq9", "gad7"])
    t4, d4 = count_forms(db, a4.id)
    scenarios.append({
        "label": "4. Returning patient — Primary Care (5 of 7 done)",
        "name": p4.full_name,
        "forms": f"{d4}/{t4} completed",
        "token": a4.intake_link_token,
    })

    # ── 5. New patient — Annual Physical ─────────────────────────────────
    p5 = make_patient(db, "Emily", "Chen", 1990, 1, 17, "Female", "emily.chen@example.com")
    a5 = make_appointment(db, p5.id, "annual_physical", 10, "Dr. Priya Kapoor, MD", "Kent, WA",
                          description="Annual wellness exam. Patient in good general health. Requesting routine labs — CBC, metabolic panel, thyroid, and cholesterol screen. No current complaints.")
    t5, d5 = count_forms(db, a5.id)
    scenarios.append({
        "label": "5. New patient — Annual Physical",
        "name": p5.full_name,
        "forms": f"{d5}/{t5} completed (brand new)",
        "token": a5.intake_link_token,
    })

    # ── 6. New patient — Pre-Employment Physical ──────────────────────────
    p6 = make_patient(db, "Raj", "Patel", 2000, 9, 5, "Male", "raj.patel@example.com")
    a6 = make_appointment(db, p6.id, "pre_employment", 2, "Dr. Priya Kapoor, MD", "Bellevue, WA",
                          description="Pre-employment physical for warehouse logistics role. Employer requires drug screen, vision and hearing test, and lift-capacity clearance.")
    t6, d6 = count_forms(db, a6.id)
    scenarios.append({
        "label": "6. New patient — Pre-Employment Physical",
        "name": p6.full_name,
        "forms": f"{d6}/{t6} completed (brand new)",
        "token": a6.intake_link_token,
    })

    # ── 7. Returning patient — almost complete (1 remaining) ─────────────
    p7 = make_patient(db, "Fatima", "Al-Hassan", 1985, 4, 12, "Female", "fatima.alhassan@example.com")
    a7 = make_appointment(db, p7.id, "immigration_medical_exam", 1, "Dr. Anjali Desai, MD", "Kent, WA",
                          description="Immigration medical exam for green card adjustment of status. Appointment tomorrow — patient has completed most forms, one outstanding.")
    all_pf = db.execute(
        select(models.PatientForm, models.FormDefinition)
        .join(models.FormDefinition)
        .where(models.PatientForm.appointment_id == a7.id)
        .order_by(models.FormDefinition.sort_order)
    ).all()
    all_form_ids = [fd.id for _, fd in all_pf]
    mark_forms_completed(db, a7.id, all_form_ids[:-1])
    t7, d7 = count_forms(db, a7.id)
    scenarios.append({
        "label": "7. Almost done — 1 form remaining (appt tomorrow!)",
        "name": p7.full_name,
        "forms": f"{d7}/{t7} completed",
        "token": a7.intake_link_token,
    })

    # ── 8. Returning patient RECENT (< 3 yrs) → only Patient Update Form ─
    p8 = make_patient(db, "Kenji", "Tanaka", 1987, 7, 20, "Male", "kenji.tanaka@example.com")
    # Prior visit 8 months ago — makes patient returning_recent
    make_appointment(db, p8.id, "primary_care", -240, "Dr. James Thornton, MD", "Bellevue, WA",
                     description="Annual wellness visit. No acute complaints.")
    # New appointment — crud detects returning_recent, serves only update form
    a8 = make_appointment(db, p8.id, "primary_care", 14, "Dr. James Thornton, MD", "Bellevue, WA",
                          description="Follow-up for blood pressure monitoring. Patient reports BP well controlled.")
    t8, d8 = count_forms(db, a8.id)
    scenarios.append({
        "label": "8. Returning patient (recent, < 3 yrs) → Patient Update Form only",
        "name": p8.full_name,
        "forms": f"{d8}/{t8} completed (update form only)",
        "token": a8.intake_link_token,
        "patient_type": a8.patient_type,
    })

    # ── 9. Returning patient STALE (> 3 yrs) → full intake, all forms ────
    p9 = make_patient(db, "Carmen", "Vega", 1975, 12, 1, "Female", "carmen.vega@example.com")
    # Create a prior appointment, then backdate it to 4 years ago
    prior_a9 = make_appointment(db, p9.id, "primary_care", 0, "Dr. Priya Kapoor, MD", "Kent, WA",
                                description="Old visit.")
    db.execute(
        text("UPDATE appointments SET created_at = now() - INTERVAL '4 years' WHERE id = :id"),
        {"id": str(prior_a9.id)}
    )
    db.commit()
    # New appointment — crud detects returning_stale, serves full intake
    a9 = make_appointment(db, p9.id, "primary_care", 10, "Dr. Priya Kapoor, MD", "Kent, WA",
                          description="Annual physical. Patient returning after 4-year gap. Full records refresh needed.")
    t9, d9 = count_forms(db, a9.id)
    scenarios.append({
        "label": "9. Returning patient (stale, > 3 yrs) → Full intake all forms",
        "name": p9.full_name,
        "forms": f"{d9}/{t9} completed (full intake)",
        "token": a9.intake_link_token,
        "patient_type": a9.patient_type,
    })

    # ── 10. New patient — depression symptoms → PHQ-9 included ───────────
    p10 = make_patient(db, "Jordan", "Williams", 1994, 5, 8, "Female", "jordan.williams@example.com")
    a10 = make_appointment(db, p10.id, "primary_care", 7, "Dr. James Thornton, MD", "Bellevue, WA",
                           description="Patient reports persistent low mood and feeling depressed for the past 3 months. Difficulty sleeping, low energy, loss of interest in daily activities.")
    t10, d10 = count_forms(db, a10.id)
    scenarios.append({
        "label": "10. New patient — depression symptoms → PHQ-9 included",
        "name": p10.full_name,
        "forms": f"{d10}/{t10} (includes PHQ-9)",
        "token": a10.intake_link_token,
    })

    # ── 11. New patient — anxiety symptoms → GAD-7 included ──────────────
    p11 = make_patient(db, "Arjun", "Sharma", 1998, 2, 14, "Male", "arjun.sharma@example.com")
    a11 = make_appointment(db, p11.id, "primary_care", 5, "Dr. Priya Kapoor, MD", "Kent, WA",
                           description="Patient experiencing significant anxiety and panic attacks. Reports constant worry about work and finances. Difficulty concentrating and feeling restless.")
    t11, d11 = count_forms(db, a11.id)
    scenarios.append({
        "label": "11. New patient — anxiety symptoms → GAD-7 included",
        "name": p11.full_name,
        "forms": f"{d11}/{t11} (includes GAD-7)",
        "token": a11.intake_link_token,
    })

    # ── 12. Returning recent + depression + anxiety → update + PHQ-9 + GAD-7
    p12 = make_patient(db, "Leila", "Nasser", 1985, 9, 25, "Female", "leila.nasser@example.com")
    make_appointment(db, p12.id, "primary_care", -180, "Dr. Priya Kapoor, MD", "Kent, WA",
                     description="Routine follow-up. Patient doing well.")
    a12 = make_appointment(db, p12.id, "primary_care", 3, "Dr. Priya Kapoor, MD", "Kent, WA",
                           description="Patient reporting increased anxiety, depression, and difficulty coping following recent bereavement. Feeling hopeless and extremely anxious about the future.")
    t12, d12 = count_forms(db, a12.id)
    scenarios.append({
        "label": "12. Returning recent + depression + anxiety → Update + PHQ-9 + GAD-7",
        "name": p12.full_name,
        "forms": f"{d12}/{t12} (update + PHQ-9 + GAD-7)",
        "token": a12.intake_link_token,
        "patient_type": a12.patient_type,
    })

    db.close()

    # ── Print links ───────────────────────────────────────────────────────
    print()
    for s in scenarios:
        print(f"  {s['label']}")
        print(f"  Patient: {s['name']}  |  Forms: {s['forms']}")
        print(f"  {BASE_URL}/?t={s['token']}")
        print()

    print("─" * 65)
    print(f"  {len(scenarios)} intake links generated above.")
    print("─" * 65 + "\n")


if __name__ == "__main__":
    run()
