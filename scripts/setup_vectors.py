import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('./backend')

from app.rag_service import RAGService

# Sample aviation documents
aviation_docs = [
    {
        "text": """Dangerous Goods Regulations for Lithium Batteries:
        
Lithium-ion batteries must be shipped at a state of charge not exceeding 30% of their rated capacity. 
Batteries must be packed in strong, rigid packaging and protected against short circuit. 
Passenger aircraft: Maximum net quantity of 5 kg per package. 
Cargo aircraft: Maximum net quantity of 35 kg per package.
All packages must be marked with "Lithium Ion Batteries" and Class 9 hazard label.""",
        "metadata": {
            "source": "IATA_DGR_Section_II",
            "doc_type": "regulation",
            "category": "dangerous_goods"
        }
    },
    {
        "text": """Aircraft Loading Procedures for Wide-body Aircraft:
        
Ensure proper weight and balance calculations before loading. 
Maximum zero fuel weight: 230,000 kg for Boeing 777-300ER.
Cargo must be properly secured using approved restraint systems.
Load distribution should maintain center of gravity within limits.
Special care required for live animals and perishable goods.""",
        "metadata": {
            "source": "Boeing_777_Loading_Manual",
            "doc_type": "procedure",
            "category": "loading"
        }
    },
    {
        "text": """Flight Delay Management Protocol:
        
For delays exceeding 2 hours, provide passengers with refreshments.
For delays exceeding 4 hours, arrange meal services and accommodation if necessary.
Communicate delay reasons and updated departure times every 30 minutes.
Coordinate with ground handling for aircraft servicing during delays.
Maintain passenger manifest updates for customs and immigration.""",
        "metadata": {
            "source": "Airline_Operations_Manual",
            "doc_type": "protocol",
            "category": "operations"
        }
    }
]

def setup_sample_data():
    rag_service = RAGService()
    rag_service.add_documents(aviation_docs)
    print("Sample aviation documents added to vector store!")

if __name__ == "__main__":
    setup_sample_data()