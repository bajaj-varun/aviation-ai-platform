-- Data validation queries
USE DATABASE AVIATION_DB;
USE SCHEMA AVIATION_DATA;

-- Check flight counts by status
SELECT status, COUNT(*) as flight_count
FROM flights
GROUP BY status
ORDER BY flight_count DESC;

-- Check cargo summary
SELECT 
    COUNT(*) as total_shipments,
    SUM(weight_kg) as total_weight_kg,
    AVG(weight_kg) as avg_weight_kg,
    COUNT(CASE WHEN hazardous_material THEN 1 END) as hazardous_shipments
FROM cargo_manifests;

-- Check maintenance status
SELECT status, COUNT(*) as maintenance_count
FROM aircraft_maintenance
GROUP BY status;

-- Check passenger bookings by class
SELECT class, COUNT(*) as passenger_count
FROM passenger_bookings
GROUP BY class;

-- Flight delays analysis
SELECT 
    AVG(TIMEDIFF(minute, scheduled_departure, actual_departure)) as avg_departure_delay_min,
    MAX(TIMEDIFF(minute, scheduled_departure, actual_departure)) as max_departure_delay_min
FROM flights
WHERE actual_departure IS NOT NULL;

-- Cargo by flight
SELECT 
    f.flight_number,
    f.departure_airport,
    f.arrival_airport,
    COUNT(cm.manifest_id) as shipment_count,
    SUM(cm.weight_kg) as total_weight_kg
FROM flights f
LEFT JOIN cargo_manifests cm ON f.flight_number = cm.flight_number
GROUP BY f.flight_number, f.departure_airport, f.arrival_airport
ORDER BY total_weight_kg DESC;