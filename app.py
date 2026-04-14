import streamlit as st
import json
import requests
from groq import Groq
import time

# --- 1. PAGE CONFIGURATION & CUSTOM CSS ---
st.set_page_config(page_title="Neural_Script // Generator", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
        .stApp {
            background-color: #0a0a0a;
            color: #00ffcc;
            font-family: 'Courier New', Courier, monospace;
        }
        h1, h2, h3 {
            color: #ff0055 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        div.stButton > button {
            background-color: transparent;
            color: #00ffcc;
            border: 1px solid #00ffcc;
            border-radius: 0px;
            padding: 10px 24px;
            transition: 0.3s;
            width: 100%;
        }
        div.stButton > button:hover {
            background-color: #00ffcc;
            color: #000000;
            box-shadow: 0 0 15px #00ffcc;
        }
        .streamlit-expanderHeader {
            color: #ff0055;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. SECURE API KEYS ---
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# --- 3. CORE LOGIC (With Strict Guardrails) ---
def fetch_universal_news(topic):
    url = "https://google.serper.dev/news"
    
    # EXACT MATCH: Added quotes around {topic} to force strict Google searches
    payload = json.dumps({"q": f"\"{topic}\" (latest news OR interesting facts OR updates)", "num": 3})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(url, headers=headers, data=payload)
    news_data = response.json()
    
    news_items = news_data.get('news', [])
    
    # GUARDRAIL 1: Stop if no exact data is found
    if len(news_items) == 0:
        return "NO_DATA"
    
    scraped_intel = ""
    for item in news_items:
        scraped_intel += f"Headline: {item.get('title')}\nSummary: {item.get('snippet')}\n\n"
    return scraped_intel

def generate_universal_script(topic, intel_data):
    client = Groq(api_key=GROQ_API_KEY)
    
    # RELEVANCE CHECK: Rule 5 forces the LLM to verify data before writing
    system_prompt = """You are an expert YouTube Shorts scriptwriter. 
    Your goal is to write a fast-paced, high-retention 60-second script based ONLY on the provided news or facts.
    Rules:
    1. Start with a strong, curiosity-driven HOOK.
    2. Keep the BODY concise and focused on the hidden details.
    3. End with a quick OUTRO.
    4. Do not output anything except the script itself. Use brackets for visual cues.
    5. CRITICAL RELEVANCE CHECK: First, verify that the provided Intel/Facts are actually about the requested Topic. If the intel is completely unrelated to the topic, DO NOT try to force a connection. Output EXACTLY: "ERROR_404: Insufficient real-world data to generate a factual script." """
    
    user_prompt = f"Topic: {topic}\n\nLatest Intel/Facts:\n{intel_data}\n\nWrite the viral script now."

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        model="llama-3.1-8b-instant", 
        temperature=0.7,        
        max_tokens=500
    )
    return response.choices[0].message.content

# --- 4. THE USER INTERFACE ---
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM STATUS")
    st.success("API: GROQ Llama-3.1 (ONLINE)")
    st.success("API: Serper.dev (ONLINE)")
    st.divider()
    st.markdown("**Developer:** Syed Mutahir Hussain")
    st.markdown("**Role:** AI & Machine Learning Engineer")
    st.markdown("*This pipeline bypasses manual research by scraping real-time data and formatting it via LLMs.*")

st.title("⚡ NEURAL_SCRIPT // PIPELINE")
st.markdown("`> INITIALIZE AUTOMATED CONTENT GENERATION`")
st.divider()

user_topic = st.text_input("ENTER TARGET TOPIC_")

if st.button("EXECUTE PIPELINE"):
    if user_topic:
        progress_bar = st.progress(0)
        
        with st.spinner("`> Establishing connection to data sources...`"):
            topic_intel = fetch_universal_news(user_topic)
            progress_bar.progress(50)
            time.sleep(0.5)
            
        # Check Guardrail 1 (Empty Search)
        if topic_intel == "NO_DATA":
            st.error("`> ERROR 404: INSUFFICIENT INTEL.`")
            st.warning("The web scraper could not find enough verified facts on this topic to prevent AI hallucination. Please try a more prominent or recent topic.")
            progress_bar.empty()
        else:
            with st.spinner("`> Injecting data into Llama-3.1 model...`"):
                final_script = generate_universal_script(user_topic, topic_intel)
                progress_bar.progress(100)
                
            st.divider()
            
            # Check Guardrail 2 (Irrelevant Data / Hallucination Risk)
            if "ERROR_404" in final_script:
                st.error("`> LLM REFUSAL: HALLUCINATION RISK DETECTED.`")
                st.warning("The AI determined that the scraped data was irrelevant to your topic and refused to generate a fake script.")
            else:
                st.subheader("🟢 OUTPUT: OPTIMIZED SCRIPT")
                st.code(final_script, language="markdown")
            
            with st.expander("View Raw Extracted Intel (Debugging)"):
                st.text(topic_intel)
    else:
        st.error("`> ERROR: NO TOPIC DETECTED. PLEASE ENTER TARGET DATA.`")
