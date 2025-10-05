from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_service import RAGService
from data_api import DataAPI
import os
import uvicorn

app = FastAPI(title="Aviation AI Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rag_service = RAGService()
data_api = DataAPI()

class QueryRequest(BaseModel):
    question: str
    context_type: str = "general"  # general, cargo, maintenance, regulations

class FlightQuery(BaseModel):
    flight_number: str = None
    date: str = None

@app.get("/")
async def root():
    return {"message": "Aviation AI Platform API"}

@app.post("/query")
async def query_rag(request: QueryRequest):
    try:
        response = rag_service.query(
            question=request.question,
            context_type=request.context_type
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/flights")
async def get_flights(flight_number: str = None, date: str = None):
    try:
        flights = data_api.get_flight_data(flight_number, date)
        return {"flights": flights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cargo/{flight_number}")
async def get_cargo_manifest(flight_number: str):
    try:
        cargo_data = data_api.get_cargo_manifest(flight_number)
        return cargo_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)