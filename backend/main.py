from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
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
    try:
        mock_results = [
            {
                "title": f"CogniCoreTech Index Result for: {q}",
                "url": f"https://github.com/try800756-hue/cognicoretch",
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
