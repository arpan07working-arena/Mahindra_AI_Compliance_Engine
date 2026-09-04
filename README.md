# Mahindra Finance — Audio AI Compliance Engine 🎙️⚡

An automated QA audit system designed for regional collection and customer service calls. Built with Python, Streamlit, SQLite, and Google Gemini API to accelerate call evaluation and compliance tracking.

🔗 **Live Application:** [Your Streamlit App URL Here]

## Key Features
* **AI Audio Analysis:** Automates call audits using Gemini API to evaluate agent sentiment, payment commitments, and regulatory adherence.
* **Structured Data Persistence:** Stores compliance outcomes, timestamped call metadata, and audit flags in an embedded SQLite database.
* **Interactive Analytics Dashboard:** Real-time visual metrics built with Streamlit and Pandas tracking agent pass/fail distributions.
* **Production-Ready Security:** API key management handled via Streamlit Secrets and `.gitignore` safety policies.

## Tech Stack
* **Language:** Python 3.13
* **Frontend UI:** Streamlit
* **Database:** SQLite3 / Pandas
* **AI Engine:** Google Gemini API
* **Version Control & Hosting:** Git, GitHub, Streamlit Cloud

## System Architecture
## 🏗️ System Architecture

```text
  [ User Uploads .mp3/.wav ]
              │
              ▼
    [ Streamlit Web UI ] ──(Audio Bytes & Prompt)──► [ Google Gemini 3.6 Flash ]
              │                                                │
      (Renders Dashboard)                                (JSON Payload)
              ▲                                                │
              │                                                ▼
     [ Pandas / Charts ] ◄─── [ SQLite Database ] ◄─── [ Audit Parser ]
