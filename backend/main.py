from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import urllib.request
import urllib.parse
import json
import re
import os

app = FastAPI(
    title="CogniCoreTech API",
    description="High-performance search gateway and developer tool suite.",
    version="0.3.0"
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
def perform_search(q: str = Query(..., min_length=1, description="Search query string")):
    results = []
    try:
        # Use DuckDuckGo Instant Answer API for zero-cost, real-time structured data without external packages
        encoded_query = urllib.parse.quote(q)
        api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        req = urllib.request.Request(
            api_url, 
            headers={"User-Agent": "CogniCoreTech-Gateway/1.0 (Arch Linux FOSS Node)"}
        )
        
        with urllib.request.urlopen(req, timeout=5.0) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            # Extract Abstract Results
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", q),
                    "url": data.get("AbstractURL", f"https://duckduckgo.com/?q={encoded_query}"),
                    "snippet": data.get("AbstractText")
                })
            
            # Extract Related Topics (Live web matches)
            for topic in data.get("RelatedTopics", []):
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "title": topic.get("Text").split(" - ")[0],
                        "url": topic.get("FirstURL"),
                        "snippet": topic.get("Text")
                    })
                    if len(results) >= 5:
                        break
                        
        # Fallback to direct HTML search parsing if API returns empty abstract fields
        if not results:
            html_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            html_req = urllib.request.Request(
                html_url,
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
            )
            with urllib.request.urlopen(html_req, timeout=5.0) as html_resp:
                html_content = html_resp.read().decode("utf-8")
                # Simple regex extraction for DuckDuckGo HTML result snippets and links
                snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html_content, re.DOTALL)
                titles = re.findall(r'<a class="result__url"[^>]*>(.*?)</a>', html_content, re.DOTALL)
                
                for i in range(min(len(snippets), 3)):
                    clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                    results.append({
                        "title": f"Live Web Result {i+1} for: {q}",
                        "url": f"https://duckduckgo.com/?q={encoded_query}",
                        "snippet": clean_snippet
                    })

        # Ultimate fallback if both return nothing
        if not results:
            results.append({
                "title": f"DuckDuckGo Search Gateway: {q}",
                "url": f"https://duckduckgo.com/?q={encoded_query}",
                "snippet": f"Click to view live community search query results for '{q}' directly on DuckDuckGo."
            })

        return {
            "query": q,
            "status": "success",
            "results": results
        }
    except Exception as e:
        return {
            "query": q,
            "status": "error",
            "results": [{
                "title": f"Gateway Query Error for: {q}",
                "url": f"https://duckduckgo.com/?q={urllib.parse.quote(q)}",
                "snippet": f"Connection exception caught: {str(e)}. Click to search directly."
            }]
        }
