import React, { useState } from 'react';
import './styles/App.css';

const App = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [flights, setFlights] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');

  const handleQuery = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
          context_type: 'general'
        }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const loadFlights = async () => {
    try {
      const res = await fetch('http://localhost:8000/flights');
      const data = await res.json();
      setFlights(data.flights);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Aviation AI Intelligence Platform</h1>
        <p>AI-powered operations and support system</p>
      </header>

      <nav className="tabs">
        <button 
          className={activeTab === 'chat' ? 'active' : ''} 
          onClick={() => setActiveTab('chat')}
        >
          AI Assistant
        </button>
        <button 
          className={activeTab === 'flights' ? 'active' : ''} 
          onClick={() => {
            setActiveTab('flights');
            loadFlights();
          }}
        >
          Flight Operations
        </button>
        <button 
          className={activeTab === 'cargo' ? 'active' : ''} 
          onClick={() => setActiveTab('cargo')}
        >
          Cargo Management
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'chat' && (
          <div className="chat-container">
            <div className="query-section">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about flight procedures, cargo regulations, maintenance protocols..."
                rows="4"
              />
              <button onClick={handleQuery} disabled={loading}>
                {loading ? 'Processing...' : 'Ask AI Assistant'}
              </button>
            </div>

            {response && (
              <div className="response-section">
                <h3>Answer:</h3>
                <div className="answer">{response.answer}</div>
                
                <h4>Sources:</h4>
                <div className="sources">
                  {response.source_documents.map((doc, index) => (
                    <div key={index} className="source-doc">
                      <p>{doc.content.substring(0, 200)}...</p>
                      <small>Source: {doc.metadata.source || 'Unknown'}</small>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'flights' && (
          <div className="flights-container">
            <h2>Flight Operations</h2>
            <div className="flights-grid">
              {flights.map((flight, index) => (
                <div key={index} className="flight-card">
                  <h3>Flight {flight.flight_number}</h3>
                  <p><strong>Route:</strong> {flight.departure_airport} → {flight.arrival_airport}</p>
                  <p><strong>Status:</strong> <span className={`status-${flight.status}`}>{flight.status}</span></p>
                  <p><strong>Scheduled:</strong> {new Date(flight.scheduled_departure).toLocaleString()}</p>
                  <p><strong>Aircraft:</strong> {flight.aircraft_type}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'cargo' && (
          <div className="cargo-container">
            <h2>Cargo Management</h2>
            <p>Enter a flight number to view cargo manifest:</p>
            <div className="cargo-search">
              <input 
                type="text" 
                placeholder="Flight number (e.g., UA123)"
                id="cargoFlightNumber"
              />
              <button onClick={async () => {
                const flightNumber = document.getElementById('cargoFlightNumber').value;
                if (flightNumber) {
                  try {
                    const res = await fetch(`http://localhost:8000/cargo/${flightNumber}`);
                    const data = await res.json();
                    // Display cargo data
                    console.log(data);
                    alert(`Found ${data.item_count} cargo items for flight ${flightNumber}`);
                  } catch (error) {
                    console.error('Error:', error);
                  }
                }
              }}>
                Search Cargo
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;