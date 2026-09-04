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

# Custom CSS for Modern Fintech Branding
st.markdown("""
<style>
    /* Main Background Accent & Font Styling */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Header Card Styling */
    .header-card {
        background: linear-gradient(135deg, #1E222D 0%, #11141C 100%);
        padding: 24px;
        border-radius: 12px;
        border-left: 6px solid #D32F2F;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin-bottom: 24px;
    }
    .header-title {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #9E9E9E;
        font-size: 14px;
        margin-top: 4px;
    }

    /* Metric Cards Custom Styling */
    [data-testid="stMetricValue"] {
        font-size: 22px !important;
        font-weight: 700 !important;
    }
    div[data-testid="metric-container"] {
        background-color: #1A1D24;
        border: 1px solid #2D313E;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    /* Tab Header Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #161920;
        border-radius: 8px 8px 0px 0px;
        color: #B0B0B0;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #222733 !important;
        color: #FF5252 !important;
        border-bottom: 2px solid #D32F2F !important;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY missing! Add it to .env or Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# Branded Banner Header
st.markdown("""
<div class="header-card">
    <div class="header-title">🛡️ Mahindra Finance - Audio AI Compliance Engine</div>
    <div class="header-subtitle">Automated QA & RBI Regulatory Compliance Audit System for Collection & Customer Service Calls</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎙️ Live Audio Audit", "📊 Compliance History & Analytics"])

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
        
        # Download Action
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