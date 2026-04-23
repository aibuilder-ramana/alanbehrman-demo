
# PHQ-9 Depression Assessment
## RAG-Optimized Knowledge Document for AI Agents (@elevia)

---

## Document Metadata

- Document Type: Clinical Assessment
- Assessment Name: PHQ‑9 (Patient Health Questionnaire‑9)
- Clinical Domain: Mental Health
- Intended Use:
  - Depression screening
  - Symptom monitoring
  - Clinical intake
  - AI-assisted mental health triage
- Version: PHQ9-RAG-v1
- Language: English
- Source: PHQ‑9 developed by Pfizer Inc.

---

# Overview

PHQ‑9 is a standardized self‑report questionnaire used to screen for symptoms of major depressive disorder.

The instrument evaluates the frequency of depressive symptoms experienced during the **previous two weeks**.

It is commonly used in:

- Primary care
- Psychiatry
- Telemedicine
- Digital health platforms
- Mental health screening systems
- AI-based clinical assistants

Each question corresponds to diagnostic symptom criteria used for major depressive disorder.

**Important:** PHQ‑9 is a **screening tool**, not a diagnostic instrument.

---

# Instructions for Respondent

Ask the patient:

> Over the **last two weeks**, how often have you been bothered by any of the following problems?

Response options:

| Response | Score |
|--------|------|
| Not at all | 0 |
| Several days | 1 |
| More than half the days | 2 |
| Nearly every day | 3 |

---

# PHQ‑9 Questions

## Q1

Little interest or pleasure in doing things

Symptom category: Anhedonia

---

## Q2

Feeling down, depressed, or hopeless

Symptom category: Depressed mood

---

## Q3

Trouble falling or staying asleep, or sleeping too much

Symptom category: Sleep disturbance

---

## Q4

Feeling tired or having little energy

Symptom category: Fatigue

---

## Q5

Poor appetite or overeating

Symptom category: Appetite change

---

## Q6

Feeling bad about yourself — or that you are a failure or have let yourself or your family down

Symptom category: Low self‑worth

---

## Q7

Trouble concentrating on things, such as reading the newspaper or watching television

Symptom category: Concentration difficulty

---

## Q8

Moving or speaking so slowly that other people could have noticed,
or being so fidgety or restless that you have been moving around more than usual

Symptom category: Psychomotor changes

---

## Q9 (CRITICAL SAFETY ITEM)

Thoughts that you would be better off dead or of hurting yourself in some way

Symptom category: Suicidal ideation

Risk Level: HIGH

---

# Functional Impairment Question

If you checked off any problems:

How difficult have these problems made it for you to do your work,
take care of things at home, or get along with other people?

Options:

- Not difficult at all
- Somewhat difficult
- Very difficult
- Extremely difficult

---

# Scoring

Total Score Calculation

Total Score = Sum(Q1 + Q2 + Q3 + Q4 + Q5 + Q6 + Q7 + Q8 + Q9)

Minimum Score: 0  
Maximum Score: 27

---

# Severity Interpretation

| Score Range | Severity |
|-------------|---------|
| 0–4 | Minimal depression |
| 5–9 | Mild depression |
| 10–14 | Moderate depression |
| 15–19 | Moderately severe depression |
| 20–27 | Severe depression |

---

# Clinical Follow‑Up Guidance

| Score | Recommendation |
|------|---------------|
| 0–4 | No clinical action required |
| 5–9 | Monitor symptoms |
| 10–14 | Clinical evaluation recommended |
| 15–19 | Active treatment recommended |
| 20–27 | Immediate psychiatric evaluation |

---

# Safety Handling Logic (CRITICAL)

If Question 9 score ≥ 1:

Potential suicidal ideation detected.

The AI system should:

1. Immediately flag high‑risk response
2. Encourage patient to seek immediate support
3. Offer crisis resources
4. Escalate to clinician or care team
5. Avoid providing diagnosis

---

# @elevia Agent Workflow

Recommended AI flow:

1. Introduce assessment
2. Ask questions sequentially
3. Record responses
4. Calculate PHQ‑9 score
5. Determine severity
6. Evaluate suicide risk (Q9)
7. If risk present → escalate
8. Offer appointment scheduling with mental health provider

---

# Example Structured Output

Example result after assessment:

{
  "assessment": "PHQ9",
  "responses": {
    "Q1": 2,
    "Q2": 3,
    "Q3": 1,
    "Q4": 2,
    "Q5": 1,
    "Q6": 2,
    "Q7": 1,
    "Q8": 0,
    "Q9": 0
  },
  "total_score": 12,
  "severity": "Moderate depression",
  "recommended_action": "Clinical evaluation recommended"
}

---

# RAG Chunking Recommendation

For optimal retrieval performance:

Chunk Structure:

1. Overview
2. Instructions
3. Q1
4. Q2
5. Q3
6. Q4
7. Q5
8. Q6
9. Q7
10. Q8
11. Q9
12. Scoring
13. Interpretation
14. Safety Handling
15. Agent Workflow

Suggested metadata for embeddings:

{
  "assessment": "PHQ9",
  "type": "question",
  "question_id": "Q1"
}

---

# Compliance Note

PHQ‑9 is intended for screening purposes only.

Final diagnosis must be performed by a qualified clinician.
