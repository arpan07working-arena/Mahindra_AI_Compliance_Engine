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

st.set_page_config(
    page_title="Mahindra Finance AI Compliance Engine",
    page_icon="🛡️",
    layout="wide"
)

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY missing! Add it to .env or Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

st.title("🛡️ Mahindra Finance - Audio AI Compliance & Insights Engine")
st.caption("Automated QA & RBI Regulatory Compliance Audit System for Collection & Service Calls")

tab1, tab2 = st.tabs(["🎙️ Audit New Call", "📊 Compliance History & Analytics"])

# TAB 1: LIVE AUDIT
with tab1:
    st.subheader("1. Upload Call Recording")
    uploaded_file = st.file_uploader("Upload Audio File (.mp3 / .wav)", type=["mp3", "wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
        
        if st.button("🚀 Run Compliance Audit", type="primary"):
            with st.spinner("Analyzing call against RBI guidelines & Mahindra Finance compliance rules..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    mime_type = "audio/mp3" if uploaded_file.name.endswith(".mp3") else "audio/wav"

                    prompt = """
                    You are a Senior Quality Assurance & Regulatory Compliance Auditor at Mahindra Finance.
                    Audit this collection/customer service audio recording based on strict RBI Recovery Agent Guidelines.

                    Check for:
                    1. Self-Identification: Agent states full name & company representation at the start.
                    2. Tone & Professionalism: Zero abusive, harassing, or threatening language.
                    3. Customer Sentiment: Cooperative, Angry, or Distressed.
                    4. Promised Payment Date: Extract date string (e.g., YYYY-MM-DD or Day) or "None".

                    Respond STRICTLY with a valid JSON object matching this schema:
                    {
                      "transcript": "Full verbatim text transcript",
                      "agent_identifies_self": true | false,
                      "customer_sentiment": "Cooperative" | "Angry" | "Distressed",
                      "promised_payment_date": "string or None",
                      "agent_compliant": true | false,
                      "violations": ["List specific violations like 'No self-identification', 'Threatening tone' or 'None'"],
                      "summary": "Short 1-sentence audit summary"
                    }
                    """

                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
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

                    st.success("Audit Completed & Logged to Database!")
                    st.divider()

                    # Audit Scorecard Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Customer Sentiment", parsed_audit.get("customer_sentiment", "N/A"))
                    col2.metric("Payment Promise", parsed_audit.get("promised_payment_date", "N/A"))
                    col3.metric("Self-Identified", "YES" if parsed_audit.get("agent_identifies_self") else "NO")
                    col4.metric(
                        "RBI Compliance Status", 
                        "PASSED" if parsed_audit.get("agent_compliant") else "FAILED",
                        delta="Compliant" if parsed_audit.get("agent_compliant") else "Violation Detected",
                        delta_color="normal" if parsed_audit.get("agent_compliant") else "inverse"
                    )

                    st.divider()
                    st.subheader("2. Compliance Findings & Transcript")
                    
                    violations = parsed_audit.get("violations", [])
                    if violations and "None" not in violations:
                        st.error(f"⚠️ **Detected Violations:** {', '.join(violations)}")
                    else:
                        st.success("✅ **No Regulatory Violations Detected.**")

                    st.info(f"**Executive Summary:** {parsed_audit.get('summary')}")
                    
                    with st.expander("📄 View Full Verbatim Transcript"):
                        st.write(parsed_audit.get("transcript"))

                    with st.expander("🔍 View Raw JSON Audit Payload"):
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
        
        # Action Toolbar
        col_dl, col_blank = st.columns([1, 3])
        with col_dl:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Compliance Report (CSV)",
                data=csv_data,
                file_name="mahindra_finance_compliance_report.csv",
                mime="text/csv",
                type="primary"
            )

        st.divider()
        st.subheader("Analytics Overview")
        col_a, col_b = st.columns(2)
        col_a.write("**Customer Sentiment Distribution**")
        col_a.bar_chart(df["Sentiment"].value_counts())
        
        col_b.write("**Agent Compliance Breakdown**")
        col_b.bar_chart(df["Compliant"].value_counts())
    else:
        st.info("No audit logs found. Run an audio evaluation in Tab 1 to populate metrics.")