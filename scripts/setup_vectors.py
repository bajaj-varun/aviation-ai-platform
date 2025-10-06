import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('./backend')

from app.rag_service import RAGService

# Sample aviation documents
aviation_docs = [
    {
        "text": """DANGEROUS GOODS REGULATIONS FOR LITHIUM BATTERIES - IATA DGR SECTION II

Lithium-ion batteries must be shipped at a state of charge not exceeding 30% of their rated capacity. 
Batteries must be packed in strong, rigid packaging and protected against short circuit. 
Passenger aircraft: Maximum net quantity of 5 kg per package. 
Cargo aircraft: Maximum net quantity of 35 kg per package.
All packages must be marked with "Lithium Ion Batteries" and Class 9 hazard label.
For defective or damaged batteries, special approval from the appropriate authority is required.
Batteries must be separated to prevent short circuits and packed to prevent movement within the package.""",
        "metadata": {
            "source": "IATA_DGR_Section_II",
            "doc_type": "regulation",
            "category": "dangerous_goods",
            "version": "2024.1"
        }
    },
    {
        "text": """AIRCRAFT LOADING PROCEDURES FOR BOEING 777-300ER

Maximum Zero Fuel Weight: 230,000 kg
Maximum Takeoff Weight: 351,500 kg
Maximum Landing Weight: 251,000 kg

LOADING PRINCIPLES:
- Ensure proper weight and balance calculations before loading
- Cargo must be properly secured using approved restraint systems
- Load distribution should maintain center of gravity within limits
- Special care required for live animals and perishable goods
- Dangerous goods must be loaded according to segregation requirements
- ULDs (Unit Load Devices) must be properly positioned and locked

BALANCE LIMITS:
- Forward CG limit: 15% MAC
- Aft CG limit: 35% MAC
- Optimal CG range: 20-30% MAC""",
        "metadata": {
            "source": "Boeing_777_Loading_Manual",
            "doc_type": "procedure",
            "category": "loading",
            "aircraft_type": "B777-300ER"
        }
    },
    {
        "text": """FLIGHT DELAY MANAGEMENT PROTOCOL - AIRLINE OPERATIONS MANUAL CHAPTER 7

DELAY CATEGORIES AND RESPONSIBILITIES:
1. DELAY 0-2 HOURS:
   - Provide passengers with refreshments
   - Communicate updates every 30 minutes
   - Coordinate with ground handling for basic services

2. DELAY 2-4 HOURS:
   - Arrange meal services
   - Provide access to communication facilities
   - Update passenger manifests for customs

3. DELAY EXCEEDS 4 HOURS:
   - Arrange hotel accommodation if necessary
   - Provide transportation to/from hotel
   - Process refunds or rebooking as per policy
   - Coordinate with immigration for overnight stays

COMMUNICATION PROTOCOL:
- Announce delay reasons and updated departure times every 30 minutes
- Designate staff to handle passenger inquiries
- Update flight information display systems
- Notify connecting flight operations""",
        "metadata": {
            "source": "Airline_Operations_Manual_Chapter7",
            "doc_type": "protocol",
            "category": "operations",
            "version": "3.2"
        }
    },
    {
        "text": """CARGO SECURITY PROTOCOLS - TSA AND ICAO STANDARDS

SECURITY SCREENING REQUIREMENTS:
1. All cargo must be screened before loading
2. Known consignor program for regular shippers
3. Screening methods: X-ray, EDS, physical search, canine
4. High-risk cargo requires enhanced screening

DOCUMENTATION REQUIREMENTS:
- Air Waybill with complete shipper/consignee information
- Security declaration form
- Dangerous goods declaration if applicable
- Export licenses for restricted items

ACCESS CONTROL:
- Cargo areas restricted to authorized personnel only
- Background checks for cargo handling staff
- Surveillance systems in cargo facilities
- Chain of custody documentation""",
        "metadata": {
            "source": "TSA_Cargo_Security_Manual",
            "doc_type": "security_protocol",
            "category": "security",
            "authority": "TSA_ICAO"
        }
    },
    {
        "text": """AIRCRAFT DEICING PROCEDURES - WINTER OPERATIONS

DEICING FLUIDS:
- Type I: Unthickened fluid for deicing
- Type II/IV: Thickened fluid for anti-icing
- Holdover time tables must be consulted

PROCEDURES:
1. Pre-flight inspection for ice accumulation
2. Deicing before departure if contamination exists
3. One-step or two-step process based on conditions
4. Communication between flight crew and deicing crew
5. Post-deicing inspection

SAFETY PRECAUTIONS:
- Safe distance from aircraft during operations
- Proper personal protective equipment
- Environmental protection measures
- Coordination with air traffic control""",
        "metadata": {
            "source": "Winter_Operations_Manual",
            "doc_type": "procedure",
            "category": "safety",
            "applicability": "cold_weather"
        }
    }
]

def setup_sample_data():
    rag_service = RAGService()
    rag_service.add_documents(aviation_docs)
    print("Sample aviation documents added to vector store!")

if __name__ == "__main__":
    setup_sample_data()