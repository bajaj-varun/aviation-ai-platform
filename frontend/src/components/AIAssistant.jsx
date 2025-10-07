import React, { useState } from 'react';
import '../styles/AIAssistant.css';

const AIAssistant = () => {
  const [query, setQuery] = useState('');
  const [contextType, setContextType] = useState('general');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const apiUrl = import.meta.env.VITE_API_URL;
  // TODO: Need to remove
  console.info("apiurl =>",apiUrl)

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    const userMessage = { type: 'user', content: query, context: contextType };
    
    try {
      const res = await fetch(`${apiUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
          context_type: contextType
        }),
      });
      
      const data = await res.json();
      const assistantMessage = { 
        type: 'assistant', 
        content: data.answer, 
        sources: data.source_documents 
      };
      
      setChatHistory(prev => [...prev, userMessage, assistantMessage]);
      setResponse(data);
      setQuery('');
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { 
        type: 'error', 
        content: 'Failed to get response. Please try again.' 
      };
      setChatHistory(prev => [...prev, userMessage, errorMessage]);
    }
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  const clearChat = () => {
    setChatHistory([]);
    setResponse(null);
  };

  return (
    <div className="ai-assistant">
      <div className="assistant-header">
        <h2>AI Aviation Assistant</h2>
        <p>Get expert answers about flight operations, cargo regulations, and maintenance procedures</p>
      </div>

      <div className="input-section">
        <div className="input-group">
          <label htmlFor="context-type">Context Type:</label>
          <select 
            id="context-type"
            value={contextType} 
            onChange={(e) => setContextType(e.target.value)}
            className="context-select"
          >
            <option value="general">General</option>
            <option value="cargo">Cargo</option>
            <option value="maintenance">Maintenance</option>
            <option value="regulations">Regulations</option>
          </select>
        </div>

        <div className="input-group">
          <label htmlFor="question-input">Your Question:</label>
          <textarea
            id="question-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about flight procedures, cargo regulations, maintenance protocols..."
            rows="4"
            disabled={loading}
          />
        </div>

        <div className="button-group">
          <button 
            onClick={handleQuery} 
            disabled={loading || !query.trim()}
            className="ask-button"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              'Ask AI Assistant'
            )}
          </button>
          
          <button 
            onClick={clearChat}
            className="clear-button"
            disabled={chatHistory.length === 0}
          >
            Clear Chat
          </button>
        </div>
      </div>

      <div className="chat-section">
        {chatHistory.length > 0 ? (
          <div className="chat-history">
            {chatHistory.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                <div className="message-header">
                  <span className="message-type">
                    {message.type === 'user' ? '👤 You' : 
                     message.type === 'assistant' ? '🤖 Assistant' : '❌ Error'}
                  </span>
                  {message.context && (
                    <span className="context-badge">{message.context}</span>
                  )}
                </div>
                <div className="message-content">
                  {message.content}
                </div>
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <strong>Sources:</strong>
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="source-item">
                        <div className="source-content">
                          {source.content.substring(0, 150)}...
                        </div>
                        <div className="source-meta">
                          {source.metadata.source || 'Unknown source'} • 
                          {source.metadata.category || 'General'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h3>Start a conversation</h3>
            <p>Ask a question about aviation operations, regulations, or procedures to get started.</p>
            <div className="example-questions">
              <h4>Try asking:</h4>
              <ul>
                <li>What are the regulations for shipping lithium batteries?</li>
                <li>How should I handle a flight delay?</li>
                <li>What are the loading procedures for a Boeing 777?</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIAssistant;