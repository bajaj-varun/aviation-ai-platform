USE DATABASE AVIATION_DB;
USE SCHEMA AVIATION_DATA;

-- Insert sample flights data
INSERT INTO flights (
    flight_number, airline_code, departure_airport, arrival_airport,
    scheduled_departure, scheduled_arrival, actual_departure, actual_arrival,
    status, aircraft_type, distance_km, capacity_economy, capacity_business, capacity_first
) VALUES
-- International long-haul flights
('UA901', 'UAL', 'JFK', 'LHR', 
 '2024-01-15 18:30:00', '2024-01-16 06:45:00', '2024-01-15 18:45:00', '2024-01-16 07:00:00',
 'ARRIVED', 'Boeing 777-300ER', 5534, 300, 50, 8),

('BA117', 'BAW', 'LHR', 'DXB', 
 '2024-01-15 20:15:00', '2024-01-16 07:30:00', '2024-01-15 20:30:00', '2024-01-16 07:45:00',
 'ARRIVED', 'Airbus A380', 5490, 400, 60, 10),

('EK202', 'UAE', 'DXB', 'SIN', 
 '2024-01-16 02:00:00', '2024-01-16 13:30:00', '2024-01-16 02:15:00', '2024-01-16 13:45:00',
 'IN_FLIGHT', 'Boeing 777-200LR', 5845, 250, 40, 8),

('SQ305', 'SIA', 'SIN', 'SYD', 
 '2024-01-16 08:00:00', '2024-01-16 18:30:00', NULL, NULL,
 'SCHEDULED', 'Airbus A350', 6307, 280, 45, 6),

-- Domestic flights
('AA1234', 'AAL', 'LAX', 'JFK', 
 '2024-01-15 14:00:00', '2024-01-15 22:30:00', '2024-01-15 14:20:00', '2024-01-15 22:50:00',
 'ARRIVED', 'Boeing 737-800', 3975, 160, 16, 0),

('DL567', 'DAL', 'ATL', 'ORD', 
 '2024-01-15 16:45:00', '2024-01-15 18:00:00', '2024-01-15 16:45:00', '2024-01-15 17:55:00',
 'ARRIVED', 'Airbus A320', 944, 150, 12, 0),

('UA789', 'UAL', 'ORD', 'SFO', 
 '2024-01-15 19:30:00', '2024-01-15 22:15:00', NULL, NULL,
 'BOARDING', 'Boeing 757-200', 2960, 180, 20, 0),

-- Cargo flights
('FX5101', 'FDX', 'MEM', 'ANC', 
 '2024-01-15 23:00:00', '2024-01-16 04:30:00', '2024-01-15 23:10:00', '2024-01-16 04:40:00',
 'ARRIVED', 'Boeing 767F', 4440, 0, 0, 0),

('5Y800', 'GTI', 'ANC', 'PVG', 
 '2024-01-16 06:00:00', '2024-01-16 16:30:00', NULL, NULL,
 'SCHEDULED', 'Boeing 747-400F', 5550, 0, 0, 0);

-- Insert sample cargo manifests
INSERT INTO cargo_manifests (
    flight_number, waybill_number, shipper_name, consignee_name,
    cargo_description, weight_kg, volume_cubic_m, special_handling, hazardous_material, hazmat_class
) VALUES
-- Regular cargo
('FX5101', 'FX7894561230', 'MedTech Solutions Inc.', 'Alaska Medical Supplies',
 'Medical equipment and supplies', 4500.50, 12.5, 'TEMPERATURE_CONTROLLED', FALSE, NULL),

('FX5101', 'FX7894561231', 'ElectroCorp International', 'Northern Electronics Distributors',
 'Consumer electronics - smartphones and tablets', 3200.75, 8.2, 'FRAGILE', FALSE, NULL),

('5Y800', '5Y20240115001', 'AutoParts Manufacturing', 'Shanghai Automotive Group',
 'Automotive parts and components', 18500.00, 45.8, 'HEAVY', FALSE, NULL),

-- Hazardous materials
('5Y800', '5Y20240115002', 'ChemTech Laboratories', 'Shanghai Pharmaceutical Co.',
 'Lithium-ion batteries for medical devices', 650.25, 2.1, 'DANGEROUS_GOODS', TRUE, 'Class 9'),

