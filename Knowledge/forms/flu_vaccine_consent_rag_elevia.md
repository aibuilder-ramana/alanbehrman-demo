# Influenza (Flu) Vaccine Consent Form
## RAG-Optimized Knowledge Document for AI Agents (@elevia)

---

## Document Metadata

- Document Type: Vaccine Consent Form
- Form Name: Influenza (Flu) Vaccine Consent
- Clinical Domain: Preventive Care / Immunization
- Intended Use: Informed consent collection for seasonal influenza vaccination at 1 Stop Medical Services
- Version: FLUVAX-CONSENT-RAG-v1
- Language: English
- Provider: 1 Stop Medical Services (Marietta, GA & Duluth, GA)
- Regulatory Basis: NCVIA (National Childhood Vaccine Injury Act); CDC Vaccine Information Statement (VIS)

---

## Overview

This consent form is completed by patients (or their legal guardian) before receiving the seasonal influenza vaccine. It ensures the patient has been informed of the benefits, risks, and contraindications of the flu vaccine, and provides documented authorization to administer the vaccine.

---

## Section 1: Patient Information

Fields:
- Patient Full Name
- Date of Birth
- Date of Vaccine Administration
- Clinic Location: Marietta, GA | Duluth, GA
- Administering Provider Name

---

## Section 2: Flu Vaccine Information

### What is the Flu Vaccine?

The influenza (flu) vaccine helps protect against influenza viruses that research indicates will be most common during the upcoming flu season.

### Types Available

- Flu shot (inactivated vaccine — injected into arm): recommended for most people aged 6 months and older
- High-dose flu shot: for adults 65 years and older
- Recombinant flu shot: egg-free option for those with egg allergies (severe)
- Nasal spray flu vaccine (live attenuated): for non-pregnant individuals 2–49 years old who are not immunocompromised

### Why Get Vaccinated?

- Reduces risk of influenza illness, hospitalization, and death
- Protects vulnerable individuals in community (herd immunity)
- Recommended annually because flu viruses evolve each season
- Especially important for: adults 65+, children under 5, pregnant women, people with chronic conditions (asthma, diabetes, heart disease, HIV)

---

## Section 3: Screening Questions (Pre-Vaccine Checklist)

The following questions are asked before vaccine administration to identify contraindications:

Q1: Do you feel sick today?
- Yes / No
- Note: Mild illness (e.g., mild cold) is not a contraindication. Moderate-to-severe illness with fever — defer until recovered.

Q2: Do you have any allergies to the flu vaccine or any of its ingredients?
- Yes / No
- Ingredients include: egg proteins (some formulations), formaldehyde, thimerosal (multi-dose vials), neomycin (some formulations), gelatin (nasal spray)
- If severe egg allergy (anaphylaxis): use egg-free recombinant formulation; administer in supervised setting.

Q3: Have you ever had a severe reaction (such as anaphylaxis) to a flu vaccine in the past?
- Yes / No
- If yes: do not administer. Refer to allergist/immunologist.

Q4: Have you ever been diagnosed with Guillain-Barré Syndrome (GBS)?
- Yes / No
- If yes: consult physician before administering. History of GBS within 6 weeks of a prior flu vaccine is a precaution.

Q5: Are you pregnant or could you possibly be pregnant?
- Yes / No
- Note: Flu shot (inactivated) IS recommended during pregnancy. Live nasal spray (LAIV) is CONTRAINDICATED during pregnancy.

Q6: Do you have a weakened immune system (due to disease such as HIV/AIDS, cancer, leukemia, or due to medication such as steroids, chemotherapy)?
- Yes / No
- Note: Inactivated flu shot is safe and recommended. Live nasal spray (LAIV) is CONTRAINDICATED.

Q7: Is this vaccine for a child between 6 months and 8 years old who has never received the flu vaccine before, or received fewer than 2 doses last season?
- Yes / No
- Note: These children need 2 doses at least 4 weeks apart in their first flu vaccine season.

Q8: Have you received any vaccines in the past 4 weeks?
- Yes / No
- Note: Live vaccines administered within 28 days of each other may reduce immune response.

---

## Section 4: Benefits and Risks

