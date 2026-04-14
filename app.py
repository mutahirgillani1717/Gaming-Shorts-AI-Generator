def fetch_universal_news(topic):
    url = "https://google.serper.dev/news"
    payload = json.dumps({"q": f"{topic} latest news OR interesting facts OR updates", "num": 3})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(url, headers=headers, data=payload)
    news_data = response.json()
    
    news_items = news_data.get('news', [])
    
    # GUARDRAIL 1: If no news is found, stop the process.
    if len(news_items) == 0:
        return "NO_DATA"
    
    scraped_intel = ""
    for item in news_items:
        scraped_intel += f"Headline: {item.get('title')}\nSummary: {item.get('snippet')}\n\n"
    return scraped_intel
