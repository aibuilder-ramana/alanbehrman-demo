# Electronic Communications Consent Form
## RAG-Optimized Knowledge Document for AI Agents (@elevia)

---

## Document Metadata

- Document Type: Patient Consent Form
- Form Name: Electronic Communications Consent
- Clinical Domain: Administrative / HIPAA Compliance
- Intended Use: Obtain patient authorization for clinic to communicate via electronic channels (text, email, phone), consistent with HIPAA requirements and state law
- Version: ECOMMS-CONSENT-RAG-v1
- Language: English
- Provider: 1 Stop Medical Services (Kent, WA & Bellevue, WA)
- Regulatory Basis: HIPAA Privacy Rule (45 CFR §164.522), Washington State RCW 70.02 (Medical Records — Health Care Information Access and Disclosure Act)

---

## Overview

This form authorizes 1 Stop Medical Services to communicate with the patient through electronic channels including text messages (SMS), email, and phone calls. It also allows patients to designate family members or other individuals who may receive health information on the patient's behalf.

Patients may consent to some channels and decline others. Consent is voluntary and can be revoked at any time.

---

## Section 1: Patient Information

Fields:
- Patient Full Name
- Date of Birth
- Date of Form Completion
- Patient Phone Numbers (mobile, home, work)
- Patient Email Address
- Preferred Contact Method: Mobile Phone | Home Phone | Work Phone | Email

---

## Section 2: Communication Channel Consent

### 2A. Text Messages (SMS)

Consent question: I consent to receive text messages from 1 Stop Medical Services.
- Yes / No

If Yes, consent covers:
- Appointment reminders and confirmations
- Test result notifications (general status only; detailed results provided via secure portal or in-office)
- Care plan reminders
- Health maintenance tips
- Prescription or lab follow-up reminders

Important disclosures:
- Standard message and data rates may apply (carrier charges)
- Message frequency varies
- Patients can reply STOP at any time to unsubscribe
- Text messages may not be fully encrypted in transit; detailed clinical information will not be sent via unsecured SMS
- For clinical questions, use secure patient portal or call the office

### 2B. Phone Calls

Consent question: I consent to receive phone calls from 1 Stop Medical Services.
- Yes / No

If Yes, consent covers:
- Appointment scheduling and reminder calls
- Follow-up calls regarding test results (provider or staff callbacks)
- Balance and billing calls
- Urgent care coordination calls
- Pre-appointment preparation instructions

Important disclosures:
- Calls may come from the clinic's main number or a staff member's direct line
- Voicemail messages will be left only if patient has consented (implied by this consent)
- Automated (robocall) appointment reminders may be used

### 2C. Email Messages

Consent question: I consent to receive email messages from 1 Stop Medical Services.
- Yes / No

If Yes, consent covers:
- Appointment confirmations and reminders
- Secure links to health records or lab results via patient portal
- Health education and preventive care newsletters (if applicable)
- Billing statements and payment notifications
- Referral coordination correspondence

Important disclosures:
- Standard email is not a fully secure transmission medium
- Personally identifiable health information (PHI) will not be included in email body — secure portal links will be provided instead
- Patient is responsible for maintaining security of their email account
- Unsubscribe option available for marketing/newsletter emails; clinical communications cannot be fully opted out

---

## Section 3: Family / Authorized Representative Disclosure

### 3A. Family Communication Authorization

Question: Do you authorize 1 Stop Medical Services to discuss your medical condition(s) with members of your family?

Covered information includes: diagnosis, test results, treatment plans, and care received.

- Yes / No

### 3B. Authorized Individuals

If Yes to Section 3A, list individuals authorized to receive health information:

| # | First and Last Name | Relationship to Patient |
|---|---------------------|------------------------|
| 1 | | |
| 2 | | |
| 3 | | |

Scope of disclosure: The named individuals may receive verbal or written information about the patient's medical conditions, diagnosis, test results, treatment, and care.

