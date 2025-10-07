import React, { useState, useEffect } from 'react';
import '../styles/CargoManagement.css';

const CargoManagement = () => {
  const [cargoData, setCargoData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredData, setFilteredData] = useState([]);
  const [error, setError] = useState(null);
  const apiUrl = import.meta.env.VITE_API_URL;
  // TODO: Need to remove
  console.info("apiurl =>",apiUrl)

  useEffect(() => {
    loadCargoData();
  }, []);

  useEffect(() => {
    filterCargoData();
  }, [searchTerm, cargoData]);

  const loadCargoData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/cargo`);
      // console.debug("cargo data=>",response.json())

      const data = await response.json();
      
      if (data.cargo && Array.isArray(data.cargo)) {
        setCargoData(data.cargo);
        
        // Show note if using sample data
        if (data.note) {
          setError(data.note);
        }
      } else {
        throw new Error('Invalid data format received');
      }
    } catch (error) {
      console.error('Error loading cargo data:', error);
      setError('Failed to load cargo data from server');
      // Fallback to sample data
      setCargoData(getSampleCargoData());
    } finally {
      setLoading(false);
    }
  };

  const filterCargoData = () => {
    if (!searchTerm.trim()) {
      setFilteredData(cargoData);
      return;
    }

    const searchLower = searchTerm.toLowerCase();
    const filtered = cargoData.filter(item =>
      item.flight_number.toLowerCase().includes(searchLower) ||
      item.waybill_number.toLowerCase().includes(searchLower) ||
      item.shipper_name.toLowerCase().includes(searchLower) ||
      item.consignee_name.toLowerCase().includes(searchLower) ||
      item.cargo_description.toLowerCase().includes(searchLower) ||
      (item.hazardous_material && 'hazardous dangerous'.includes(searchLower)) ||
      (item.special_handling && item.special_handling.toLowerCase().includes(searchLower))
    );
    
    setFilteredData(filtered);
  };

  const getHazardousBadge = (isHazardous, hazmatClass) => {
    if (!isHazardous) return null;
    
    return (
      <span className={`hazardous-badge ${hazmatClass?.toLowerCase() || 'class-9'}`}>
        ⚠️ HAZMAT {hazmatClass || 'Class 9'}
      </span>
    );
  };

  const getSpecialHandlingBadge = (handling) => {
    if (!handling) return null;
    
    const handlingIcons = {
      'TEMPERATURE_CONTROLLED': '❄️',
      'FRAGILE': '🎯',
      'HEAVY': '⚖️',
      'HIGH_VALUE': '💎',
      'PERISHABLE': '⏰',
      'DANGEROUS_GOODS': '⚠️'
    };
    
    return (
      <span className="handling-badge">
        {handlingIcons[handling] || '📦'} {handling.replace('_', ' ')}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="cargo-management">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading cargo data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="cargo-management">
      <div className="cargo-header">
        <h2>Cargo Management System</h2>
        <p>Manage and track cargo shipments across all flights</p>
      </div>

      <div className="cargo-controls">
        <div className="search-section">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by flight, waybill, shipper, consignee, or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <span className="search-icon">🔍</span>
          </div>
          <div className="search-stats">
            Showing {filteredData.length} of {cargoData.length} shipments
          </div>
        </div>

        <button onClick={loadCargoData} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {error && (
        <div className="info-banner">
          {error}
        </div>
      )}

      <div className="cargo-grid">
        {filteredData.length > 0 ? (
          filteredData.map((item, index) => (
            <div key={`${item.flight_number}-${item.waybill_number}-${index}`} className="cargo-card">
              <div className="card-header">
                <div className="flight-info">
                  <span className="flight-number">✈️ {item.flight_number}</span>
                  <span className="waybill">📋 {item.waybill_number}</span>
                </div>
                <div className="weight-info">
                  <span className="weight">{item.weight_kg?.toLocaleString()} kg</span>
                  {item.volume_cubic_m && (
                    <span className="volume">{item.volume_cubic_m} m³</span>
                  )}
                </div>
              </div>

              <div className="card-content">
                <div className="parties">
                  <div className="shipper">
                    <strong>Shipper:</strong>
                    <span>{item.shipper_name}</span>
                  </div>
                  <div className="consignee">
                    <strong>Consignee:</strong>
                    <span>{item.consignee_name}</span>
                  </div>
                </div>

                <div className="cargo-description">
                  <strong>Description:</strong>
                  <p>{item.cargo_description}</p>
                </div>

                <div className="special-info">
                  {getHazardousBadge(item.hazardous_material, item.hazmat_class)}
                  {getSpecialHandlingBadge(item.special_handling)}
                </div>
              </div>

              <div className="card-footer">
                <div className="status-indicators">
                  {item.hazardous_material && (
                    <span className="hazard-indicator">⚠️ Hazardous</span>
                  )}
                  {item.special_handling && (
                    <span className="handling-indicator">🔄 Special Handling</span>
                  )}
                </div>
                <div className="timestamp">
                  {formatDate(item.created_at)}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="no-cargo">
            <div className="no-cargo-icon">📭</div>
            <h3>No cargo shipments found</h3>
            <p>Try adjusting your search terms or check back later for new shipments.</p>
          </div>
        )}
      </div>

      <div className="cargo-summary">
        <div className="summary-card total-weight">
          <h4>Total Weight</h4>
          <p>{filteredData.reduce((sum, item) => sum + (item.weight_kg || 0), 0).toLocaleString()} kg</p>
        </div>
        <div className="summary-card total-shipments">
          <h4>Total Shipments</h4>
          <p>{filteredData.length}</p>
        </div>
        <div className="summary-card hazardous-count">
          <h4>Hazardous Shipments</h4>
          <p>{filteredData.filter(item => item.hazardous_material).length}</p>
        </div>
        <div className="summary-card unique-flights">
          <h4>Unique Flights</h4>
          <p>{new Set(filteredData.map(item => item.flight_number)).size}</p>
        </div>
      </div>
    </div>
  );
};

// Fallback sample data (in case API fails completely)
const getSampleCargoData = () => {
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
      "hazardous_material": false,
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
      "hazardous_material": true,
      "hazmat_class": "Class 9",
      "created_at": "2024-01-15T15:00:00"
    }
  ];
};

export default CargoManagement;