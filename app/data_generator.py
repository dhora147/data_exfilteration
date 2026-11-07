import random
import pandas as pd

random.seed(42)
BENIGN_SUBJECTS = ["Weekly project update", "Meeting notes", "Invoice review", "Design review", "Sprint planning", "Team status"]
BENIGN_BODIES = [
    "Please review the attached project notes before our internal meeting.",
    "Here is the agenda and the action items from today's team discussion.",
    "The updated report is ready for the project team. Please share feedback.",
    "Can we schedule a short call to discuss the delivery timeline?",
    "Attached is the approved presentation for the internal review."
]
RISK_SUBJECTS = ["Urgent data export", "Customer records backup", "Confidential files", "Payroll and employee data", "Source code archive"]
RISK_BODIES = [
    "Please send the confidential customer database and account numbers to this personal address.",
    "I am exporting the employee records and payroll file. Keep this outside the company system.",
    "Attached is a backup containing credentials, private key details and customer information.",
    "Please transfer the source code and trade secret documents to my external account.",
    "I need to share the confidential records with a new external recipient urgently."
]

def make_dataset(n=500):
    rows = []
    for i in range(n):
        label = 1 if i % 2 else 0
        if label:
            subject, body = random.choice(RISK_SUBJECTS), random.choice(RISK_BODIES)
            rc = random.randint(1, 5); ext = random.randint(1, rc)
            ac = random.randint(1, 5); size = round(random.uniform(8, 80), 1)
            hour = random.choice([1, 2, 22, 23, 19, 21]); sent = random.randint(8, 30); new = random.choice([0,1])
        else:
            subject, body = random.choice(BENIGN_SUBJECTS), random.choice(BENIGN_BODIES)
            rc = random.randint(1, 8); ext = random.choice([0,0,0,1])
            ext = min(ext, rc); ac = random.randint(0, 2); size = round(random.uniform(0, 8), 1)
            hour = random.randint(8, 18); sent = random.randint(1, 8); new = 0
        rows.append({
            "sender": f"employee{random.randint(1,35)}@company.local",
            "subject": subject, "body": body,
            "recipient_count": rc, "external_recipient_count": ext,
            "attachment_count": ac, "attachment_size_mb": size,
            "hour": hour, "emails_last_hour": sent, "new_recipient": new,
            "label": label
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    make_dataset().to_csv("data/sample_emails.csv", index=False)