('5Y800', '5Y20240115003', 'AeroSpace Components', 'China Aviation Industries',
 'Aircraft maintenance chemicals', 1200.50, 3.8, 'DANGEROUS_GOODS', TRUE, 'Class 8'),

-- Perishable goods
('UA901', 'UA20240115001', 'FreshFoods Exporters', 'London Gourmet Markets',
 'Fresh seafood and perishable foods', 2800.00, 15.3, 'PERISHABLE', FALSE, NULL),

('SQ305', 'SQ20240116001', 'Singapore Electronics', 'Sydney Tech Distributors',
 'High-value electronics and components', 4200.75, 9.6, 'HIGH_VALUE', FALSE, NULL);

-- Insert sample aircraft maintenance records
INSERT INTO aircraft_maintenance (
    aircraft_registration, aircraft_type, maintenance_type, maintenance_description,
    scheduled_date, completed_date, status, technician, next_due_date
) VALUES
('N123UA', 'Boeing 777-300ER', 'A Check', 'Routine maintenance and inspection',
 '2024-01-10', '2024-01-12', 'COMPLETED', 'John Anderson', '2024-04-10'),

('N456BA', 'Airbus A380', 'C Check', 'Heavy maintenance check - structural inspection',
 '2024-01-05', NULL, 'IN_PROGRESS', 'Sarah Chen', '2026-01-05'),

('N789EK', 'Boeing 777-200LR', 'A Check', 'Routine maintenance after long-haul flight',
 '2024-01-16', NULL, 'SCHEDULED', 'Mike Rodriguez', '2024-04-16'),

('N321SQ', 'Airbus A350', 'B Check', 'Intermediate maintenance check',
 '2024-01-14', '2024-01-15', 'COMPLETED', 'Emily Watson', '2024-07-14'),

('N654FX', 'Boeing 767F', 'A Check', 'Cargo aircraft routine inspection',
 '2024-01-13', '2024-01-13', 'COMPLETED', 'Robert Kim', '2024-04-13');

-- Insert sample passenger bookings
INSERT INTO passenger_bookings (
    flight_number, passenger_name, passenger_email, seat_number, class,
    special_assistance, booking_status, check_in_status, baggage_count
) VALUES
('UA901', 'John Smith', 'john.smith@email.com', '12A', 'BUSINESS',
 'None', 'CONFIRMED', TRUE, 2),

('UA901', 'Maria Garcia', 'maria.garcia@email.com', '12B', 'BUSINESS',
 'Vegetarian meal', 'CONFIRMED', TRUE, 1),

('UA901', 'David Johnson', 'david.johnson@email.com', '32C', 'ECONOMY',
 'Wheelchair assistance', 'CONFIRMED', TRUE, 1),

('BA117', 'Sarah Wilson', 'sarah.wilson@email.com', '8A', 'FIRST',
 'None', 'CONFIRMED', FALSE, 3),

('BA117', 'James Brown', 'james.brown@email.com', '45F', 'ECONOMY',
 'None', 'CONFIRMED', FALSE, 2),

('EK202', 'Lisa Taylor', 'lisa.taylor@email.com', '15C', 'BUSINESS',
 'Kosher meal', 'CONFIRMED', TRUE, 2),

('SQ305', 'Michael Davis', 'michael.davis@email.com', '28B', 'ECONOMY',
 'None', 'CONFIRMED', FALSE, 1);

-- Insert sample flight operations data
INSERT INTO flight_operations (
    flight_number, operation_date, fuel_consumption_kg, crew_count,
    catering_cost, ground_time_minutes, delay_minutes, delay_reason, weather_conditions
) VALUES
('UA901', '2024-01-15', 87500.50, 14, 4500.00, 45, 15, 'Late baggage loading', 'Clear'),

('AA1234', '2024-01-15', 18500.75, 6, 2200.00, 35, 20, 'Air traffic control', 'Cloudy'),

('DL567', '2024-01-15', 8200.25, 5, 1800.00, 30, 0, NULL, 'Clear'),

('FX5101', '2024-01-15', 32500.00, 3, 800.00, 25, 10, 'Cargo documentation check', 'Snow');