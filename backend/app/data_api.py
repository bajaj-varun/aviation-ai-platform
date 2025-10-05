import snowflake.connector
import os
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class DataAPI:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
    
    def get_flight_data(self, flight_number: Optional[str] = None, date: Optional[str] = None) -> List[Dict]:
        query = """
        SELECT 
            flight_number,
            departure_airport,
            arrival_airport,
            scheduled_departure,
            scheduled_arrival,
            actual_departure,
            actual_arrival,
            status,
            aircraft_type
        FROM flights 
        WHERE 1=1
        """
        
        params = []
        if flight_number:
            query += " AND flight_number = %s"
            params.append(flight_number)
        if date:
            query += " AND DATE(scheduled_departure) = %s"
            params.append(date)
        
        query += " ORDER BY scheduled_departure LIMIT 50"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        flights = []
        for row in results:
            flights.append({
                "flight_number": row[0],
                "departure_airport": row[1],
                "arrival_airport": row[2],
                "scheduled_departure": row[3].isoformat() if row[3] else None,
                "scheduled_arrival": row[4].isoformat() if row[4] else None,
                "actual_departure": row[5].isoformat() if row[5] else None,
                "actual_arrival": row[6].isoformat() if row[6] else None,
                "status": row[7],
                "aircraft_type": row[8]
            })
        
        return flights
    
    def get_cargo_manifest(self, flight_number: str) -> Dict:
        query = """
        SELECT 
            cm.flight_number,
            cm.waybill_number,
            cm.shipper_name,
            cm.consignee_name,
            cm.cargo_description,
            cm.weight_kg,
            cm.special_handling,
            cm.hazardous_material
        FROM cargo_manifests cm
        WHERE cm.flight_number = %s
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (flight_number,))
        results = cursor.fetchall()
        
        cargo_items = []
        total_weight = 0
        
        for row in results:
            cargo_items.append({
                "waybill_number": row[1],
                "shipper_name": row[2],
                "consignee_name": row[3],
                "cargo_description": row[4],
                "weight_kg": float(row[5]) if row[5] else 0,
                "special_handling": row[6],
                "hazardous_material": row[7]
            })
            total_weight += float(row[5]) if row[5] else 0
        
        return {
            "flight_number": flight_number,
            "cargo_items": cargo_items,
            "total_weight_kg": total_weight,
            "item_count": len(cargo_items)
        }