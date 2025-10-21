from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_service import RAGService
from data_api import DataAPI
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

app = FastAPI(title="Aviation AI Platform", version="1.0.0")

'''
 TODO:
    1) Pydoc
    2) Logging
    3) Traces
'''

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
    context_type: str = "general"

class TestRequest(BaseModel):
    test_message: str = "Test connection"

@app.get("/")
async def root():
    return {"message": "Aviation AI Platform API", "status": "healthy"}

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

@app.get("/cargo")
async def get_all_cargo():
    """Get all cargo manifests"""
    try:
        cargo_data = data_api.get_all_cargo_manifests()
        return {"cargo": cargo_data}
    except Exception as e:
        # Return sample data if real data fails
        sample_cargo = data_api.get_sample_cargo_data()
        return {"cargo": sample_cargo, "note": "Using sample data due to backend issue"}

@app.get("/cargo/{flight_number}")
async def get_cargo_by_flight(flight_number: str):
    """Get cargo manifests for a specific flight"""
    try:
        cargo_data = data_api.get_cargo_manifest(flight_number)
        return cargo_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-bedrock")
async def test_bedrock():
    """Test Bedrock connection"""
    try:
        status,message = rag_service.test_connection()
        return {"status": status, "result": message}
    except Exception as e:
        # str(e)
        raise HTTPException(status_code=500, detail="ERROR: Some error reported to bedrock connection.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)