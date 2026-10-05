from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
import urllib.request
import urllib.parse
import json
import os

app = FastAPI(
    title="CogniCoreTech Enterprise API",
    description="Sovereign search engine powered by SearXNG meta-search architecture.",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reliable public SearXNG instances supporting JSON format
SEARXNG_INSTANCES = [
    "https://search.ononoki.org",
    "https://searx.be",
    "https://etsay.recursivo.org"
]

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return "<h1>CogniCoreTech Gateway Active</h1>"

@app.get("/opensearch.xml", response_class=Response)
def opensearch_xml():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/" xmlns:moz="http://www.mozilla.org/2006/browser/search/">
  <ShortName>CogniCoreTech</ShortName>
  <Description>CogniCoreTech Sovereign Search Engine - Seeta, Uganda</Description>
  <Image width="16" height="16" type="image/x-icon">https://cognicoretch-gateway.onrender.com/favicon.ico</Image>
  <Url type="text/html" template="https://cognicoretch-gateway.onrender.com/?q={searchTerms}"/>
  <Url type="application/x-suggestions+json" template="https://cognicoretch-gateway.onrender.com/api/v1/search?q={searchTerms}"/>
</OpenSearchDescription>
"""
    return Response(content=xml_content, media_type="application/opensearchdescription+xml")

@app.get("/health")
def health_check():
    return {"status": "healthy", "origin": "Seeta, Uganda", "engine": "SearXNG Meta-Search Gateway"}

@app.get("/api/v1/dashboard")
def get_dashboard_feeds():
    rates = [
        {"pair": "USD / UGX", "value": "3,987.25", "change": "+0.34%", "trend": "up"},
        {"pair": "EUR / UGX", "value": "4,120.50", "change": "-0.18%", "trend": "down"},
        {"pair": "GBP / UGX", "value": "4,945.10", "change": "+0.45%", "trend": "up"},
        {"pair": "KES / UGX", "value": "29.42", "change": "+0.08%", "trend": "up"}
    ]
    items = [
        {
            "title": "East African Community Finalizes Cross-Border Fintech Settlement Protocols",
            "category": "African Economy",
            "symbol": "EAC",
            "snippet": "Regional central banks met yesterday in Kampala to review monetary integration.",
            "url": "https://eac.int",
            "timestamp": "Yesterday"
        },
        {
            "title": "Seeta Tech Hub Launches Sovereign Zero-Trust Linux Kernel Security Standard",
            "category": "Technology",
            "symbol": "FOSS",
            "snippet": "Local software engineers released open-source memory safety toolsets for enterprise Linux.",
            "url": "https://github.com/try800756-hue/cognicoretch",
            "timestamp": "Today"
        }
    ]
    return {"rates": rates, "items": items}

@app.get("/api/v1/search")
def perform_search(q: str = Query(..., min_length=1)):
    encoded_query = urllib.parse.quote(q)
    results = []
    images = []

    # Attempt fetching from SearXNG instances
    success = False
    for instance in SEARXNG_INSTANCES:
        try:
            api_url = f"{instance}/search?q={encoded_query}&format=json"
            req = urllib.request.Request(
                api_url,
                headers={"User-Agent": "CogniCoreTechSovereignGateway/2.1 (Arch Linux FOSS Node)"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
                # Parse web results
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "snippet": item.get("content") or item.get("snippet", ""),
                        "type": "web"
                    })
                
                # Parse image results if available
                for img in data.get("infoboxes", []) or data.get("results", []):
                    if "img_src" in img or "thumbnail" in img:
                        images.append({
                            "title": img.get("title", q),
                            "url": img.get("url", "https://github.com/try800756-hue/cognicoretch"),
                            "thumb": img.get("img_src") or img.get("thumbnail"),
                            "source": "SearXNG Node"
                        })

                if results:
                    success = True
                    break
        except Exception:
            continue

    # Fallback if public instances fail temporarily
    if not results:
        results.append({
            "title": f"CogniCoreTech Sovereign Archive: {q.capitalize()}",
            "url": f"https://github.com/try800756-hue/cognicoretch",
            "snippet": f"Decentralized node record for {q}. Hosted locally from Seeta, Uganda.",
            "type": "web"
        })

    if not images:
        images = [
            {
                "title": f"{q.capitalize()} - Sovereign Architecture Asset",
                "url": "https://github.com/try800756-hue/cognicoretch",
                "thumb": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80",
                "source": "Seeta Node"
            }
        ]

    return {
        "query": q,
        "status": "success",
        "results": results[:15],
        "images": images[:6]
    }
