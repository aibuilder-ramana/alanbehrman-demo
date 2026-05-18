# I-693 Immigration Medical Intake

## RAG-Optimized Knowledge Document for @elevia

---

## Document Metadata

* Form: I-693 Medical Intake (USCIS Civil Surgeon)
* Domain: Immigration Medical Screening
* Use: Patient intake, compliance workflows, AI-assisted triage
* Sections: Demographics, Identity, Vaccination, Medical History, Risk Assessment, TB Screening

---

## Instructions

* Enter all details exactly as they should appear on the official I-693 form
* Upload required documents where specified
* Some responses may trigger additional follow-up questions

---

# SECTION 1: Personal Information

### Fields

* First Name (text)

* Middle Name (text)

* Last Name (text)

* Gender (single select)

  * Male
  * Female

* Marital Status (single select)

  * Single
  * Married
  * Domestic Partner
  * Separated
  * Divorced
  * Widowed

* Date of Birth (date)

---

## Address

* Street Address (text)

* Unit Type (single select)

  * Apartment
  * Suite
  * Floor
  * Unit
  * Trailer Space

* Unit Number (text)

* City (text)

* State (text)

* Zip Code (text)

---

## Contact Information

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

## Demographics

* Country of Birth (text)
* City/Town/Village of Birth (text)

### Race (multi-select)

* Caucasian (White)

* Black or African American

* Asian

* Asian Indian

* American Indian or Alaska Native

* Native Hawaiian or Pacific Islander

* Other

* If Other Race (text)

### Ethnicity (single select)

* Non-Hispanic/Latino

* Hispanic/Latino

* Other

* If Other Ethnicity (text)

---

## Clinic Location

* Exam Location (single select)

  * Marietta, GA
  * Duluth, GA

---

# SECTION 2: Document Uploads

* Photo ID Upload (file)
* Health Insurance Upload (file)
* Vaccination Records Upload (file)

---

# SECTION 3: Identification

* ID Type (single select)

  * Passport
  * Driver License
  * Identification Card
  * Employment Authorization Card
  * Instruction Permit
  * Other

* If Other ID Type (text)

* Issuing State/Country (text)

* ID Number (text)

---

# SECTION 4: Interpreter Requirement

* Interpreter Needed (yes/no)

* Language (text)

## Interpreter Details (conditional)

* First Name (text)
* Last Name (text)
* Organization (text)
* Phone (text)
* Mobile (text)
* Email (text)
* Interpreter ID Upload (file)

---

# SECTION 5: Vaccination Status

## General

* Has Vaccination Records (yes/no)

---

## Vaccines

### Flu

* Received Flu Vaccine (yes/no)
* Date (date)

### Tdap/Td

* Received (yes/no)
* Date (date)

### MMR

* Status (single select)

  * Vaccine Series
  * Immunity Titer
  * No

* Dose 1 Date (date)

* Dose 2 Date (date)

* Titer Date (date)

### Varicella

* Status (same structure as MMR)

### Hepatitis B

* Status (same structure)
* Dose 1 / 2 / 3 Dates (date)
* Titer Date (date)

### COVID-19

* Vaccine Type (single select)

  * Pfizer
  * Moderna
  * Johnson & Johnson
  * AstraZeneca
  * Combination
  * Other
  * No

* Dose 1–4 Dates (date)

---

# SECTION 6: Immigration Identifiers

* Alien Number (text)
* USCIS Online Account Number (text)

---

# SECTION 7: Communication Consent

### Consent

* Text Messages (yes/no)
* Phone Calls (yes/no)
* Email Messages (yes/no)

---

## Health Information Sharing

* Share Medical Info with Family (yes/no)

### Authorized Individuals

* Name + Relationship (repeatable list)

---

# SECTION 8: Medical History

## Conditions (yes/no for each)

* Heart problems

* Skin conditions

* Stomach/abdominal conditions

* Lung problems

* HIV/AIDS

* Hypertension

* Thyroid problems

* High cholesterol

* Muscle conditions

