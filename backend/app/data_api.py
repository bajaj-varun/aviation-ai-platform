import snowflake.connector
import os
import pandas as pd
from typing import List, Dict, Optional

class DataAPI:
    def __init__(self):
        try:
            self.conn = snowflake.connector.connect(
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
                database=os.getenv('SNOWFLAKE_DATABASE'),
                schema=os.getenv('SNOWFLAKE_SCHEMA')
            )
        except Exception as e:
            print(f"Snowflake connection failed: {e}")
            self.conn = None
    
    def get_flight_data(self, flight_number: Optional[str] = None, date: Optional[str] = None) -> List[Dict]:
        """Get flight data from Snowflake"""
        if not self.conn:
            return self.get_sample_flight_data()
            
        query = """
        SELECT 
            flight_number,
            airline_code,
            departure_airport,
            arrival_airport,
            scheduled_departure,
            scheduled_arrival,
            actual_departure,
            actual_arrival,
            status,
            aircraft_type,
            distance_km
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
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            flights = []
            for row in results:
                flights.append({
                    "flight_number": row[0],
                    "airline_code": row[1],
                    "departure_airport": row[2],
                    "arrival_airport": row[3],
                    "scheduled_departure": row[4].isoformat() if row[4] else None,
                    "scheduled_arrival": row[5].isoformat() if row[5] else None,
                    "actual_departure": row[6].isoformat() if row[6] else None,
                    "actual_arrival": row[7].isoformat() if row[7] else None,
                    "status": row[8],
                    "aircraft_type": row[9],
                    "distance_km": float(row[10]) if row[10] else None
                })
            
            return flights
        except Exception as e:
            print(f"Error fetching flight data: {e}")
            return self.get_sample_flight_data()
    
    def get_all_cargo_manifests(self) -> List[Dict]:
        """Get all cargo manifests from Snowflake"""
        if not self.conn:
            return self.get_sample_cargo_data()
            
        query = """
        SELECT 
            flight_number,
            waybill_number,
            shipper_name,
            consignee_name,
            cargo_description,
            weight_kg,
            volume_cubic_m,
            special_handling,
            hazardous_material,
            hazmat_class,
            created_at
        FROM cargo_manifests
        ORDER BY created_at DESC
        LIMIT 100
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            cargo_data = []
            for row in results:
                cargo_data.append({
                    "flight_number": row[0],
                    "waybill_number": row[1],
                    "shipper_name": row[2],
                    "consignee_name": row[3],
                    "cargo_description": row[4],
                    "weight_kg": float(row[5]) if row[5] else 0,
                    "volume_cubic_m": float(row[6]) if row[6] else None,
                    "special_handling": row[7],
                    "hazardous_material": bool(row[8]),
                    "hazmat_class": row[9],
                    "created_at": row[10].isoformat() if row[10] else None
                })
            
            return cargo_data
        except Exception as e:
            print(f"Error fetching cargo data: {e}")
            return self.get_sample_cargo_data()
    
    def get_cargo_manifest(self, flight_number: str) -> Dict:
        """Get cargo manifest for a specific flight"""
        if not self.conn:
            return self.get_sample_cargo_by_flight(flight_number)
            
        query = """
        SELECT 
            cm.flight_number,
            cm.waybill_number,
            cm.shipper_name,
            cm.consignee_name,
            cm.cargo_description,
            cm.weight_kg,
            cm.volume_cubic_m,
            cm.special_handling,
            cm.hazardous_material,
            cm.hazmat_class
        FROM cargo_manifests cm
        WHERE cm.flight_number = %s
        """
        
        try:
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
                    "volume_cubic_m": float(row[6]) if row[6] else None,
                    "special_handling": row[7],
                    "hazardous_material": bool(row[8]),
                    "hazmat_class": row[9]
                })
                total_weight += float(row[5]) if row[5] else 0
            
            return {
                "flight_number": flight_number,
                "cargo_items": cargo_items,
                "total_weight_kg": total_weight,
                "item_count": len(cargo_items)
            }
        except Exception as e:
            print(f"Error fetching cargo manifest: {e}")
            return self.get_sample_cargo_by_flight(flight_number)
    
    def get_sample_flight_data(self) -> List[Dict]:
        """Return sample flight data for fallback"""
        return [
            {
                "flight_number": "UA901",
                "airline_code": "UAL",
                "departure_airport": "JFK",
                "arrival_airport": "LHR",
                "scheduled_departure": "2024-01-15T18:30:00",
                "scheduled_arrival": "2024-01-16T06:45:00",
                "actual_departure": "2024-01-15T18:45:00",
                "actual_arrival": "2024-01-16T07:00:00",
                "status": "ARRIVED",
                "aircraft_type": "Boeing 777-300ER",
                "distance_km": 5534
            },
            {
                "flight_number": "BA117",
                "airline_code": "BAW",
                "departure_airport": "LHR",
                "arrival_airport": "DXB",
                "scheduled_departure": "2024-01-15T20:15:00",
                "scheduled_arrival": "2024-01-16T07:30:00",
                "actual_departure": "2024-01-15T20:30:00",
                "actual_arrival": "2024-01-16T07:45:00",
                "status": "ARRIVED",
                "aircraft_type": "Airbus A380",
                "distance_km": 5490
            }
        ]
    
    def get_sample_cargo_data(self) -> List[Dict]:
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
            }
        ]
    
    def get_sample_cargo_by_flight(self, flight_number: str) -> Dict:
        """Return sample cargo data for a specific flight"""
        sample_data = {
            "flight_number": flight_number,
            "cargo_items": [
                {
                    "waybill_number": f"{flight_number}-001",
                    "shipper_name": "Sample Shipper",
                    "consignee_name": "Sample Consignee",
                    "cargo_description": "Sample cargo description",
                    "weight_kg": 1000.0,
                    "volume_cubic_m": 5.0,
                    "special_handling": "GENERAL",
                    "hazardous_material": False
                }
            ],
            "total_weight_kg": 1000.0,
            "item_count": 1
        }
        return sample_data