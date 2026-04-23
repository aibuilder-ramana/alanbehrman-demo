# GAD-7 Anxiety Assessment
## RAG-Optimized Knowledge Document for @elevia

---

## Document Metadata
- Assessment: GAD-7 (Generalized Anxiety Disorder 7-item scale)
- Domain: Anxiety screening
- Use: Digital health, AI triage, clinical intake

---

## Overview
GAD-7 screens for generalized anxiety disorder. Evaluates anxiety symptoms over the previous two weeks. Used in primary care, psychiatry, telehealth, and AI mental health platforms.

---

## Instructions
Over the last 2 weeks, how often have you been bothered by the following problems?
Response: Not at all=0, Several days=1, More than half the days=2, Nearly every day=3

---

## Questions
Q1: Feeling nervous, anxious, or on edge — Symptom: Nervousness
Q2: Not being able to stop or control worrying — Symptom: Uncontrollable worry
Q3: Worrying too much about different things — Symptom: Excessive worry
Q4: Trouble relaxing — Symptom: Relaxation difficulty
Q5: Being so restless that it is hard to sit still — Symptom: Restlessness
Q6: Becoming easily annoyed or irritable — Symptom: Irritability
Q7: Feeling afraid, as if something awful might happen — Symptom: Fear/dread

---

## Scoring
Total = Q1+Q2+Q3+Q4+Q5+Q6+Q7 (0–21)

---

## Severity
0–4: Minimal anxiety
5–9: Mild anxiety
10–14: Moderate anxiety
15–21: Severe anxiety

---

## Clinical Follow-Up
0–4: No action required
5–9: Monitor symptoms
10–14: Evaluation recommended
15–21: Active treatment recommended

---

## Agent Workflow
Trigger when: patient mentions anxiety, worry, panic, nervousness, fear, on edge, restlessness, irritability
1. Introduce warmly
2. Present all 7 questions as table
3. Score total
4. Recommend appropriate next step
5. Offer provider scheduling if score ≥ 10
