import streamlit as st
import requests
import json
import base64
import time
import os
import pandas as pd
from dotenv import load_dotenv
from database import init_db, save_audit, fetch_all_audits

# Initialize SQLite database
init_db()

st.set_page_config(page_title="Mahindra Finance AI Compliance", layout="wide")

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY not found in environment!")
    st.stop()

# Updated endpoint to standard Gemini 1.5 Flash model
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

st.title("🛡️ Mahindra Finance - Audio AI Compliance & Insights Engine")
st.markdown("Automated QA audit system for regional collection and customer service calls.")

# Setup Navigation Tabs
tab1, tab2 = st.tabs(["🎙️ Audit New Call", "📊 Compliance History & Analytics"])

# TAB 1: LIVE AUDIT
with tab1:
    st.subheader("1. Upload Call Recording")
    uploaded_file = st.file_uploader("Choose an audio file (.mp3 / .wav)", type=["mp3", "wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
        
        if st.button("🚀 Run Compliance Audit", type="primary"):
            with st.spinner("Transcribing audio and analyzing compliance metrics..."):
                bytes_data = uploaded_file.getvalue()
                encoded_audio = base64.b64encode(bytes_data).decode("utf-8")
                
                prompt = """
                You are an expert Quality Assurance AI Engineer at Mahindra Finance.
                Listen carefully to this customer service/collection call recording.

                Perform two tasks:
                1. Generate an accurate verbatim transcript of the call.
                2. Audit the interaction based on compliance rules.

                You MUST respond strictly with a valid JSON object matching this schema:
                {
                  "transcript": "Full text transcript of the audio",
                  "customer_sentiment": "Cooperative" | "Angry" | "Distressed",
                  "promised_payment_date": "string (e.g., Friday, 2026-09-05, or None)",
                  "agent_compliant": true | false,
                  "summary": "Short 1-sentence summary of the call"
                }

                Do NOT include markdown backticks (such as ```json) or any conversational text. Return ONLY the raw JSON object.
                """

                payload = {
                    "contents": [{
                        "parts": [
                            {"inline_data": {"mime_type": "audio/mp3", "data": encoded_audio}},
                            {"text": prompt}
                        ]
                    }],
                    "generationConfig": {"response_mime_type": "application/json"}
                }

                headers = {'Content-Type': 'application/json'}

                success = False
                parsed_audit = None

                for attempt in range(1, 4):
                    try:
                        response = requests.post(URL, headers=headers, data=json.dumps(payload))
                        if response.status_code == 200:
                            result_data = response.json()
                            raw_json_string = result_data['candidates'][0]['content']['parts'][0]['text']
                            parsed_audit = json.loads(raw_json_string)
                            success = True
                            break
                        elif response.status_code == 503:
                            time.sleep(2)
                        else:
                            st.error(f"API Error ({response.status_code}): {response.text}")
                            break
                    except Exception as e:
                        st.error(f"Request Error: {str(e)}")
                        break

                if success and parsed_audit:
                    # Save audit result into database
                    save_audit(
                        parsed_audit.get("customer_sentiment"),
                        parsed_audit.get("promised_payment_date"),
                        parsed_audit.get("agent_compliant"),
                        parsed_audit.get("summary"),
                        parsed_audit.get("transcript")
                    )

                    st.success("Audit Completed & Saved to Database!")
                    st.divider()

                    # Define metrics columns inside the success block
                    col1, col2, col3 = st.columns(3)
                    col1.metric(label="Customer Sentiment", value=parsed_audit.get("customer_sentiment", "N/A"))
                    col2.metric(label="Promised Payment Date", value=parsed_audit.get("promised_payment_date", "N/A"))
                    col3.metric(
                        label="Agent Compliance Status", 
                        value="PASSED" if parsed_audit.get("agent_compliant") else "FAILED",
                        delta="Compliant" if parsed_audit.get("agent_compliant") else "Non-Compliant"
                    )

                    st.divider()
                    st.subheader("2. Call Summary & Transcript")
                    st.info(f"**Executive Summary:** {parsed_audit.get('summary')}")
                    
                    with st.expander("📄 View Full Verbatim Transcript"):
                        st.write(parsed_audit.get("transcript"))

                    with st.expander("🔍 View Raw JSON Output"):
                        st.json(parsed_audit)

# TAB 2: HISTORICAL LOGS & ANALYTICS
with tab2:
    st.subheader("Historical Audit Records")
    records = fetch_all_audits()
    
    if records:
        df = pd.DataFrame(records, columns=["ID", "Timestamp", "Sentiment", "Payment Date", "Compliant", "Summary", "Transcript"])
        df["Compliant"] = df["Compliant"].apply(lambda x: "PASSED" if x == 1 else "FAILED")
        
        st.dataframe(df[["Timestamp", "Sentiment", "Payment Date", "Compliant", "Summary"]], use_container_width=True)
        
        # CSV Export Feature
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Compliance Audit Report (CSV)",
            data=csv_data,
            file_name="mahindra_finance_compliance_report.csv",
            mime="text/csv",
            type="primary"
        )

        st.divider()
        st.subheader("Analytics Summary")
        col_a, col_b = st.columns(2)
        col_a.write("**Customer Sentiment Distribution**")
        col_a.bar_chart(df["Sentiment"].value_counts())
        
        col_b.write("**Agent Compliance Pass/Fail**")
        col_b.bar_chart(df["Compliant"].value_counts())
    else:
        st.info("No audit records saved yet. Run an audit in Tab 1 to start populating data.")