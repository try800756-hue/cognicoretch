from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI(
    title="CogniCoreTech API",
    description="High-performance search gateway and developer tool suite.",
    version="0.1.0"
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

@app.get("/")
def read_root():
    return {
        "system": "CogniCoreTech Core Gateway",
        "status": "operational",
        "environment": "production-ready"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "code": 200}

@app.get("/api/v1/search", response_model=SearchResponse)
async def perform_search(q: str = Query(..., min_length=1, description="Search query string")):
    try:
        mock_results = [
            {
                "title": f"CogniCoreTech Index Result for: {q}",
                "url": f"https://cognicoretch.com/search?q={q}",
                "snippet": "Lightning-fast, privacy-first search aggregation powered by your independent enterprise infrastructure."
            }
        ]
        return {
            "query": q,
            "status": "success",
            "results": mock_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
