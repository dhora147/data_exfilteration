# Project Overview

## Proposed title
**Insider Data Exfiltration Email Detection Using NLP and Behavioural-Feature Classification**

## Objective
Develop a working prototype that combines Natural Language Processing (NLP), cybersecurity indicators, and an AI/ML behavioural-feature classifier to flag outbound emails that may be attempting to exfiltrate confidential information.

## Pipeline
1. Ingest authorised outbound email content samples and metadata.
2. Preprocess subject/body text and derive behavioural indicators.
3. Convert text into TF-IDF features; scale numeric behavioural features.
4. Train a Logistic Regression classifier on labelled examples.
5. Evaluate using a stratified held-out test set.
6. Score individual emails and batches.
7. Generate DLP-style review alerts for medium/high-risk messages.

## Feature groups
- NLP: subject/body tokens, word and character patterns, n-grams.
- Behavioural: recipient counts, external-recipient ratio, attachment count and size, after-hours sending, recent sending volume, new-recipient flag.
- Output: probability-like risk score, risk tier, contributing review signals, alert log.

## Important research note
The included dataset is synthetic and uses deliberately illustrative labels. Do not report its scores as evidence of production accuracy. For a research evaluation, replace it with a properly authorised, representative dataset; prevent sender/recipient leakage across splits; define labels with security reviewers; and report precision, recall, F1, ROC-AUC, PR-AUC, false-positive rate, and calibration.
