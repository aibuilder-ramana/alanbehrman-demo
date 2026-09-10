"""
Real provider roster for Alan Behrman & Associates.

Source: https://www.alanbehrman.com/about/team/ (grouped by office location).
These are real people — do not generate or invent entries here. Synthetic
patients and appointments reference this roster by name.

Two provider types drive scheduling and billing:
  psychiatrist — psychiatric medication providers (MD / PMHNP-BC)
  therapist    — therapy, counseling, and psychological testing

`appointment_type` maps 1:1 off the provider type and must stay in sync with
SERVICE_AVG_CHARGE in service/routes/reports.py.
"""
from __future__ import annotations

PSYCHIATRIST = "psychiatrist"
THERAPIST = "therapist"

APPOINTMENT_TYPE_FOR = {
    PSYCHIATRIST: "psychiatry_consultation",
    THERAPIST: "therapy_consultation",
}

MARIETTA = "Marietta, GA"
ALPHARETTA = "Alpharetta, GA"
DULUTH = "Duluth, GA"
DUNWOODY = "Dunwoody, GA"
NEW_ORLEANS = "New Orleans, LA"

LOCATIONS = [MARIETTA, ALPHARETTA, DULUTH, DUNWOODY, NEW_ORLEANS]

# npi is only recorded for providers already referenced by existing seeded
# clinical notes; the rest bill under the practice group.
PROVIDERS = [
    # ── Psychiatric medication providers ────────────────────────────────────
    {"name": "Dr. Ramakanth Vemuluri, MD",       "type": PSYCHIATRIST, "credential": "MD",
     "specialty": "Psychiatry & Primary Care",   "npi": "1720384950", "locations": [DULUTH, DUNWOODY]},
    {"name": "Meredith Mitchell, PMHNP-BC",      "type": PSYCHIATRIST, "credential": "PMHNP-BC",
     "specialty": "Psychiatric Mental Health",   "npi": "1932847561", "locations": [MARIETTA]},
    {"name": "Ashley Lee, PMHNP-BC",             "type": PSYCHIATRIST, "credential": "PMHNP-BC",
     "specialty": "Psychiatric Mental Health",   "npi": None,         "locations": [NEW_ORLEANS]},

    # ── Therapists, counselors, psychologists ───────────────────────────────
    {"name": "Alan Behrman, Ph.D",               "type": THERAPIST, "credential": "Ph.D",
     "specialty": "Psychologist",                "npi": None, "locations": [MARIETTA]},
    {"name": "Patty Postanowicz, Ph.D, LMFT",    "type": THERAPIST, "credential": "Ph.D, LMFT",
     "specialty": "Psychologist / LMFT",         "npi": None, "locations": [MARIETTA]},
    {"name": "Emma Green, LAMFT",                "type": THERAPIST, "credential": "LAMFT",
     "specialty": "Marriage & Family Therapy",   "npi": None, "locations": [MARIETTA, ALPHARETTA, DULUTH]},
    {"name": "Jamie Goldberg, LPC, E-RYT",       "type": THERAPIST, "credential": "LPC, E-RYT",
     "specialty": "Professional Counseling",     "npi": None, "locations": [MARIETTA, ALPHARETTA]},
    {"name": "Rachel Barlev, LCSW",              "type": THERAPIST, "credential": "LCSW",
     "specialty": "Clinical Social Work",        "npi": None, "locations": [MARIETTA]},
    {"name": "Silvia Lynch, LCSW",               "type": THERAPIST, "credential": "LCSW",
     "specialty": "Clinical Social Work",        "npi": None, "locations": [MARIETTA]},
    {"name": "Tu Vo, LPC",                       "type": THERAPIST, "credential": "LPC",
     "specialty": "Professional Counseling",     "npi": None, "locations": [MARIETTA]},
    {"name": "Whitney Rudd, LMFT",               "type": THERAPIST, "credential": "LMFT",
     "specialty": "Marriage & Family Therapy",   "npi": None, "locations": [MARIETTA]},
    {"name": "Ariella Peist, LCSW",              "type": THERAPIST, "credential": "LCSW",
     "specialty": "Clinical Social Work",        "npi": None, "locations": [ALPHARETTA]},
    {"name": "Cristina Lazaro, LPC",             "type": THERAPIST, "credential": "LPC",
     "specialty": "Professional Counseling",     "npi": None, "locations": [ALPHARETTA, DULUTH]},
    {"name": "Kelly Villarreal, LMFT",           "type": THERAPIST, "credential": "LMFT",
     "specialty": "Marriage & Family Therapy",   "npi": None, "locations": [ALPHARETTA]},
    {"name": "Mona Chandra, Psy.D",              "type": THERAPIST, "credential": "Psy.D",
     "specialty": "Psychologist",                "npi": None, "locations": [ALPHARETTA]},
    {"name": "Antonio Cordero, LPC",             "type": THERAPIST, "credential": "LPC",
     "specialty": "Professional Counseling",     "npi": None, "locations": [ALPHARETTA, DULUTH]},
    {"name": "Jessica Bosson, Psy.D",            "type": THERAPIST, "credential": "Psy.D",
     "specialty": "Psychologist",                "npi": None, "locations": [DULUTH]},
    {"name": "Kailyn Blackmon, PsyD",            "type": THERAPIST, "credential": "PsyD",
     "specialty": "Psychologist",                "npi": None, "locations": [DULUTH]},
    {"name": "Sheldon Kay, LPC",                 "type": THERAPIST, "credential": "LPC",
     "specialty": "Professional Counseling",     "npi": None, "locations": [DULUTH]},
    {"name": "Ashley LeGros, MEd, PLPC, NCC",    "type": THERAPIST, "credential": "MEd, PLPC, NCC",
     "specialty": "Professional Counseling",     "npi": None, "locations": [NEW_ORLEANS]},
    {"name": "Ashlie Martinez, LCSW",            "type": THERAPIST, "credential": "LCSW",
     "specialty": "Clinical Social Work",        "npi": None, "locations": [NEW_ORLEANS]},
    {"name": "David Dolese, LPC",                "type": THERAPIST, "credential": "LPC",
     "specialty": "Professional Counseling",     "npi": None, "locations": [NEW_ORLEANS]},
    {"name": "Rae Sidlauskas, MS LPC",           "type": THERAPIST, "credential": "MS, LPC",
     "specialty": "Professional Counseling",     "npi": None, "locations": [NEW_ORLEANS]},
]

PSYCHIATRISTS = [p for p in PROVIDERS if p["type"] == PSYCHIATRIST]
THERAPISTS = [p for p in PROVIDERS if p["type"] == THERAPIST]


def by_location(location: str, provider_type: str | None = None) -> list[dict]:
    return [
        p for p in PROVIDERS
        if location in p["locations"] and (provider_type is None or p["type"] == provider_type)
    ]


def appointment_type_for(provider: dict) -> str:
    return APPOINTMENT_TYPE_FOR[provider["type"]]
