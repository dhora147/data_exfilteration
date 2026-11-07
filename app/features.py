import re
import pandas as pd

TEXT_COLUMNS = ["subject", "body"]
BEHAVIOUR_COLUMNS = [
    "recipient_count", "external_recipient_count", "external_ratio",
    "attachment_count", "attachment_size_mb", "sensitive_keyword_count",
    "hour", "after_hours", "emails_last_hour", "new_recipient"
]
SENSITIVE_TERMS = [
    "confidential", "customer database", "payroll", "salary", "password",
    "credentials", "source code", "trade secret", "private key",
    "passport", "account number", "export", "backup", "employee records"
]

def prepare_frame(df):
    out = df.copy()
    for c in TEXT_COLUMNS:
        if c not in out: out[c] = ""
        out[c] = out[c].fillna("").astype(str)
    defaults = {
        "sender": "unknown@company.local",
        "recipient_count": 1,
        "external_recipient_count": 0,
        "attachment_count": 0,
        "attachment_size_mb": 0.0,
        "sensitive_keyword_count": None,
        "hour": 12,
        "emails_last_hour": 1,
        "new_recipient": 0,
    }
    for c, v in defaults.items():
        if c not in out: out[c] = v
    numeric = ["recipient_count", "external_recipient_count", "attachment_count",
               "attachment_size_mb", "hour", "emails_last_hour", "new_recipient"]
    for c in numeric:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(defaults[c])
    out["recipient_count"] = out["recipient_count"].clip(lower=0)
    out["external_recipient_count"] = out["external_recipient_count"].clip(lower=0)
    out["external_ratio"] = (
        out["external_recipient_count"] / out["recipient_count"].clip(lower=1)
    ).clip(0, 1)
    out["after_hours"] = ((out["hour"] < 7) | (out["hour"] >= 20)).astype(int)
    if out["sensitive_keyword_count"].isna().any():
        def count_terms(row):
            txt = (row["subject"] + " " + row["body"]).lower()
            return sum(len(re.findall(r"\b" + re.escape(term) + r"\b", txt)) for term in SENSITIVE_TERMS)
        calculated = out.apply(count_terms, axis=1)
        out["sensitive_keyword_count"] = pd.to_numeric(
            out["sensitive_keyword_count"], errors="coerce"
        ).fillna(calculated)
    out["sensitive_keyword_count"] = pd.to_numeric(
        out["sensitive_keyword_count"], errors="coerce"
    ).fillna(0)
    for c in BEHAVIOUR_COLUMNS:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0)
    out["text"] = (out["subject"] + " " + out["body"]).str.strip()
    return out

def reasons_for(row):
    reasons = []
    if row["external_recipient_count"] > 0:
        reasons.append(f'{int(row["external_recipient_count"])} external recipient(s)')
    if row["external_ratio"] >= 0.5:
        reasons.append("Most recipients are outside the organisation")
    if row["attachment_size_mb"] >= 10:
        reasons.append("Large attachment size")
    if row["sensitive_keyword_count"] >= 2:
        reasons.append("Multiple sensitive-data terms in message")
    if row["after_hours"] == 1:
        reasons.append("Sent outside typical business hours")
    if row["emails_last_hour"] >= 15:
        reasons.append("Unusually high recent sending volume")
    if row["new_recipient"] == 1:
        reasons.append("Recipient is new or not previously observed")
    if row["attachment_count"] >= 3:
        reasons.append("Multiple attachments")
    return reasons or ["No strong behavioural indicator; review the content and context"]
