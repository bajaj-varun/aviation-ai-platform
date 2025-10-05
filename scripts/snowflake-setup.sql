-- Create database and schema
CREATE DATABASE IF NOT EXISTS AVIATION_DB;
USE DATABASE AVIATION_DB;

CREATE SCHEMA IF NOT EXISTS AVIATION_DATA;
USE SCHEMA AVIATION_DATA;

-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS AVIATION_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 300
  AUTO_RESUME = TRUE;

-- Flights table
CREATE OR REPLACE TABLE flights (
    flight_id NUMBER AUTOINCREMENT,
    flight_number VARCHAR(10) NOT NULL,
    airline_code VARCHAR(3) NOT NULL,
    departure_airport VARCHAR(3) NOT NULL,
    arrival_airport VARCHAR(3) NOT NULL,
    scheduled_departure TIMESTAMP_NTZ,
    scheduled_arrival TIMESTAMP_NTZ,
    actual_departure TIMESTAMP_NTZ,
    actual_arrival TIMESTAMP_NTZ,
    status VARCHAR(20) DEFAULT 'SCHEDULED',
    aircraft_type VARCHAR(20),
    distance_km NUMBER(10,2),
    capacity_economy NUMBER(4),
    capacity_business NUMBER(4),
    capacity_first NUMBER(4),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Cargo manifests table
CREATE OR REPLACE TABLE cargo_manifests (
    manifest_id NUMBER AUTOINCREMENT,
    flight_number VARCHAR(10) NOT NULL,
    waybill_number VARCHAR(20) NOT NULL,
    shipper_name VARCHAR(100) NOT NULL,
    shipper_address VARCHAR(200),
    consignee_name VARCHAR(100) NOT NULL,
    consignee_address VARCHAR(200),
    cargo_description VARCHAR(200) NOT NULL,
    weight_kg NUMBER(10,2) NOT NULL,
    volume_cubic_m NUMBER(8,3),
    special_handling VARCHAR(100),
    hazardous_material BOOLEAN DEFAULT FALSE,
    hazmat_class VARCHAR(10),
    storage_requirements VARCHAR(100),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Aircraft maintenance table
CREATE OR REPLACE TABLE aircraft_maintenance (
    maintenance_id NUMBER AUTOINCREMENT,
    aircraft_registration VARCHAR(10) NOT NULL,
    aircraft_type VARCHAR(20) NOT NULL,
    maintenance_type VARCHAR(50) NOT NULL,
    maintenance_description VARCHAR(500),
    scheduled_date DATE,
    completed_date DATE,
    status VARCHAR(20) DEFAULT 'SCHEDULED',
    technician VARCHAR(100),
    parts_used VARCHAR(500),
    next_due_date DATE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Passenger bookings table
CREATE OR REPLACE TABLE passenger_bookings (
    booking_id NUMBER AUTOINCREMENT,
    flight_number VARCHAR(10) NOT NULL,
    passenger_name VARCHAR(100) NOT NULL,
    passenger_email VARCHAR(100),
    seat_number VARCHAR(5),
    class VARCHAR(20) DEFAULT 'ECONOMY',
    special_assistance VARCHAR(200),
    booking_status VARCHAR(20) DEFAULT 'CONFIRMED',
    check_in_status BOOLEAN DEFAULT FALSE,
    baggage_count NUMBER(2) DEFAULT 1,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Flight operations table
CREATE OR REPLACE TABLE flight_operations (
    operation_id NUMBER AUTOINCREMENT,
    flight_number VARCHAR(10) NOT NULL,
    operation_date DATE NOT NULL,
    fuel_consumption_kg NUMBER(10,2),
    crew_count NUMBER(2),
    catering_cost NUMBER(10,2),
    ground_time_minutes NUMBER(4),
    delay_minutes NUMBER(4),
    delay_reason VARCHAR(200),
    weather_conditions VARCHAR(100),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);