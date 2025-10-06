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
        sample_cargo = get_sample_cargo_data()
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
        if hasattr(rag_service, 'test_connection'):
            result = rag_service.test_connection()
        else:
            # Simple test query
            result = rag_service.query("Please respond with 'OK' to confirm the connection is working.")
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/available-models")
async def get_available_models():
    """Get available Claude models"""
    try:
        if hasattr(rag_service, 'get_available_models'):
            models = rag_service.get_available_models()
            return {"available_models": models}
        else:
            return {"available_models": ["anthropic.claude-3-5-sonnet-20240620-v1:0"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_sample_cargo_data():
    """Return sample cargo data for fallback"""
    return [
        {
            "flight_number": "FX5101",
            "waybill_number": "FX7894561230",
            "shipper_name": "MedTech Solutions Inc.",
            "consignee_name": "Alaska Medical Supplies",
            "cargo_description": "Medical equipment and supplies",
            "weight_kg": 4500.50,
            "volume_cubic_m": 12.5,
            "special_handling": "TEMPERATURE_CONTROLLED",
            "hazardous_material": False,
            "created_at": "2024-01-15T10:00:00"
        },
        {
            "flight_number": "FX5101",
            "waybill_number": "FX7894561231",
            "shipper_name": "ElectroCorp International",
            "consignee_name": "Northern Electronics Distributors",
            "cargo_description": "Consumer electronics - smartphones and tablets",
            "weight_kg": 3200.75,
            "volume_cubic_m": 8.2,
            "special_handling": "FRAGILE",
            "hazardous_material": False,
            "created_at": "2024-01-15T10:15:00"
        },
        {
            "flight_number": "5Y800",
            "waybill_number": "5Y20240115001",
            "shipper_name": "AutoParts Manufacturing",
            "consignee_name": "Shanghai Automotive Group",
            "cargo_description": "Automotive parts and components",
            "weight_kg": 18500.00,
            "volume_cubic_m": 45.8,
            "special_handling": "HEAVY",
            "hazardous_material": False,
            "created_at": "2024-01-15T14:30:00"
        },
        {
            "flight_number": "5Y800",
            "waybill_number": "5Y20240115002",
            "shipper_name": "ChemTech Laboratories",
            "consignee_name": "Shanghai Pharmaceutical Co.",
            "cargo_description": "Lithium-ion batteries for medical devices",
            "weight_kg": 650.25,
            "volume_cubic_m": 2.1,
            "special_handling": "DANGEROUS_GOODS",
            "hazardous_material": True,
            "hazmat_class": "Class 9",
            "created_at": "2024-01-15T15:00:00"
        },
        {
            "flight_number": "UA901",
            "waybill_number": "UA20240115001",
            "shipper_name": "FreshFoods Exporters",
            "consignee_name": "London Gourmet Markets",
            "cargo_description": "Fresh seafood and perishable foods",
            "weight_kg": 2800.00,
            "volume_cubic_m": 15.3,
            "special_handling": "PERISHABLE",
            "hazardous_material": False,
            "created_at": "2024-01-15T16:00:00"
        },
        {
            "flight_number": "SQ305",
            "waybill_number": "SQ20240116001",
            "shipper_name": "Singapore Electronics",
            "consignee_name": "Sydney Tech Distributors",
            "cargo_description": "High-value electronics and components",
            "weight_kg": 4200.75,
            "volume_cubic_m": 9.6,
            "special_handling": "HIGH_VALUE",
            "hazardous_material": False,
            "created_at": "2024-01-16T08:00:00"
        },
        {
            "flight_number": "BA117",
            "waybill_number": "BA20240115001",
            "shipper_name": "UK Pharmaceuticals Ltd",
            "consignee_name": "Dubai Medical Center",
            "cargo_description": "Pharmaceutical supplies and vaccines",
            "weight_kg": 1800.25,
            "volume_cubic_m": 6.8,
            "special_handling": "TEMPERATURE_CONTROLLED",
            "hazardous_material": False,
            "created_at": "2024-01-15T18:00:00"
        },
        {
            "flight_number": "EK202",
            "waybill_number": "EK20240116001",
            "shipper_name": "Middle East Logistics",
            "consignee_name": "Singapore Trading Co.",
            "cargo_description": "Industrial machinery parts",
            "weight_kg": 7500.00,
            "volume_cubic_m": 22.5,
            "special_handling": "HEAVY",
            "hazardous_material": False,
            "created_at": "2024-01-16T01:00:00"
        }
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)