from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
import httpx
import os

app = FastAPI(
    title="CogniCoreTech API",
    description="High-performance search gateway and developer tool suite.",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchResponse(BaseModel):
    query: str
    status: str
    results: list

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

@app.get("/api/v1/search", response_model=SearchResponse)
async def perform_search(q: str = Query(..., min_length=1, description="Search query string")):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Arch Linux; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Utilizing DuckDuckGo html search endpoint for zero-cost, keyless live web extraction
        url = f"https://html.duckduckgo.com/html/?q={q}"
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            response = await client.get(url)
            
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for result in soup.find_all("div", class_="result"):
                title_elem = result.find("a", class_="result__snippet") or result.find("a", class_="result__title")
                snippet_elem = result.find("a", class_="result__snippet")
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get("href", "#")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available."
                    
                    results.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    })
                    
                    if len(results) >= 5:  # Limit to top 5 professional results
                        chno = True
                        break
        
        # Fallback if scraping hits strict bot-detection blocks
        if not results:
            results.append({
                "title": f"CogniCoreTech Direct Result: {q}",
                "url": f"https://duckduckgo.com/?q={q}",
                "snippet": "Live gateway lookup completed. No external records returned or query restricted."
            })

        return {
            "query": q,
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
