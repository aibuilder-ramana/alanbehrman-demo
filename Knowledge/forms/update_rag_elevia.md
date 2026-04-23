# Patient Update Intake Form
## RAG-Optimized Knowledge Document for @elevia

---

## Document Metadata

* Form: Patient Update Form
* Domain: General Medical Intake / Patient Profile Update
* Use: Intake, profile updates, billing, communication preferences
* Sections: Demographics, Contact, Emergency, Insurance, Consent

---

## Instructions

* Please fill all fields accurately
* Upload required documents where applicable
* Some fields may trigger additional sections (e.g., insurance)

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
* Apt / Unit Number (text)
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

# SECTION 2: Identity & Language

* Photo ID Upload (file)

* Preferred Language (single select)
  * English
  * Hindi
  * Spanish
  * Gujarati
  * Punjabi
  * Other

* If Other Language (text)

---

# SECTION 3: Demographics

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

# SECTION 4: Referral & Awareness

* How did you learn about this office? (text)
* Who referred you? (text)

---

# SECTION 5: Emergency Contact

* Name (text)
* Relationship (text)
* Address (text)
* Phone (text)

---

# SECTION 6: Healthcare Providers

* Previous Primary Doctor (text)
* Other Health Provider (text)

## Preferred Pharmacy

* Name (text)
* Address (text)
* Phone (text)

---

# SECTION 7: Communication Preferences

* Okay to Leave Detailed Message (yes/no)

## Consent Preferences

### Communication Consent

* Text Messages (yes/no)
* Phone Calls (yes/no)
* Emails (yes/no)

### Health Information Sharing

* Share Medical Info with Family (yes/no)

### Authorized Individuals (repeatable)

* Name (text)
* Relationship (text)

---

# SECTION 8: Insurance Information

## Coverage

* Has Medical Insurance (yes/no)

## Primary Insurance (conditional: if yes)

* Insurance Company (text)

* Relationship to Insured (single select)
  * Self
  * Spouse
  * Child
  * Other

* Member ID / Policy Number (text)
* Group Number (text)

### Insured Person Details

* Name (text)
* Date of Birth (date)

* Gender (single select)
  * Female
  * Male

* Phone Number (text)

### Insured Address

* Street Address (text)
* City (text)
* State (text)
* Zip Code (text)

### Uploads

* Primary Insurance Card — front & back (file)

## Secondary Insurance

* Has Secondary Insurance (yes/no)

### Secondary Insurance Details (conditional)

* Insurance Company (text)

* Relationship to Insured (single select)
  * Self
  * Spouse
  * Child
  * Other

* Member ID (text)
* Group Number (text)

### Insured Details

* Name (text)
* Date of Birth (date)
* Gender (single select)
* Phone (text)

### Address

* Street Address (text)
* City (text)
* State (text)
* Zip Code (text)

### Upload

* Secondary Insurance Card (file)

---

# SECTION 9: Authorization

## Insurance Billing Authorization

* Authorize Release of Medical Information (yes/no)
* Signature (text or digital signature)
* Date (date)

---

# Agent Workflow

## Trigger When

* Patient returning for a follow-up visit
* Patient requests to update contact, insurance, or provider information
* Insurance change or renewal
* Change in demographics or communication preferences

## Suggested Flow

1. Confirm patient identity (name, DOB)
2. Review and update contact information
3. Confirm emergency contact is current
4. Update insurance information (primary + secondary)
5. Confirm communication preferences and consent
6. Collect authorization signature
7. Flag:
   * Missing insurance card uploads
   * Expired authorization signature
   * Missing emergency contact
8. Confirm updated record with patient before submission

## Field ID Reference

| field_id | Description |
|---|---|
| first_name | First name |
| middle_initials | Middle initials |
| last_name | Last name |
| gender | Gender |
| marital_status | Marital status |
| dob | Date of birth |
| street_address | Street address |
| apt_unit | Apt/unit number |
| city | City |
| state | State |
| zip | Zip code |
| mobile_phone | Mobile phone |
| home_phone | Home phone |
| work_phone | Work phone |
| email | Email |
| preferred_contact | Preferred contact method |
| preferred_language | Preferred language |
| language_other | Other language (if selected) |
| race | Race (multi-select) |
| race_other | Other race description |
| ethnicity | Ethnicity |
| referral_source | How patient learned about office |
| referral_name | Who referred |
| ec_name | Emergency contact name |
| ec_relationship | Emergency contact relationship |
| ec_address | Emergency contact address |
| ec_phone | Emergency contact phone |
| prev_doctor | Previous primary doctor |
| other_provider | Other health provider |
| pharmacy_name | Preferred pharmacy name |
| pharmacy_address | Pharmacy address |
| pharmacy_phone | Pharmacy phone |
| ok_detailed_msg | Okay to leave detailed voicemail |
| consent_text | Consent to text messages |
| consent_phone | Consent to phone calls |
| consent_email | Consent to emails |
| family_disclosure | Share info with family |
| has_insurance | Has medical insurance |
| ins_company | Primary insurance company |
| ins_relationship | Relationship to insured (primary) |
| ins_member_id | Member ID / policy number |
| ins_group | Group number |
| ins_name | Insured person name |
| ins_dob | Insured person DOB |
| ins_gender | Insured person gender |
| ins_phone | Insured person phone |
| ins_address | Insured person address |
| has_secondary | Has secondary insurance |
| ins2_company | Secondary insurance company |
| ins2_relationship | Relationship to secondary insured |
| ins2_member_id | Secondary member ID |
| ins2_group | Secondary group number |
| authorize_release | Authorize release of medical info |
| auth_signature | Authorization signature |
| auth_date | Authorization date |
