"""
Provider-specific intake rules.

The paperwork packet, the fee, and the logistics a patient is told are not a
static list — they are determined by the combination of:

    provider  ×  modality (in_person | telehealth)  ×  location

Each entry below is transcribed from the practice's own scheduling template
for that combination, so the wording patients see matches what the front desk
already sends. Providers with no entry here fall back to the app's existing
behaviour (crud.create_appointment attaches the standard packet); they become
dynamic as their templates arrive.

Form ids refer to service/seed.py form_definitions.
"""
from __future__ import annotations
from typing import Optional

IN_PERSON = "in_person"
TELEHEALTH = "telehealth"
MODALITIES = (IN_PERSON, TELEHEALTH)

MODALITY_LABELS = {IN_PERSON: "In Person", TELEHEALTH: "Telehealth"}

# "virtual" is what patients and staff often say for telehealth
MODALITY_ALIASES = {
    "in person": IN_PERSON, "in-person": IN_PERSON, "inperson": IN_PERSON,
    "office": IN_PERSON, "in_person": IN_PERSON,
    "telehealth": TELEHEALTH, "virtual": TELEHEALTH, "video": TELEHEALTH,
    "remote": TELEHEALTH, "online": TELEHEALTH,
}

# Order matters — this is the order the packet is presented in.
STANDARD_PACKET = [
    "credit_card_authorization",
    "hipaa",
    "client_info",
    "cancellation_policy",
    "provider_consent",
    "insurance_authorization",
    "release_information",
    "surprise_billing",
]

_POLICY_BUSINESS_HOURS = (
    "All forms must be completed at least 48 business hours prior to your "
    "appointment or your appointment will be cancelled and need to be "
    "rescheduled. This practice requires a credit card to secure the initial "
    "appointment. No-shows or cancellations less than 48 business hours in "
    "advance will be charged a $150 administrative fee. All credit card "
    "information will be processed securely."
)

_POLICY_48_HOURS = (
    "All forms must be completed at least 48 hours prior to your appointment "
    "or your appointment will be cancelled and need to be rescheduled. This "
    "practice requires a credit card to secure the initial appointment. "
    "No-shows or cancellations less than 48 business hours in advance will be "
    "charged a $150 administrative fee. All credit card information will be "
    "processed securely."
)


def _fee_text(amount: int) -> str:
    return (
        f"If you are out of network or out of pocket, your payment of ${amount} "
        "can be made via cash, check, or credit card/HSA."
    )


DR_RAM = "Dr. Ramakanth Vemuluri, MD"
ASHLEY_LEE = "Ashley Lee, PMHNP-BC"

RULES = [
    {
        "provider": DR_RAM,
        "modality": IN_PERSON,
        "location": "Dunwoody, GA",
        "location_label": "Peachford",
        "address": "2150 Peachford Rd, Suite I, Atlanta, GA 30338",
        "address_note": (
            "Office is on the Peachford Hospital campus in the medical building. "
            "Suite I is next to the pharmacy."
        ),
        "session_link": None,
        "session_link_note": None,
        "forms": STANDARD_PACKET,
        "consent_label": "Informed consent for Dr. Ram",
        "insurance_payers": ["Aetna", "United Healthcare", "BCBS", "Oscar", "Medicare", "Tricare"],
        "release_note": (
            "To obtain medical records from previous providers or to discuss your "
            "treatment with anyone — please include all parties you would like this for."
        ),
        "fee_amount": 400,
        "fee_text": _fee_text(400),
        "policy": _POLICY_BUSINESS_HOURS,
    },
    {
        "provider": DR_RAM,
        "modality": TELEHEALTH,
        "location": None,
        "location_label": "Telehealth",
        "address": None,
        "address_note": None,
        "session_link": "https://sessions.psychologytoday.com/dr-ramakanth-k-vemuluri",
        "session_link_note": "Please save this link for all virtual visits with Dr. Ram.",
        "forms": STANDARD_PACKET,
        "consent_label": "Informed consent for Dr. Ram",
        "insurance_payers": ["Aetna", "United Healthcare", "BCBS", "Oscar", "Medicare", "Tricare"],
        "release_note": (
            "To obtain medical records from previous providers or to discuss your "
            "treatment with anyone — please include all parties you would like this for."
        ),
        "fee_amount": 400,
        "fee_text": _fee_text(400),
        "policy": _POLICY_BUSINESS_HOURS,
    },
    {
        "provider": ASHLEY_LEE,
        "modality": TELEHEALTH,
        "location": None,
        "location_label": "Telehealth",
        "address": None,
        "address_note": None,
        "session_link": "https://sessions.psychologytoday.com/ashley-lee-1",
        "session_link_note": "Please save for ALL virtual appointments with Ashley.",
        "forms": STANDARD_PACKET,
        "consent_label": "Informed consent for Ashley Lee",
        "insurance_payers": ["United Healthcare", "BCBS", "Medicare"],
        "release_note": (
            "Please complete for providers you want us to obtain medical records from, "
            "or parties you would like us to be able to speak with about your treatment."
        ),
        "fee_amount": 300,
        "fee_text": _fee_text(300),
        "policy": _POLICY_48_HOURS,
    },
    {
        "provider": ASHLEY_LEE,
        "modality": IN_PERSON,
        "location": "New Orleans, LA",
        "location_label": "New Orleans",
        "address": "2517 Jena St., New Orleans, LA 70115",
        "address_note": "Little black building next to Bearcat café.",
        "session_link": None,
        "session_link_note": None,
        "forms": STANDARD_PACKET,
        "consent_label": "Informed consent for Ashley Lee",
        "insurance_payers": ["United Healthcare", "BCBS", "Medicare"],
        "release_note": (
            "Optional — to discuss your treatment with anyone or obtain previous "
            "medical records; please include all parties you would like this for."
        ),
        "fee_amount": 300,
        "fee_text": _fee_text(300),
        "policy": _POLICY_48_HOURS,
    },
]


def normalize_modality(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return MODALITY_ALIASES.get(str(value).strip().lower())


def _city(location: Optional[str]) -> str:
    """"Dunwoody, GA" and "Dunwoody" must match the same rule."""
    if not location:
        return ""
    return str(location).split(",")[0].split(" — ")[0].strip().lower()


def resolve(
    provider_name: Optional[str],
    modality: Optional[str],
    clinic_location: Optional[str] = None,
) -> Optional[dict]:
    """The rule for this combination, or None when the provider has no template
    yet — callers then keep the app's existing default behaviour."""
    if not provider_name:
        return None
    modality = normalize_modality(modality)
    if modality is None:
        return None

    candidates = [
        r for r in RULES
        if r["provider"] == provider_name and r["modality"] == modality
    ]
    if not candidates:
        return None

    # Telehealth rules are location-independent; in-person rules must match the office.
    if modality == TELEHEALTH:
        return candidates[0]

    wanted = _city(clinic_location)
    for r in candidates:
        if _city(r["location"]) == wanted:
            return r
    # A provider with exactly one in-person office is unambiguous even if the
    # stored location string is worded differently.
    return candidates[0] if len(candidates) == 1 else None


def has_rules_for(provider_name: Optional[str]) -> bool:
    return any(r["provider"] == provider_name for r in RULES)


def providers_with_rules() -> list[str]:
    seen = []
    for r in RULES:
        if r["provider"] not in seen:
            seen.append(r["provider"])
    return seen
