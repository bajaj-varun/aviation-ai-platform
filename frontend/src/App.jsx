import React, { useState } from 'react';
import AIAssistant from './components/AIAssistant';
import FlightOperations from './components/FlightOperations';
import CargoManagement from './components/CargoManagement';
import './styles/App.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('ai-assistant');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'ai-assistant':
        return <AIAssistant />;
      case 'flight-operations':
        return <FlightOperations />;
      case 'cargo-management':
        return <CargoManagement />;
      default:
        return <AIAssistant />;
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
          className={activeTab === 'ai-assistant' ? 'active' : ''} 
          onClick={() => setActiveTab('ai-assistant')}
        >
          🤖 AI Assistant
        </button>
        <button 
          className={activeTab === 'flight-operations' ? 'active' : ''} 
          onClick={() => setActiveTab('flight-operations')}
        >
          ✈️ Flight Operations
        </button>
        <button 
          className={activeTab === 'cargo-management' ? 'active' : ''} 
          onClick={() => setActiveTab('cargo-management')}
        >
          📦 Cargo Management
        </button>
      </nav>

      <main className="main-content">
        {renderActiveTab()}
      </main>
    </div>
  );
};

export default App;