### Benefits
- Prevents influenza illness in most healthy adults
- Reduces severity of illness if infection does occur
- Reduces flu-related hospitalizations and complications
- Helps protect those around you who cannot be vaccinated

### Risks / Possible Side Effects

Common (not serious):
- Soreness, redness, swelling at injection site
- Headache, fatigue
- Muscle aches
- Low-grade fever
- Nausea (mild)

Less Common:
- Fainting (syncope) — remain seated for 15 minutes after injection
- Shoulder injury related to vaccine administration (SIRVA) — rare with improper technique

Rare but Serious:
- Allergic reaction (hives, swelling of face/throat, rapid heartbeat, dizziness, weakness): typically within minutes to hours
- Guillain-Barré Syndrome (GBS): approximately 1–2 additional cases per million doses — very rare

---

## Section 5: Contraindications

Do NOT administer flu vaccine if:
- Severe allergic reaction (anaphylaxis) to a previous flu vaccine dose
- Allergy to any ingredient in the vaccine formulation
- Age under 6 months (no flu vaccine approved for infants under 6 months)

Additional contraindications for LIVE nasal spray (LAIV) specifically:
- Pregnancy
- Age 2 years or under, or 50 years or over
- Immunocompromised status (including HIV, chemotherapy, long-term steroids)
- Received influenza antiviral medication within prior 48 hours
- Cochlear implant (certain formulations)
- Close contact with severely immunocompromised persons requiring protective environment

---

## Section 6: Consent Statement

By signing this form, the patient (or legal guardian) acknowledges:

1. They have read or had read to them the Vaccine Information Statement (VIS) for the flu vaccine.
2. They have had an opportunity to ask questions.
3. They consent to receive the influenza vaccine today.
4. They understand the benefits and risks described above.
5. They have truthfully answered the screening questions.

Consent fields:
- Patient Signature (or Guardian Signature)
- Guardian Name (if signing for a minor)
- Relationship to Patient (if guardian)
- Date of Consent

---

## Section 7: Post-Vaccination Instructions

- Remain in the clinic for 15 minutes after vaccination to monitor for immediate reactions.
- If you experience signs of a severe allergic reaction (difficulty breathing, swelling of throat, rapid heartbeat, dizziness) seek emergency care immediately or call 911.
- The arm where you received the shot may be sore for 1–2 days. Applying a cool, damp cloth can help.
- Over-the-counter pain relievers (ibuprofen, acetaminophen) may be taken to reduce soreness or fever.
- Report any adverse reactions to your provider and the VAERS (Vaccine Adverse Event Reporting System).

---

## Section 8: Documentation Fields

| field_id | Description |
|----------|-------------|
| flu_consent_given | Patient consented to flu vaccine (Yes/No) |
| flu_vaccine_type | Type of flu vaccine administered |
| flu_vaccine_lot | Lot number of vaccine administered |
| flu_vaccine_date | Date of vaccine administration |
| flu_vaccine_site | Injection site (left arm / right arm / other) |
| flu_prior_reaction | Prior severe reaction to flu vaccine |
| flu_egg_allergy | Egg allergy present |
| flu_gbs_history | History of Guillain-Barré Syndrome |
| flu_pregnant | Patient is pregnant |
| flu_immunocompromised | Patient is immunocompromised |
| flu_signature | Patient/guardian signature captured |
| flu_vis_provided | VIS document provided to patient |

---

## AI Agent Workflow

Recommended flow for AI-assisted flu vaccine consent collection:

1. Confirm patient name and date of birth
2. Inform patient about the flu vaccine (what it is, why recommended)
3. Provide or summarize the VIS
4. Ask screening questions Q1–Q8 sequentially
5. Flag any contraindications — escalate to clinical staff if found
6. If no contraindications: present consent statement
7. Collect patient acknowledgment/signature
8. Record VIS version and date provided
9. Document vaccine details after administration

---

## RAG Chunking Recommendation

Chunk by section:
1. Overview + Patient Info
2. Vaccine Types
3. Screening Questions (one chunk per question or grouped)
4. Benefits
5. Risks/Side Effects
6. Contraindications
7. Consent Statement
8. Post-Vaccination Instructions

Suggested metadata:
```json
{
  "form": "flu_vaccine_consent",
  "section": "screening",
  "question": "Q2"
}
```
