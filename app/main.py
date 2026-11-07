import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
from app.data_generator import make_dataset
from app.model import train, load_model, evaluate_metrics, predict
from app.features import prepare_frame, reasons_for

st.set_page_config(page_title="Insider Email Exfiltration Detection", page_icon="🛡️", layout="wide")
st.title("🛡️ Insider Data Exfiltration Email Detection")
st.caption("NLP + behavioural-feature classifier | Cybersecurity & AI-driven threat detection | Local academic prototype")

def ensure_model():
    model = load_model()
    metrics = evaluate_metrics()
    if model is None:
        with st.spinner("Training the initial model on the included synthetic dataset..."):
            model, metrics = train(make_dataset(500))
    return model, metrics

model, metrics = ensure_model()
with st.sidebar:
    st.header("Model controls")
    st.write("Classifier: TF-IDF NLP + behavioural features + Logistic Regression")
    if st.button("Retrain model", use_container_width=True):
        with st.spinner("Training and evaluating on held-out data..."):
            model, metrics = train(make_dataset(500))
        st.success("Model retrained.")
    st.divider()
    st.caption("Prototype only. Alerts require human review.")

tab1, tab2, tab3 = st.tabs(["Email analysis", "Batch CSV screening", "Model evaluation"])

with tab1:
    st.subheader("Analyse an outbound email")
    c1, c2 = st.columns(2)
    with c1:
        sender = st.text_input("Sender", "employee12@company.local")
        subject = st.text_input("Email subject", "Please review the project update")
        body = st.text_area("Email body", "Please review the attached project notes before our internal meeting.", height=150)
        recipient_count = st.number_input("Total recipients", min_value=0, max_value=500, value=2)
        external_count = st.number_input("External recipients", min_value=0, max_value=500, value=0)
    with c2:
        attachment_count = st.number_input("Attachment count", min_value=0, max_value=100, value=1)
        attachment_size = st.number_input("Total attachment size (MB)", min_value=0.0, max_value=10000.0, value=1.5)
        hour = st.slider("Hour sent (24-hour clock)", 0, 23, 14)
        emails_last_hour = st.number_input("Emails sent by sender in last hour", min_value=0, max_value=1000, value=2)
        new_recipient = st.selectbox("New/unusual recipient?", ["No", "Yes"])
    if external_count > recipient_count:
        st.warning("External recipients cannot exceed total recipients.")
    if st.button("Analyse email", type="primary"):
        if external_count > recipient_count:
            st.error("Please correct the recipient counts.")
        else:
            row = pd.DataFrame([{
                "sender": sender, "subject": subject, "body": body,
                "recipient_count": recipient_count, "external_recipient_count": external_count,
                "attachment_count": attachment_count, "attachment_size_mb": attachment_size,
                "hour": hour, "emails_last_hour": emails_last_hour,
                "new_recipient": 1 if new_recipient == "Yes" else 0
            }])
            result = predict(row, model).iloc[0]
            score = float(result["risk_score"])
            st.divider()
            left, right = st.columns([1,2])
            with left:
                st.metric("Exfiltration risk score", f"{score:.1%}")
                if score >= 0.70:
                    st.error("HIGH RISK — DLP review recommended")
                elif score >= 0.40:
                    st.warning("MEDIUM RISK — Review recommended")
                else:
                    st.success("LOWER RISK — No strong model signal")
            with right:
                st.write("**Signals to review**")
                for reason in reasons_for(result):
                    st.write("• " + reason)
            alert = {
                "timestamp": pd.Timestamp.now().isoformat(timespec="seconds"),
                "sender": sender, "subject": subject, "risk_score": round(score,4),
                "risk_level": "HIGH" if score >= .70 else "MEDIUM" if score >= .40 else "LOW",
                "reasons": "; ".join(reasons_for(result))
            }
            if score >= .40:
                path = Path("data/alerts.csv")
                pd.DataFrame([alert]).to_csv(path, mode="a", header=not path.exists(), index=False)
                st.info("A review alert was added to data/alerts.csv.")
            st.caption("A model score is a prioritisation signal, not proof of malicious intent.")

with tab2:
    st.subheader("Screen a batch of emails")
    st.write("Upload a CSV with at least `subject` and `body`. Behavioural columns are optional.")
    sample_path = Path("data/sample_emails.csv")
    if sample_path.exists():
        st.download_button("Download sample CSV", sample_path.read_bytes(), "sample_emails.csv", "text/csv")
    uploaded = st.file_uploader("Choose email CSV", type=["csv"])
    if uploaded:
        try:
            batch = pd.read_csv(uploaded)
            if not {"subject", "body"}.issubset(batch.columns):
                st.error("CSV must contain subject and body columns.")
            else:
                screened = predict(batch, model)
                screened["risk_level"] = screened["risk_score"].apply(lambda x: "HIGH" if x >= .70 else "MEDIUM" if x >= .40 else "LOW")
                st.dataframe(screened[["sender","subject","risk_score","risk_level"] if "sender" in screened else ["subject","risk_score","risk_level"]], use_container_width=True)
                st.download_button("Download screening results", screened.to_csv(index=False).encode("utf-8"), "screening_results.csv", "text/csv")
                alerts = screened[screened["risk_score"] >= .40].copy()
                if len(alerts):
                    alert_path = Path("data/alerts.csv")
                    alerts_out = pd.DataFrame({
                        "timestamp": pd.Timestamp.now().isoformat(timespec="seconds"),
                        "sender": alerts.get("sender", "unknown"),
                        "subject": alerts["subject"],
                        "risk_score": alerts["risk_score"],
                        "risk_level": alerts["risk_level"]
                    })
                    alerts_out.to_csv(alert_path, mode="a", header=not alert_path.exists(), index=False)
                    st.warning(f"{len(alerts)} review alert(s) added to data/alerts.csv.")
        except Exception as e:
            st.error(f"Could not process CSV: {e}")

with tab3:
    st.subheader("Held-out test evaluation")
    if metrics:
        cols = st.columns(5)
        for col, key in zip(cols, ["accuracy","precision","recall","f1","roc_auc"]):
            val = metrics.get(key)
            col.metric(key.replace("_"," ").title(), "N/A" if val is None else f"{val:.3f}")
        st.write(f"Test samples: {metrics['test_rows']}")
        st.write("Confusion matrix (actual rows × predicted columns; class order 0, 1)")
        st.dataframe(pd.DataFrame(metrics["confusion_matrix"], index=["Actual benign","Actual suspected"], columns=["Predicted benign","Predicted suspected"]))
        st.caption("Metrics are from a held-out split of synthetic, rule-labelled examples. They demonstrate the pipeline, not real-world performance.")
    else:
        st.info("Train the model to generate evaluation metrics.")

st.divider()
st.caption("For authorized defensive research only. Use approved data, minimise personal data, and keep a human analyst in the decision loop.")
