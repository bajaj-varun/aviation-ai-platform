import React, { useState, useEffect } from 'react';
import '../styles/FlightOperations.css';

const FlightOperations = () => {
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    loadFlights();
  }, []);

  const loadFlights = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/flights');
      const data = await res.json();
      setFlights(data.flights || []);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to load flight data');
      // Load sample data if API fails
      setFlights(sampleFlights);
    }
    setLoading(false);
  };

  const filteredFlights = flights.filter(flight => 
    flight.flight_number.toLowerCase().includes(filter.toLowerCase()) ||
    flight.departure_airport.toLowerCase().includes(filter.toLowerCase()) ||
    flight.arrival_airport.toLowerCase().includes(filter.toLowerCase()) ||
    flight.status.toLowerCase().includes(filter.toLowerCase())
  );

  const getStatusBadge = (status) => {
    const statusClass = {
      'SCHEDULED': 'scheduled',
      'BOARDING': 'boarding',
      'DEPARTED': 'departed',
      'IN_FLIGHT': 'in-flight',
      'ARRIVED': 'arrived',
      'DELAYED': 'delayed',
      'CANCELLED': 'cancelled'
    }[status] || 'scheduled';
    
    return <span className={`status-badge ${statusClass}`}>{status}</span>;
  };

  const formatDateTime = (dateTime) => {
    if (!dateTime) return 'N/A';
    return new Date(dateTime).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flight-operations">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading flight data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flight-operations">
      <div className="operations-header">
        <h2>Flight Operations Dashboard</h2>
        <p>Real-time flight status and operational data</p>
      </div>

      <div className="controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search flights by number, route, or status..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
        
        <button onClick={loadFlights} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {error && (
        <div className="error-banner">
          {error} (Showing sample data)
        </div>
      )}

      <div className="flights-table-container">
        <table className="flights-table">
          <thead>
            <tr>
              <th>Flight Number</th>
              <th>Route</th>
              <th>Departure</th>
              <th>Arrival</th>
              <th>Status</th>
              <th>Aircraft</th>
              <th>Distance</th>
            </tr>
          </thead>
          <tbody>
            {filteredFlights.length > 0 ? (
              filteredFlights.map((flight, index) => (
                <tr key={index} className="flight-row">
                  <td className="flight-number">
                    <strong>{flight.flight_number}</strong>
                    <div className="airline-code">{flight.airline_code}</div>
                  </td>
                  <td className="route">
                    <div className="airports">
                      <span className="departure">{flight.departure_airport}</span>
                      <span className="arrow">→</span>
                      <span className="arrival">{flight.arrival_airport}</span>
                    </div>
                  </td>
                  <td className="time-cell">
                    <div className="scheduled">{formatDateTime(flight.scheduled_departure)}</div>
                    {flight.actual_departure && (
                      <div className="actual">Actual: {formatDateTime(flight.actual_departure)}</div>
                    )}
                  </td>
                  <td className="time-cell">
                    <div className="scheduled">{formatDateTime(flight.scheduled_arrival)}</div>
                    {flight.actual_arrival && (
                      <div className="actual">Actual: {formatDateTime(flight.actual_arrival)}</div>
                    )}
                  </td>
                  <td>{getStatusBadge(flight.status)}</td>
                  <td className="aircraft">{flight.aircraft_type || 'N/A'}</td>
                  <td className="distance">{flight.distance_km ? `${flight.distance_km.toLocaleString()} km` : 'N/A'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="no-data">
                  No flights found matching your search criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="table-footer">
        <div className="summary">
          Showing {filteredFlights.length} of {flights.length} flights
        </div>
      </div>
    </div>
  );
};

// Sample data for fallback
const sampleFlights = [
  {
    flight_number: "UA901",
    airline_code: "UAL",
    departure_airport: "JFK",
    arrival_airport: "LHR",
    scheduled_departure: "2024-01-15T18:30:00",
    scheduled_arrival: "2024-01-16T06:45:00",
    actual_departure: "2024-01-15T18:45:00",
    actual_arrival: "2024-01-16T07:00:00",
    status: "ARRIVED",
    aircraft_type: "Boeing 777-300ER",
    distance_km: 5534
  },
  {
    flight_number: "BA117",
    airline_code: "BAW",
    departure_airport: "LHR",
    arrival_airport: "DXB",
    scheduled_departure: "2024-01-15T20:15:00",
    scheduled_arrival: "2024-01-16T07:30:00",
    actual_departure: "2024-01-15T20:30:00",
    actual_arrival: "2024-01-16T07:45:00",
    status: "ARRIVED",
    aircraft_type: "Airbus A380",
    distance_km: 5490
  },
  {
    flight_number: "EK202",
    airline_code: "UAE",
    departure_airport: "DXB",
    arrival_airport: "SIN",
    scheduled_departure: "2024-01-16T02:00:00",
    scheduled_arrival: "2024-01-16T13:30:00",
    actual_departure: "2024-01-16T02:15:00",
    status: "IN_FLIGHT",
    aircraft_type: "Boeing 777-200LR",
    distance_km: 5845
  },
  {
    flight_number: "AA1234",
    airline_code: "AAL",
    departure_airport: "LAX",
    arrival_airport: "JFK",
    scheduled_departure: "2024-01-15T14:00:00",
    scheduled_arrival: "2024-01-15T22:30:00",
    actual_departure: "2024-01-15T14:20:00",
    actual_arrival: "2024-01-15T22:50:00",
    status: "ARRIVED",
    aircraft_type: "Boeing 737-800",
    distance_km: 3975
  }
];

export default FlightOperations;