* Bone conditions

* Mental conditions

* Diabetes

* Tuberculosis history

* Hospitalization history

* Other condition

* If Yes → Explanation (text)

---

## Diagnosed Conditions

* List of Conditions (repeatable)

---

## Allergies

* Has Allergies (yes/no)

### Allergy List (repeatable)

* Allergy
* Year Diagnosed

---

# SECTION 9: Substance & Legal Risk

* Criminal Record (yes/no)

* Drug Use (yes/no)

* Drug Addiction (yes/no)

* Alcohol Addiction (yes/no)

* Explanation (text)

---

# SECTION 10: OB/GYN

* Pregnant (yes/no)
* Trying to Conceive (yes/no)
* Last Menstrual Period (date)
* Pregnancy Duration (text)

---

# SECTION 11: Medications

### Medication List (repeatable)

* Name
* Dose
* Frequency
* Reason

---

# SECTION 12: Sexual Health / STD Risk

* Sexually Active (yes/no)
* STD Clinic Visit (yes/no)
* Last Visit Date (date)
* STD Treatment History (enum)

  * Yes with docs
  * Yes without docs
  * Unsure
  * No

---

## Symptoms (multi-select)

* Bleeding
* Warts
* Pain
* Rash
* Itch
* Urination problems
* Discharge
* Sores/Blisters
* None
* Other

---

## Sexual Behavior

* Sex in last 6 months (yes/no)

* Number of Partners (numeric bucket)

* Condom Use (single select)

  * Always / Most / Sometimes / Rarely / Never

* Partner Type

  * Men / Women / Both / Other

* Sexual Practices (multi-select)

  * Oral
  * Vaginal
  * Anal
  * Insertive
  * Receptive
  * None

---

## Risk Factors

* Domestic Violence (yes/no)
* Sex for money/drugs (yes/no)
* Partner injects drugs (yes/no)
* Personal injection drug use (yes/no)
* Partner HIV (yes/no)
* Drug use last year (yes/no)
* Smoking (yes/no)
* Jail history (yes/no)
* Tattoos (yes/no)

---

## STD History

* Prior STD Diagnosis (multi-select)

  * Chlamydia, Gonorrhea, HPV, Herpes, Syphilis, Trichomonas, HIV, Other, None

---

## Birth Control

* Partner Uses Birth Control (yes/no/unsure)
* Method (text)
* Personal Use (yes/no)

---

# SECTION 13: Tuberculosis Screening

## History

* Prior TB Diagnosis (yes/no/unsure)
* Treatment Details (text)

---

## Symptoms (yes/no each)

* Persistent fever + cough
* Blood in sputum
* Night sweats
* Fatigue
* Appetite loss
* Weight loss

---

## Current Health

* Acute illness (yes/no)
* Live vaccine (yes/no)
* Steroids (yes/no)
* Immunosuppressive therapy (yes/no)

---

## Travel

* Travel in last 6 months (yes/no)
* Countries (text)

---

## TB Testing

* Prior TB test (yes/no)
* Type (skin/blood)
* Positive result (yes/no)
* Date (date)

---

## Imaging

* Chest X-ray (yes/no)
* Date (date)

---

## Exposure

* Family TB history (yes/no/unsure)
* Close contact with TB (yes/no)

---

## Treatment

* TB medication history (yes/no)
* Treatment details (text)

---

## BCG Vaccine

* Received BCG (yes/no)

---

## Immunocompromised Status

* Immunosuppressive illness (yes/no)
* Explanation (text)

---

# Agent Workflow

## Trigger When

* Immigration medical exam requested
* Mentions I-693, USCIS, green card medical
* Vaccination compliance queries

---

## Suggested Flow

1. Collect demographics + identity
2. Validate document uploads
3. Capture vaccination history
4. Run medical + risk questionnaire
5. Flag:

   * Missing vaccines
   * TB risk
   * STD risk
6. Generate pre-check summary for civil surgeon
7. Recommend next steps (labs, vaccines, follow-up)
