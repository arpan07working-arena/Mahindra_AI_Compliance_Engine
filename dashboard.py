import streamlit as st
import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from database import init_db, save_audit, fetch_all_audits

# Initialize database
init_db()

st.set_page_config(page_title="Mahindra Finance AI Compliance", layout="wide")

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY not found in environment!")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=API_KEY)

st.title("🛡️ Mahindra Finance - Audio AI Compliance & Insights Engine")
st.markdown("Automated QA audit system for regional collection and customer service calls.")

tab1, tab2 = st.tabs(["🎙️ Audit New Call", "📊 Compliance History & Analytics"])

# TAB 1: LIVE AUDIT
with tab1:
    st.subheader("1. Upload Call Recording")
    uploaded_file = st.file_uploader("Choose an audio file (.mp3 / .wav)", type=["mp3", "wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
        
        if st.button("🚀 Run Compliance Audit", type="primary"):
            with st.spinner("Transcribing audio and analyzing compliance metrics..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    mime_type = "audio/mp3" if uploaded_file.name.endswith(".mp3") else "audio/wav"

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
                    """

                    # Send request using SDK
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_bytes(data=bytes_data, mime_type=mime_type),
                            prompt
                        ],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                    parsed_audit = json.loads(response.text)

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

                except Exception as e:
                    st.error(f"Audit Processing Error: {str(e)}")

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