Limitations: This authorization does not grant these individuals the right to make medical decisions on the patient's behalf (that requires a separate Healthcare Power of Attorney or Durable Power of Attorney).

---

## Section 4: Secure Patient Portal

1 Stop Medical Services provides a secure online patient portal for:
- Reviewing lab results
- Messaging clinical staff
- Viewing appointment history and upcoming visits
- Accessing billing information

Patients are encouraged to use the portal as the primary channel for receiving detailed clinical information. Registration requires a valid email address.

Portal access fields:
- Patient email for portal registration
- Portal enrollment preference: Yes / No

---

## Section 5: Revocation of Consent

Patients may revoke consent for any or all electronic communication channels at any time by:
- Replying STOP to any text message
- Calling the clinic at (253) 397-8683
- Emailing the clinic's administrative contact
- Submitting a written revocation at the front desk

Revocation takes effect within 5 business days of receipt.

Revocation does not apply retroactively to communications already sent.

---

## Section 6: HIPAA Notice Reference

This consent operates in conjunction with the clinic's Notice of Privacy Practices (HIPAA Privacy Notice), which describes how protected health information (PHI) is used and disclosed. A copy is available at the front desk or upon request.

Key HIPAA points:
- The clinic will not sell patient information to third parties
- Information is shared only as permitted or required by law (treatment, payment, healthcare operations, public health)
- Patients have the right to request restrictions on certain uses and disclosures
- Patients have the right to access and amend their health records

---

## Section 7: Consent Confirmation

Patient acknowledgment statement:
> "I have read and understand this Electronic Communications Consent form. I voluntarily provide the consent indicated above. I understand I may revoke this consent at any time. I acknowledge receipt of the clinic's Notice of Privacy Practices."

Consent fields:
- Patient Signature (or Legal Guardian Signature)
- Guardian Name (if applicable)
- Relationship to Patient (if guardian)
- Date of Signature

---

## Section 8: Field ID Reference

| field_id | Description |
|----------|-------------|
| consent_text | Consent to receive text messages (Yes/No) |
| consent_phone | Consent to receive phone calls (Yes/No) |
| consent_email | Consent to receive email messages (Yes/No) |
| preferred_contact | Preferred contact method |
| family_disclosure | Authorization to discuss with family (Yes/No) |
| family_contact_1_name | Authorized family member 1 — name |
| family_contact_1_rel | Authorized family member 1 — relationship |
| family_contact_2_name | Authorized family member 2 — name |
| family_contact_2_rel | Authorized family member 2 — relationship |
| family_contact_3_name | Authorized family member 3 — name |
| family_contact_3_rel | Authorized family member 3 — relationship |
| portal_enrollment | Patient wishes to enroll in patient portal (Yes/No) |
| ecomms_signature | Patient signature captured |
| ecomms_date | Date of consent |
| hipaa_ack | Patient acknowledged receipt of HIPAA Notice |

---

## AI Agent Workflow

Recommended flow for AI-assisted electronic communications consent collection:

1. Confirm patient name and date of birth
2. Confirm or collect current phone numbers (mobile, home, work) and email
3. Explain purpose: the clinic contacts patients for reminders, results, and care coordination
4. Ask about text message consent (Q: "Is it okay if we send you text reminders about your appointments and results?")
5. Ask about phone call consent
6. Ask about email consent
7. Ask about preferred contact method
8. Ask if patient authorizes sharing information with family members
9. If yes: collect names and relationships of authorized individuals (up to 3)
10. Confirm HIPAA Notice has been reviewed
11. Collect patient signature/acknowledgment

---

## RAG Chunking Recommendation

Chunk by section:
1. Overview + Patient Info
2. Text Message Consent
3. Phone Call Consent
4. Email Consent
5. Family Disclosure
6. Secure Portal
7. Revocation
8. HIPAA Reference
9. Consent Confirmation

Suggested metadata:
```json
{
  "form": "electronic_comms_consent",
  "section": "text_consent",
  "field": "consent_text"
}
```
