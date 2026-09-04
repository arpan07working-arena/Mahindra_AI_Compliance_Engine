from gtts import gTTS
import os

# Hinglish collection call script
sample_call_text = (
    "Hello, calling from Mahindra Finance. Your vehicle loan EMI of 8500 rupees was due on the 1st. "
    "When are you paying? "
    "Sir, please listen to me. My tractor had a breakdown this week and I had to spend money on repairs. "
    "I don't have the cash today. Please give me 3 days. "
    "I will definitely deposit the money by this Friday, I promise. "
    "Okay, ensuring the payment reflects by Friday. Thank you."
)

print("🎙️ Generating sample Hindi/Hinglish audio file...")

# Generate audio file using Indian English accent
tts = gTTS(text=sample_call_text, lang='en', tld='co.in')
tts.save("sample_call.mp3")

print("✅ Success! Created 'sample_call.mp3' in your project folder.")