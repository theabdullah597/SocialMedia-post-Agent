import { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000';

const PROGRESS_STEPS = [
  "Researching...",
  "Analyzing knowledge...",
  "Planning...",
  "Writing...",
  "Fact checking...",
  "Revising...",
  "Finalizing..."
];

function App() {
  const [topic, setTopic] = useState('');
  const [audience, setAudience] = useState('');
  const [platform, setPlatform] = useState('LinkedIn');
  const [tone, setTone] = useState('Professional');
  const [length, setLength] = useState('Medium');
  const [contentType, setContentType] = useState('educational post');
  
  const [isLoading, setIsLoading] = useState(false);
  const [progressIndex, setProgressIndex] = useState(0);
  
  const [result, setResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('content');
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    let interval: number;
    if (isLoading) {
      interval = setInterval(() => {
        setProgressIndex(prev => (prev < PROGRESS_STEPS.length - 1 ? prev + 1 : prev));
      }, 3000);
    } else {
      setProgressIndex(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleGenerate = async () => {
    if (!topic) return alert("Please enter a topic.");
    
    setIsLoading(true);
    setResult(null);
    setFeedback('');
    
    try {
      const res = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic, audience, platform, tone, length, content_type: contentType
        })
      });
      
      const data = await res.json();
      setResult(data);
    } catch (e) {
      alert("Error connecting to backend.");
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRevise = async () => {
    if (!feedback) return alert("Please enter feedback.");
    
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/revise`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: result.thread_id,
          feedback: feedback
        })
      });
      
      const data = await res.json();
      setResult(data);
      setFeedback('');
    } catch (e) {
      alert("Error requesting revision.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: result.thread_id })
      });
      
      const data = await res.json();
      setResult({ ...result, draft: data.final_content, status: 'completed' });
    } catch (e) {
      alert("Error approving content.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(result.draft);
    alert("Copied to clipboard!");
  };

  return (
    <div className="container">
      <header className="header">
        <h1>AI Content Agent</h1>
        <p>Advanced Agentic Social Media Creator</p>
      </header>
      
      <main className="main-content">
        <aside className="sidebar">
          <h3>Campaign Settings</h3>
          
          <div className="form-group">
            <label>Topic</label>
            <input value={topic} onChange={e => setTopic(e.target.value)} placeholder="e.g. How RAG works" />
          </div>
          
          <div className="form-group">
            <label>Audience</label>
            <input value={audience} onChange={e => setAudience(e.target.value)} placeholder="e.g. Beginner AI engineers" />
          </div>
          
          <div className="form-group">
            <label>Platform</label>
            <select value={platform} onChange={e => setPlatform(e.target.value)}>
              <option>LinkedIn</option>
              <option>X/Twitter</option>
              <option>Instagram</option>
              <option>Facebook</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Tone</label>
            <select value={tone} onChange={e => setTone(e.target.value)}>
              <option>Professional</option>
              <option>Educational</option>
              <option>Conversational</option>
              <option>Provocative</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Length</label>
            <select value={length} onChange={e => setLength(e.target.value)}>
              <option>Short</option>
              <option>Medium</option>
              <option>Long</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Content Type</label>
            <select value={contentType} onChange={e => setContentType(e.target.value)}>
              <option>educational post</option>
              <option>tutorial</option>
              <option>myth vs fact</option>
              <option>listicle</option>
              <option>carousel script</option>
              <option>short thread</option>
            </select>
          </div>
          
          <button className="primary-btn generate-btn" onClick={handleGenerate} disabled={isLoading}>
            {isLoading ? "Working..." : "Generate Content"}
          </button>
        </aside>
        
        <section className="results-panel">
          {isLoading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <h2>{PROGRESS_STEPS[progressIndex]}</h2>
              <p>The agent is autonomously operating...</p>
            </div>
          )}
          
          {!isLoading && result && (
            <div className="result-container">
              <div className="result-header">
                <div className="tabs">
                  <button className={activeTab === 'content' ? 'active' : ''} onClick={() => setActiveTab('content')}>Final Content</button>
                  <button className={activeTab === 'plan' ? 'active' : ''} onClick={() => setActiveTab('plan')}>Content Plan</button>
                  <button className={activeTab === 'critique' ? 'active' : ''} onClick={() => setActiveTab('critique')}>Critique</button>
                  <button className={activeTab === 'sources' ? 'active' : ''} onClick={() => setActiveTab('sources')}>Sources</button>
                </div>
                <div className="meta-badges">
                  <span className="badge">Revisions: {result.revision_count}</span>
                  <span className="badge">Platform: {result.platform}</span>
                </div>
              </div>
              
              <div className="tab-content">
                {activeTab === 'content' && (
                  <div className="content-view">
                    <pre className="draft-content">{result.draft}</pre>
                    
                    {result.status === 'waiting_for_review' && (
                      <div className="review-actions">
                        <div className="feedback-box">
                          <input 
                            value={feedback} 
                            onChange={e => setFeedback(e.target.value)} 
                            placeholder="Request changes (e.g., 'Make it shorter')" 
                          />
                          <button className="secondary-btn" onClick={handleRevise}>Request Changes</button>
                        </div>
                        <div className="approval-box">
                          <button className="primary-btn" onClick={handleApprove}>Approve Content</button>
                        </div>
                      </div>
                    )}
                    
                    {result.status === 'completed' && (
                      <div className="success-banner">
                        <p>✅ Content Finalized and Approved</p>
                      </div>
                    )}
                  </div>
                )}
                
                {activeTab === 'plan' && (
                  <pre className="document-view">{result.plan}</pre>
                )}
                
                {activeTab === 'critique' && (
                  <pre className="document-view">{result.critique}</pre>
                )}
                
                {activeTab === 'sources' && (
                  <div className="sources-view">
                    {result.sources && result.sources.length > 0 ? (
                      <ul>
                        {result.sources.map((s: any, i: number) => (
                          <li key={i}>
                            <strong>{s.title}</strong>
                            <a href={s.url} target="_blank" rel="noreferrer">{s.url}</a>
                            <p>{s.content}</p>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p>No web sources used.</p>
                    )}
                  </div>
                )}
              </div>
              
              <div className="action-bar">
                <button className="secondary-btn" onClick={handleCopy}>Copy Content</button>
                <button className="secondary-btn" onClick={handleGenerate}>Regenerate</button>
              </div>
            </div>
          )}
          
          {!isLoading && !result && (
            <div className="empty-state">
              <h2>Ready to build.</h2>
              <p>Configure your campaign settings and click Generate Content to start the agent.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
