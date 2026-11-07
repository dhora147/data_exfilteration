# Insider Data Exfiltration Email Detection — Working Prototype

A local, explainable prototype combining NLP, cybersecurity signals, AI/ML, and behavioural-feature classification to flag outbound emails that may indicate insider data exfiltration.

## Features
- NLP pipeline: text cleaning + TF-IDF word and character features.
- Behavioural/cybersecurity features: recipient count, external-recipient ratio, attachment count/size, sensitive-keyword count, after-hours indicator, sender's recent sending volume, and unusual-recipient indicator.
- Hybrid classifier: combines NLP and behavioural features using a scikit-learn `ColumnTransformer` and Logistic Regression.
- Train/test split with held-out evaluation (accuracy, precision, recall, F1, ROC-AUC where available).
- Local web interface to analyse an email, view a risk score/reasons, inspect model metrics, and upload a CSV for batch screening.
- Data-loss-prevention-style alert log saved locally as CSV.
- Synthetic sample dataset. No real corporate email or personal data is included.

## Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10–3.12 recommended
- Internet connection for the first dependency installation

## Run on Windows (PowerShell)
1. Extract the ZIP.
2. Open PowerShell in the extracted `insider_email_exfiltration_prototype` folder.
3. Run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

If Python 3.11 is not installed, use `py -3.12` or `py -3.10` to create the environment.

4. Open the URL printed in the terminal (normally `http://127.0.0.1:8501`).

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

## First use
The app automatically trains the model on the included synthetic dataset if no trained model exists. You can also click **Retrain model** in the sidebar.

Use **Email analysis** to enter a sample outbound email and its metadata. Use **Batch CSV screening** to upload a CSV. A sample CSV is in `data/sample_emails.csv`.

## CSV columns
Required:
- `subject`
- `body`

Optional behavioural columns (defaults are applied if omitted):
- `sender`
- `recipient_count`
- `external_recipient_count`
- `attachment_count`
- `attachment_size_mb`
- `sensitive_keyword_count`
- `hour`
- `emails_last_hour`
- `new_recipient` (0 or 1)

Optional label for training data:
- `label` (0 = benign, 1 = suspected exfiltration)

## Important limitations
This is an academic working prototype, not a production DLP product or proof of malicious intent. It uses synthetic training examples and heuristic labels. A high-risk result is an investigation lead, not a finding of wrongdoing. Do not upload confidential, regulated, or personally identifiable corporate data without authorization. For real deployment, obtain approved datasets, define governance and retention rules, validate false-positive rates, and integrate with authorized mail gateway/audit logs.
