# Medical Full Intake Form
## RAG-Optimized Knowledge Document for @elevia

---

## Document Metadata

* Form: Medical Full Intake Form
* Domain: Primary Care / Comprehensive Intake
* Use: First-time patient intake, clinical triage, longitudinal health record creation
* Sections: Demographics, Insurance, Chief Complaints, ROS, History, Lifestyle, Family History, Preventive Care

---

## Instructions

* Complete all applicable fields
* Provide as much detail as possible for clinical accuracy
* Some answers will trigger additional follow-up questions

---

# SECTION 1: Personal Information

## Identity

* First Name (text)
* Middle Initials (text)
* Last Name (text)

* Gender (single select)
  * Female
  * Male
  * Transgender
  * Non-binary
  * Other

* Date of Birth (date)

* Marital Status (single select)
  * Single
  * Married
  * Domestic Partner
  * Separated
  * Divorced
  * Widowed

---

## Address

* Street Address (text)
* Apt / Unit Number (text)
* City (text)
* State (text)
* Zip Code (text)

---

## Contact

* Mobile Phone (text)
* Home Phone (text)
* Work Phone (text)
* Email (text)

* Preferred Contact Method (multi-select)
  * Mobile Phone
  * Home Phone
  * Work Phone
  * Email

---

# SECTION 2: Identity & Demographics

* Photo ID Upload (file)

* Preferred Language (single select)
  * English
  * Hindi
  * Spanish
  * Gujarati
  * Punjabi
  * Other
* If Other Language (text)

## Race (multi-select)

* White
* Black
* Asian
* American Indian / Native Alaskan
* Native Hawaiian / Pacific Islander
* Other
* If Other Race (text)

## Ethnicity (single select)

* Hispanic / Latino(a)
* Not Hispanic / Latino(a)

---

# SECTION 3: Referral & Contacts

* How did you learn about this office? (text)
* Who referred you? (text)

## Emergency Contact

* Name (text)
* Relationship (text)
* Address (text)
* Phone (text)
* Alternate Phone (text)

## Providers

* Previous Primary Doctor (text)
* Doctor Phone (text)
* Other Health Provider (text)
* Provider Phone (text)

## Preferred Pharmacy

* Name (text)
* Address (text)

---

# SECTION 4: Communication & Consent

* Okay to leave detailed message (yes/no)

## Communication Consent

* Text Messages (yes/no)
* Phone Calls (yes/no)
* Emails (yes/no)

## Health Info Sharing

* Share with family (yes/no)

### Authorized Individuals (repeatable)

* Name (text)
* Relationship (text)

---

# SECTION 5: Insurance

* Has Insurance (yes/no)

## Primary Insurance (conditional)

* Insurance Company (text)
* Relationship to Insured (single select): Self / Spouse / Child / Other
* Member ID (text)
* Group Number (text)

### Insured Details

* Name (text)
* DOB (date)
* Gender (single select): Female / Male
* Phone (text)
* Address — Street, City, State, Zip

### Upload

* Insurance Card (file)

## Secondary Insurance

* Has Secondary Insurance (yes/no)
* (Same structure as primary)

## Authorization

* Consent to bill insurance (yes/no)
* Signature (text or digital)
* Date (date)

---

# SECTION 6: Chief Complaint

* Reason for Visit (text)

## Problems (up to 3, repeatable)

* Description (text)
* Duration (text)
* Treatments Tried (text)
* Severity (single select): Mild / Moderate / Severe

---

# SECTION 7: Review of Systems (ROS)

## Constitutional (multi-select)

Fatigue, Fever/Chills, Weight loss, Weight gain, Night sweats, None

## Neurological (multi-select)

Confusion, Dizziness, Headaches, Memory issues, Numbness, Tingling, None

## Eyes (multi-select)

Blurry vision, Burning, Redness, Vision loss, None

## ENT (multi-select)

Congestion, Ear pain, Hoarseness, Nosebleeds, Sinus pain, Tinnitus, None

## Respiratory (multi-select)

Cough, Shortness of breath, Wheezing, Sleep apnea, Blood in sputum, None

## Cardiovascular (multi-select)

Chest pain, Palpitations, Swelling, Exercise intolerance, None

## GI (multi-select)

Abdominal pain, Constipation, Diarrhea, Nausea/vomiting, Blood in stool, Heartburn, None

## GU (multi-select)

Painful urination, Frequency, Incontinence, Blood in urine, None

## Allergy / Immunology (multi-select)

Frequent infections, Allergies, Swollen glands, None

