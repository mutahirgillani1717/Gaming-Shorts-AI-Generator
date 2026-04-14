import streamlit as st
import json
import requests
from groq import Groq

# 1. Securely load API keys from Streamlit's secret manager
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# --- Core Logic Functions ---
def fetch_universal_news(topic):
    url = "https://google.serper.dev/news"
    payload = json.dumps({
        "q": f"{topic} latest news OR interesting facts OR updates",
        "num": 3
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    news_data = response.json()
    
    scraped_intel = ""
    for item in news_data.get('news', []):
        scraped_intel += f"Headline: {item.get('title')}\nSummary: {item.get('snippet')}\n\n"
    return scraped_intel

def generate_universal_script(topic, intel_data):
    client = Groq(api_key=GROQ_API_KEY)
    system_prompt = """You are an expert YouTube Shorts scriptwriter. 
    Your goal is to write a fast-paced, high-retention 60-second script based on the provided news or facts.
    Rules:
    1. Start with a strong, curiosity-driven HOOK (0-3 seconds).
    2. Keep the BODY concise, energetic, and focused on the most interesting details.
    3. End with a quick OUTRO asking viewers to subscribe for more.
    4. Do not output anything except the script itself. Use brackets for visual cues like [Show image]."""
    
    user_prompt = f"Topic: {topic}\n\nLatest Intel/Facts:\n{intel_data}\n\nWrite the viral script now."

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.1-8b-instant", 
        temperature=0.7,        
        max_tokens=500
    )
    return response.choices[0].message.content

# --- The User Interface ---
st.set_page_config(page_title="Viral Script Generator", page_icon="🎬")

st.title("🌟 Universal YouTube Shorts Generator")
st.markdown("Enter any topic below, and the AI will scrape the web for the latest intel to write a viral 60-second script.")

# UI Input
user_topic = st.text_input("Enter your topic (e.g., SpaceX, Ancient Rome, GTA VI):")

# UI Button
if st.button("Generate Script 🚀"):
    if user_topic:
        with st.spinner(f"Scouring the web for the latest intel on '{user_topic}'..."):
            topic_intel = fetch_universal_news(user_topic)
            
        with st.spinner("AI Brain is formatting the data into a script..."):
            final_script = generate_universal_script(user_topic, topic_intel)
            
        st.success("Script Generated Successfully!")
        st.markdown("### 🎬 Your Viral Script:")
        
        # Display the script in a nice formatted box
        st.info(final_script)
    else:
        st.warning("Please enter a topic first!")
