from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import urllib.request
import urllib.parse
import json
import os

app = FastAPI(
    title="CogniCoreTech API",
    description="High-performance search gateway and developer tool suite.",
    version="0.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return "<h1>CogniCoreTech Gateway Active</h1><p>Frontend portal loading error.</p>"

@app.get("/health")
def health_check():
    return {"status": "healthy", "code": 200}

@app.get("/api/v1/search")
def perform_search(q: str = Query(..., min_length=1), category: str = Query("all")):
    results = []
    try:
        encoded_query = urllib.parse.quote(q)
        api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        req = urllib.request.Request(
            api_url, 
            headers={"User-Agent": "CogniCoreTech-Gateway/2.0 (Arch Linux FOSS Node)"}
        )
        
        with urllib.request.urlopen(req, timeout=5.0) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            # Primary Abstract Result
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", q),
                    "url": data.get("AbstractURL", f"https://duckduckgo.com/?q={encoded_query}"),
                    "snippet": data.get("AbstractText"),
                    "type": "reference"
                })
            
            # Related Topics / Web Results
            for topic in data.get("RelatedTopics", []):
                if "Text" in topic and "FirstURL" in topic:
                    text_val = topic.get("Text")
                    url_val = topic.get("FirstURL")
                    
                    # Categorize based on filter selection
                    item_type = "web"
                    if "github" in url_val.lower() or "code" in text_val.lower() or "linux" in text_val.lower():
                        item_type = "code"
                    elif "news" in text_val.lower() or "times" in text_val.lower() or "post" in text_val.lower():
                        item_type = "news"
                    elif "wiki" in url_val.lower() or "dictionary" in url_val.lower():
                        item_type = "media"

                    if category == "all" or category == item_type:
                        results.append({
                            "title": text_val.split(" - ")[0],
                            "url": url_val,
                            "snippet": text_val,
                            "type": item_type
                        })

        # Curated enterprise category fallbacks if standard API yields few results
        if len(results) < 3:
            if category == "news" or category == "all":
                results.append({
                    "title": f"Latest Global & Regional Headlines: {q}",
                    "url": f"https://news.google.com/search?q={encoded_query}",
                    "snippet": f"Real-time news feeds and media bulletins covering live updates for '{q}'.",
                    "type": "news"
                })
            if category == "code" or category == "all":
                results.append({
                    "title": f"Open Source Repositories & FOSS Packages: {q}",
                    "url": f"https://github.com/search?q={encoded_query}",
                    "snippet": f"Explore source code, libraries, and developer projects matching '{q}' on GitHub.",
                    "type": "code"
                })
            if category == "media" or category == "all":
                results.append({
                    "title": f"Visual & Reference Archives: {q}",
                    "url": f"https://duckduckgo.com/?q={encoded_query}&iax=images&ia=images",
                    "snippet": f"High-resolution media assets, image galleries, and encyclopedic references for '{q}'.",
                    "type": "media"
                })

        return {
            "query": q,
            "category": category,
            "status": "success",
            "results": results[:8]
        }
    except Exception as e:
        return {
            "query": q,
            "category": category,
            "status": "error",
            "results": [{
                "title": f"Gateway Exception for: {q}",
                "url": f"https://duckduckgo.com/?q={urllib.parse.quote(q)}",
                "snippet": f"Node warning: {str(e)}. Click to query directly on the web.",
                "type": "error"
            }]
        }