## Hematology (multi-select)

Easy bruising, Blood clots, Transfusion history, None

## Musculoskeletal (multi-select)

Joint pain, Muscle pain, Weakness, None

## Skin / Breast (multi-select)

Rash, Dry skin, Lump, Discharge, None

## Psychiatric (multi-select)

Anxiety, Depression, Poor sleep, Suicidal thoughts, None

---

# SECTION 8: Medical History

## Last Exams

* Annual Physical (date)
* Eye Exam (date)
* Dental Exam (date)

## Conditions (Yes / No / Past for each)

Anxiety, Asthma, Arthritis, Blood clots, Diabetes I, Diabetes II, Heart disease, Hypertension, Kidney disease, Liver disease, Cancer, Stroke, Thyroid disorder, Neurologic disorder

* If Yes → Explanation (text)

---

# SECTION 9: Surgical History

* Had surgery (yes/no)

## Surgeries (repeatable)

* Procedure (text)
* Month/Year (text)

---

# SECTION 10: Medications & Allergies

## Medications (repeatable)

* Name (text)
* Dose (text)
* Frequency (text)
* Reason (text)

* Recent antibiotics (yes/no)

## Allergies

* Has allergies (yes/no)

### Allergy List (repeatable)

* Allergy (text)
* Reaction (text)

* Shellfish / Iodine / Contrast allergy (yes/no + reaction)
* Latex allergy (yes/no)

---

# SECTION 11: Gender-Specific Health

## Female

* LMP (date)
* Number of Pregnancies
* Miscarriages
* C-sections
* Vaginal births
* Contraceptives (yes/no + type)
* Menopause (yes/no)
* Hysterectomy (yes/no)
* Hormone therapy (yes/no)
* Last Pap smear (date)
* Last Mammogram (date)

## Male

* Vasectomy (yes/no)
* Erectile dysfunction (yes/no)
* Last Prostate exam (date)
* PSA result (text)

---

# SECTION 12: Social & Lifestyle

## Substance Use

* Alcohol (yes/no/past)
* Tobacco (yes/no/past)
* Drugs (yes/no/past)
* Caffeine — type + cups/day

## Diet & Exercise

* Dietary restrictions (yes/no + description)
* Exercise (yes/no)
* Frequency (single select): Daily / Several times/week / Weekly / Rarely
* Types (text)

## Sexual Health

* Sexually active (yes/no)
* New partner in past year (yes/no)
* Partner type: Men / Women / Both

---

# SECTION 13: Family History

For each condition: Yes / No + Relationship

* Alzheimer's
* Heart disease
* Stroke
* Hypertension
* Diabetes
* Cancer (type if yes)
* Mental illness

---

# SECTION 14: Preventive Care

## Screenings (date for each)

* Colonoscopy
* Bone Density
* EKG
* Cholesterol
* Thyroid
* Chest X-ray

## Immunizations (date for each)

* Flu
* Tdap
* Hepatitis A
* Hepatitis B
* MMR
* COVID-19
* Pneumococcal
* Shingles
* Other (text + date)

---

# SECTION 15: Social Determinants

* Abuse history (yes/no + type)
* Social support (yes/no)
* Travel history (yes/no + destination)

## Education & Employment

* Education Level (single select): Less than HS / HS Diploma / Some College / Bachelor's / Graduate+
* Employment Status (single select): Employed / Self-employed / Unemployed / Retired / Student / Disabled
* Occupation (text)

## Environmental Exposure

* Chemical or environmental exposure (yes/no + explanation)

---

# SECTION 16: Legal & Directives

* Advanced Directive (yes/no + upload)
* Power of Attorney (yes/no + upload)
* Living Will (yes/no)

---

# SECTION 17: Attestation

* Certification statement (acknowledgment checkbox)
* Signature (text or digital)
* Date (date)

---

# Agent Workflow

## Trigger When

* New patient onboarding
* Primary care intake
* Annual checkup
* Complex symptom reporting

## Suggested Flow

1. Capture demographics
2. Validate insurance + identity
3. Collect chief complaints
4. Run ROS dynamically
5. Capture medical + surgical history
6. Capture medications + allergies
7. Capture lifestyle + family history
8. Run preventive care checks
9. Generate structured patient summary
10. Flag risks:
    * Chronic disease
    * Mental health
    * Substance use
    * Preventive gaps

## RAG Retrieval Keys

* chief_complaint
* ros.systems.*
* medical_history.conditions
* medications.current
* allergies.list
* family_history
* lifestyle.substance_use
* preventive.immunizations
