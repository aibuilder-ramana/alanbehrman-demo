"""
Synthetic demo data: patients, appointments, and form progress.

Providers are NOT synthetic — they come from service/providers.py, which
mirrors the real roster at https://www.alanbehrman.com/about/team/.

Run from the repo root:
    python -m service.seed_demo_data

Idempotent: patients are keyed by email, so re-running skips anyone already
present rather than duplicating them. Every patient created here uses an
@example.com address, which is what identifies the cohort as synthetic.

Appointment descriptions are deliberately worded to exercise the keyword
routing in crud.create_appointment — 'panic'/'worry' pull in the GAD-7,
'low mood'/'grief' pull in the PHQ-9, 'couples'/'marriage' the relational
intake, and so on — so the seeded packets vary the way real ones do.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone, date

from service.database import engine, SessionLocal
from service import models, crud, schemas, providers
from service.seed_billing_reports import make_billing_record, _seed as _billing_seed

random.seed(1729)

BASE_PACKET_ALWAYS_DONE = {"hipaa", "client_info"}


def _p(name: str) -> dict:
    for prov in providers.PROVIDERS:
        if prov["name"].startswith(name):
            return prov
    raise KeyError(name)


# (full_name, dob, gender, phone, provider, location, description, when_days, form_state)
#   when_days < 0 → past visit, > 0 → upcoming visit
#   form_state: "complete" | "partial" | "fresh"
COHORT = [
    # ── Marietta ────────────────────────────────────────────────────────────
    ("Daniel Okafor",     date(1986, 3, 14), "Male",   "(770) 555-0141",
     "Meredith Mitchell", providers.MARIETTA,
     "Medication management follow-up for depression and low mood", -21, "complete"),
    ("Priya Raghavan",    date(1994, 11, 2), "Female", "(770) 555-0142",
     "Rachel Barlev", providers.MARIETTA,
     "Ongoing anxiety and panic episodes at work", -14, "complete"),
    ("Marcus Trent",      date(1979, 6, 28), "Male",   "(770) 555-0143",
     "Tu Vo", providers.MARIETTA,
     "Grief counseling following loss of a parent", -35, "complete"),
    ("Helena Vasquez",    date(1991, 1, 19), "Female", "(770) 555-0144",
     "Whitney Rudd", providers.MARIETTA,
     "Couples therapy — communication and marriage concerns", 4, "partial"),
    ("Nathan Cole",       date(2001, 8, 7),  "Male",   "(770) 555-0145",
     "Silvia Lynch", providers.MARIETTA,
     "Initial intake — stress and sleep difficulty", 9, "fresh"),
    ("Bianca Ferrari",    date(1988, 12, 5), "Female", "(770) 555-0146",
     "Meredith Mitchell", providers.MARIETTA,
     "Psychiatric evaluation — persistent worry and restlessness", 2, "partial"),

    # ── Alpharetta ──────────────────────────────────────────────────────────
    ("Owen Delacroix",    date(1983, 4, 22), "Male",   "(678) 555-0151",
     "Ariella Peist", providers.ALPHARETTA,
     "Trauma-focused therapy, PTSD symptoms", -28, "complete"),
    ("Salma Haddad",      date(1997, 9, 30), "Female", "(678) 555-0152",
     "Cristina Lazaro", providers.ALPHARETTA,
     "Career and leadership coaching goals", -7, "complete"),
    ("Grant Whitmore",    date(1972, 2, 16), "Male",   "(678) 555-0153",
     "Kelly Villarreal", providers.ALPHARETTA,
     "Family therapy — parenting and relationship conflict", 6, "partial"),
    ("Tessa Nguyen",      date(1999, 5, 11), "Female", "(678) 555-0154",
     "Mona Chandra", providers.ALPHARETTA,
     "Psychological testing and evaluation", 13, "fresh"),
    ("Julian Reyes",      date(1990, 10, 3), "Male",   "(678) 555-0155",
     "Jamie Goldberg", providers.ALPHARETTA,
     "Anxiety management and mindfulness work", -10, "complete"),

    # ── Duluth ──────────────────────────────────────────────────────────────
    ("Amara Osei",        date(1985, 7, 25), "Female", "(770) 555-0161",
     "Dr. Ramakanth Vemuluri", providers.DULUTH,
     "Medication review — depression, coordinate records with physician", -17, "complete"),
    ("Victor Lindqvist",  date(1968, 11, 8), "Male",   "(770) 555-0162",
     "Jessica Bosson", providers.DULUTH,
     "Cognitive evaluation and testing", -42, "complete"),
    ("Rosa Milanovic",    date(1993, 3, 2),  "Female", "(770) 555-0163",
     "Kailyn Blackmon", providers.DULUTH,
     "Initial consult — hopelessness and loss of interest", 3, "partial"),
    ("Elias Brandt",      date(2000, 1, 27), "Male",   "(770) 555-0164",
     "Sheldon Kay", providers.DULUTH,
     "Counseling for academic stress and tension", 11, "fresh"),
    ("Noor Al-Fayed",     date(1996, 6, 18), "Female", "(770) 555-0165",
     "Dr. Ramakanth Vemuluri", providers.DULUTH,
     "Psychiatry follow-up — panic and palpitations", 7, "partial"),

    # ── Dunwoody ────────────────────────────────────────────────────────────
    ("Theodore Ngata",    date(1981, 9, 14), "Male",   "(678) 555-0171",
     "Dr. Ramakanth Vemuluri", providers.DUNWOODY,
     "Medication management — mood stabilization", -25, "complete"),
    ("Clara Benedetti",   date(1989, 12, 21), "Female", "(678) 555-0172",
     "Dr. Ramakanth Vemuluri", providers.DUNWOODY,
     "Psychiatric intake — nervousness and dread", 5, "fresh"),

    # ── New Orleans ─────────────────────────────────────────────────────────
    ("Beauregard Thibault", date(1975, 5, 9), "Male",  "(504) 555-0181",
     "Ashley Lee", providers.NEW_ORLEANS,
     "Medication management for major depressive disorder", -19, "complete"),
    ("Simone Aucoin",     date(1992, 8, 16), "Female", "(504) 555-0182",
     "Ashlie Martinez", providers.NEW_ORLEANS,
     "Individual therapy — trauma and fear response", -12, "complete"),
    ("Marcel Duplantier", date(1987, 2, 4),  "Male",   "(504) 555-0183",
     "David Dolese", providers.NEW_ORLEANS,
     "Relationship counseling with partner", 8, "partial"),
    ("Genevieve Boudreaux", date(1998, 10, 30), "Female", "(504) 555-0184",
     "Rae Sidlauskas", providers.NEW_ORLEANS,
     "Initial intake — worry and social avoidance", 15, "fresh"),
    ("Isaac Fontenot",    date(1970, 4, 12), "Male",   "(504) 555-0185",
     "Ashley LeGros", providers.NEW_ORLEANS,
     "Counseling — career transition and life goals", -5, "complete"),
]


def _email(full_name: str) -> str:
    return full_name.lower().replace(" ", ".").replace("'", "") + "@example.com"


def _apply_form_state(db, appt, state: str, appt_date: datetime) -> tuple[int, int]:
    """Mark the appointment's auto-attached forms to reflect `state`.
    Returns (completed, in_progress)."""
    rows = db.query(models.PatientForm).filter(
        models.PatientForm.appointment_id == appt.id
    ).all()

    completed = in_progress = 0
    for idx, pf in enumerate(rows):
        if state == "complete":
            done = True
        elif state == "partial":
            # leave a realistic tail unfinished
            done = pf.form_id in BASE_PACKET_ALWAYS_DONE or idx < max(1, len(rows) // 2)
        else:  # fresh
            done = pf.form_id in BASE_PACKET_ALWAYS_DONE and idx == 0

        if done:
            pf.status = "completed"
            pf.intake_method = "ai" if idx % 3 == 0 else "manual"
            pf.started_at = appt_date - timedelta(days=2, hours=idx)
            pf.completed_at = appt_date - timedelta(days=2, hours=max(0, idx - 1))
            completed += 1
        elif state == "partial" and idx == len(rows) - 1:
            pf.status = "in_progress"
            pf.intake_method = "manual"
            pf.started_at = appt_date - timedelta(days=1)
            in_progress += 1
        else:
            pf.status = "not_started"

    db.commit()
    return completed, in_progress


def seed() -> None:
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    created = skipped = billed = 0
    tot_forms = tot_done = tot_prog = 0
    by_type = {providers.PSYCHIATRIST: 0, providers.THERAPIST: 0}

    for (full_name, dob, gender, phone, prov_name, location,
         description, when_days, form_state) in COHORT:
        email = _email(full_name)
        exists = db.query(models.Patient).filter(models.Patient.email == email).first()
        if exists:
            print(f"  skip (exists): {full_name}")
            skipped += 1
            continue

        provider = _p(prov_name)
        patient = crud.create_patient(db, schemas.PatientCreate(
            full_name=full_name,
            first_name=full_name.split()[0],
            dob=dob,
            gender=gender,
            email=email,
            phone=phone,
        ))

        appt_date = now + timedelta(days=when_days,
                                    hours=random.choice([-3, -1, 0, 1, 2]))
        appt = crud.create_appointment(db, schemas.AppointmentCreate(
            patient_id=patient.id,
            appointment_type=providers.appointment_type_for(provider),
            appointment_date=appt_date,
            provider_name=provider["name"],
            clinic_location=location,
            appointment_description=description,
        ))

        # A past visit is a billed encounter. Without this the provider
        # scorecard shows these clinicians at $0 and drags revenue/visit down.
        if when_days < 0:
            appt.status = "completed"
            make_billing_record(db, appt, _billing_seed(full_name, provider["name"]))
            billed += 1
            db.commit()

        done, prog = _apply_form_state(db, appt, form_state, appt_date)
        n_forms = db.query(models.PatientForm).filter(
            models.PatientForm.appointment_id == appt.id
        ).count()

        created += 1
        by_type[provider["type"]] += 1
        tot_forms += n_forms
        tot_done += done
        tot_prog += prog

        when = f"{abs(when_days)}d {'ago' if when_days < 0 else 'ahead'}"
        print(f"  + {full_name:22} {provider['type'][:5]:6} {provider['name'][:30]:32}"
              f" {location[:14]:16} {when:9} forms {done}/{n_forms}")

    print(f"\n  created {created}, skipped {skipped}")
    print(f"  by provider type: {by_type[providers.PSYCHIATRIST]} psychiatry, "
          f"{by_type[providers.THERAPIST]} therapy")
    print(f"  forms: {tot_forms} attached, {tot_done} completed, {tot_prog} in progress")
    print(f"  billing records for {billed} completed visits")
    db.close()


if __name__ == "__main__":
    seed()
