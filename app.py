import requests
import json
import base64
import time
import os

API_KEY =  "AQ.Ab8RN6KBm58Yib7_MkDUAwn7gdwKK3ManP5PWk2ksx98crpA-w"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"

AUDIO_FILE_PATH = "sample_call.mp3"

if not os.path.exists(AUDIO_FILE_PATH):
    raise FileNotFoundError(f"Could not find {AUDIO_FILE_PATH}. Run generate_audio.py first!")

# Read the local .mp3 file and encode it to Base64
print("🎧 Reading and encoding audio file...")
with open(AUDIO_FILE_PATH, "rb") as audio_file:
    encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")

# Prompt instructing Gemini to listen, transcribe, and audit
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

# Format payload to send inline Base64 audio data to Gemini REST API
payload = {
    "contents": [{
        "parts": [
            {
                "inline_data": {
                    "mime_type": "audio/mp3",
                    "data": encoded_audio
                }
            },
            {
                "text": prompt
            }
        ]
    }],
    "generationConfig": {
        "response_mime_type": "application/json"
    }
}

headers = {'Content-Type': 'application/json'}

print("🚀 Sending raw audio to Gemini API for Multimodal Audit...")

for attempt in range(1, 4):
    response = requests.post(URL, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result_data = response.json()
        raw_json_string = result_data['candidates'][0]['content']['parts'][0]['text']
        
        parsed_audit = json.loads(raw_json_string)
        
        print("\n📊 --- COMPLETE AUDIO AUDIT LOG --- 📊")
        print(json.dumps(parsed_audit, indent=4))
        
        print("\n✅ Verification:")
        print(f"• Generated Transcript: {parsed_audit.get('transcript')[:80]}...")
        print(f"• Customer Sentiment:   {parsed_audit.get('customer_sentiment')}")
        print(f"• Payment Date:         {parsed_audit.get('promised_payment_date')}")
        print(f"• Agent Compliant:      {parsed_audit.get('agent_compliant')}")
        break
    elif response.status_code == 503:
        print(f"  [503 High Demand] Attempt {attempt}/3. Retrying in 2 seconds...")
        time.sleep(2)
    else:
        print(f"❌ Error Code {response.status_code}: {response.text}")
        break