import snowflake.connector
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()

class SnowflakeDataLoader:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
    
    def execute_sql_file(self, file_path):
        """Execute SQL commands from a file"""
        with open(file_path, 'r') as file:
            sql_commands = file.read()
        
        # Split commands by semicolon
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        cursor = self.conn.cursor()
        for command in commands:
            try:
                cursor.execute(command)
                print(f"Executed: {command[:50]}...")
            except Exception as e:
                print(f"Error executing command: {e}")
        cursor.close()
    
    def generate_additional_flight_data(self):
        """Generate additional realistic flight data"""
        cursor = self.conn.cursor()
        
        # Generate flights for the next 7 days
        base_date = datetime.now()
        airlines = ['UAL', 'AAL', 'DAL', 'BAW', 'UAE', 'SIA', 'AFR', 'LUF']
        aircraft_types = ['Boeing 737-800', 'Airbus A320', 'Boeing 757-200', 
                         'Airbus A321', 'Boeing 787-9', 'Airbus A330-300']
        
        routes = [
            ('JFK', 'LAX', 3975), ('LAX', 'ORD', 2800), ('ORD', 'DFW', 1290),
            ('DFW', 'ATL', 1180), ('ATL', 'DEN', 1950), ('DEN', 'SFO', 1265),
            ('SFO', 'SEA', 1090), ('SEA', 'JFK', 3860), ('MIA', 'JFK', 1765)
        ]
        
        for i in range(50):  # Generate 50 additional flights
            flight_date = base_date + timedelta(days=i % 7)
            airline = airlines[i % len(airlines)]
            flight_num = f"{airline}{1000 + i}"
            dep_airport, arr_airport, distance = routes[i % len(routes)]
            aircraft = aircraft_types[i % len(aircraft_types)]
            
            scheduled_dep = flight_date.replace(hour=6 + (i % 12), minute=0, second=0)
            scheduled_arr = scheduled_dep + timedelta(hours=3 + (i % 4))
            
            insert_query = """
            INSERT INTO flights (
                flight_number, airline_code, departure_airport, arrival_airport,
                scheduled_departure, scheduled_arrival, status, aircraft_type, distance_km,
                capacity_economy, capacity_business, capacity_first
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                flight_num, airline, dep_airport, arr_airport,
                scheduled_dep, scheduled_arr, 'SCHEDULED', aircraft, distance,
                150 + (i % 50), 20 + (i % 10), 4 + (i % 4)
            ))
        
        cursor.close()
        print("Generated additional flight data")
    
    def load_from_csv(self, csv_file, table_name):
        """Load data from CSV file to Snowflake table"""
        try:
            df = pd.read_csv(csv_file)
            cursor = self.conn.cursor()
            
            # Generate placeholders for SQL
            placeholders = ', '.join(['%s'] * len(df.columns))
            columns = ', '.join(df.columns)
            
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            for _, row in df.iterrows():
                cursor.execute(insert_query, tuple(row))
            
            cursor.close()
            print(f"Loaded data from {csv_file} to {table_name}")
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
    
    def create_sample_views(self):
        """Create useful views for reporting"""
        cursor = self.conn.cursor()
        
        views = {
            "flight_delays_view": """
            CREATE OR REPLACE VIEW flight_delays_view AS
            SELECT 
                flight_number,
                departure_airport,
                arrival_airport,
                scheduled_departure,
                actual_departure,
                TIMEDIFF(minute, scheduled_departure, actual_departure) as departure_delay_minutes,
                status
            FROM flights
            WHERE actual_departure IS NOT NULL
            """,
            
            "cargo_summary_view": """
            CREATE OR REPLACE VIEW cargo_summary_view AS
            SELECT 
                flight_number,
                COUNT(*) as total_shipments,
                SUM(weight_kg) as total_weight_kg,
                SUM(CASE WHEN hazardous_material THEN 1 ELSE 0 END) as hazardous_shipments,
                AVG(weight_kg) as avg_shipment_weight
            FROM cargo_manifests
            GROUP BY flight_number
            """,
            
            "maintenance_schedule_view": """
            CREATE OR REPLACE VIEW maintenance_schedule_view AS
            SELECT 
                aircraft_registration,
                aircraft_type,
                maintenance_type,
                scheduled_date,
                completed_date,
                status,
                DATEDIFF(day, CURRENT_DATE(), scheduled_date) as days_until_due
            FROM aircraft_maintenance
            WHERE status IN ('SCHEDULED', 'IN_PROGRESS')
            """
        }
        
        for view_name, view_query in views.items():
            try:
                cursor.execute(view_query)
                print(f"Created view: {view_name}")
            except Exception as e:
                print(f"Error creating view {view_name}: {e}")
        
        cursor.close()
    
    def close(self):
        self.conn.close()

def main():
    loader = SnowflakeDataLoader()
    
    try:
        print("Starting Snowflake data setup...")
        
        # Step 1: Create tables
        print("Creating tables...")
        loader.execute_sql_file('scripts/snowflake-setup.sql')
        
        # Step 2: Insert sample data
        print("Inserting sample data...")
        loader.execute_sql_file('scripts/sample-data-insertion.sql')
        
        # Step 3: Generate additional flight data
        print("Generating additional flight data...")
        loader.generate_additional_flight_data()
        
        # Step 4: Create views
        print("Creating analytical views...")
        loader.create_sample_views()
        
        print("Snowflake data setup completed successfully!")
        
    except Exception as e:
        print(f"Error during data setup: {e}")
    finally:
        loader.close()

if __name__ == "__main__":
    main()