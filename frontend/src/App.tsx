import { useState, useEffect } from 'react';
import { Sparkles, Plus, RefreshCw, AlertTriangle } from 'lucide-react';
import { ENDPOINTS, PROJECT_NAME, PROJECT_SUBTITLE } from './config';
import StartupForm from './components/StartupForm';
import WorkflowVisualizer from './components/WorkflowVisualizer';
import AgentLogs from './components/AgentLogs';
import ReportViewer from './components/ReportViewer';
import HistoryPanel from './components/HistoryPanel';

interface HistoryItem {
  id: string;
  idea: string;
  status: string;
  created_at: string;
}

interface ValidationRun {
  id: string;
  idea: string;
  status: string;
  current_agent: string;
  plan: string;
  competitors: any[];
  market_analysis: any;
  risks: any;
  tech_stack: any;
  report: string;
  logs: string[];
  created_at: string;
}

export default function App() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [currentRun, setCurrentRun] = useState<ValidationRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Load History on Mount
  useEffect(() => {
    fetchHistory();
    document.title = `${PROJECT_NAME} - Dynamic Validation Engine`;
  }, []);

  // 2. Poll Status when running is active
  useEffect(() => {
    let intervalId: any;

    if (selectedRunId) {
      // Immediate fetch
      fetchRunDetails(selectedRunId);

      // Setup interval polling if run is running
      intervalId = setInterval(() => {
        if (currentRun && (currentRun.status === 'PENDING' || currentRun.status === 'RUNNING')) {
          fetchRunDetails(selectedRunId);
        } else if (currentRun && (currentRun.status === 'COMPLETED' || currentRun.status === 'FAILED')) {
          clearInterval(intervalId);
          setLoading(false);
        }
      }, 1500);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [selectedRunId, currentRun?.status]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(ENDPOINTS.history);
      if (!res.ok) throw new Error("Failed to load history lists");
      const data = await res.json();
      setHistory(data);
    } catch (err: any) {
      console.error(err);
      setError("Unable to connect to the backend server. Make sure FastAPI is running.");
    }
  };

  const fetchRunDetails = async (id: string) => {
    try {
      const res = await fetch(ENDPOINTS.status(id));
      if (!res.ok) throw new Error("Failed to load run details");
      const data = await res.json();
      setCurrentRun(data);
      
      // Update history list item status dynamically
      setHistory(prev => prev.map(item => 
        item.id === id ? { ...item, status: data.status } : item
      ));

      if (data.status === 'FAILED') {
        setLoading(false);
      }
    } catch (err: any) {
      console.error(err);
      setError("Error loading execution details.");
    }
  };

  const handleValidateIdea = async (idea: string) => {
    setLoading(true);
    setError(null);
    setCurrentRun(null);

    try {
      const res = await fetch(ENDPOINTS.validate, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea })
      });

      if (!res.ok) {
        const errDetail = await res.json();
        throw new Error(errDetail.detail || "Submission failed");
      }

      const data = await res.json();
      setSelectedRunId(data.id);
      setCurrentRun(data);
      
      // Refresh list to include new item
      await fetchHistory();
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to submit startup idea.");
      setLoading(false);
    }
  };

  const startNewValidation = () => {
    setSelectedRunId(null);
    setCurrentRun(null);
    setError(null);
    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* Page Header */}
      <header className="app-header">
        <h1 className="app-logo">
          {PROJECT_NAME} <span>{PROJECT_SUBTITLE}</span>
        </h1>
        
        <div style={{ display: 'flex', gap: '10px' }}>
          {selectedRunId && (
            <button
              onClick={startNewValidation}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'var(--text-primary)',
                borderRadius: '8px',
                padding: '8px 16px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.85rem',
                fontFamily: 'var(--font-family-title)',
              }}
            >
              <Plus size={14} />
              New Validation
            </button>
          )}
          <button
            onClick={fetchHistory}
            style={{
              background: 'transparent',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              color: 'var(--text-muted)',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
            }}
            title="Refresh history"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </header>

      {/* Connection Error Banner */}
      {error && (
        <div 
          className="glass-panel" 
          style={{ 
            borderColor: 'var(--danger)', 
            background: 'rgba(239, 68, 68, 0.05)', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '12px',
            padding: '16px 20px'
          }}
        >
          <AlertTriangle color="var(--danger)" size={20} />
          <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>{error}</span>
        </div>
      )}

      {/* Main Grid Content */}
      <div className="dashboard-grid">
        {/* Left Side: history log */}
        <HistoryPanel
          history={history}
          selectedId={selectedRunId}
          onSelect={(id) => {
            setError(null);
            setSelectedRunId(id);
          }}
        />

        {/* Right Side: main screen */}
        <main className="work-area">
          {!selectedRunId ? (
            <StartupForm onSubmit={handleValidateIdea} isLoading={loading} />
          ) : (
            currentRun && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                
                {/* Active Graph Orchestrator Status */}
                <WorkflowVisualizer
                  currentAgent={currentRun.current_agent}
                  status={currentRun.status}
                />

                {/* Live Output Audit Trails */}
                <AgentLogs logs={currentRun.logs || []} />

                {/* Final Dashboard & Markdown document container */}
                {currentRun.status === 'COMPLETED' && currentRun.report && (
                  <ReportViewer
                    report={currentRun.report}
                    competitors={currentRun.competitors || []}
                    marketAnalysis={currentRun.market_analysis || {}}
                    risks={currentRun.risks || {}}
                    techStack={currentRun.tech_stack || {}}
                  />
                )}

                {/* Running state notice */}
                {(currentRun.status === 'PENDING' || currentRun.status === 'RUNNING') && (
                  <div className="glass-panel" style={{ textAlign: 'center', padding: '40px 20px' }}>
                    <Sparkles 
                      className="animate-spin" 
                      size={28} 
                      color="var(--primary-color)" 
                      style={{ margin: '0 auto 12px auto' }} 
                    />
                    <h4 style={{ fontFamily: 'var(--font-family-title)', marginBottom: '8px' }}>
                      Agentic Synthesis In Progress
                    </h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      Our LLM nodes are active. Planner, Researcher, Analyst, and Risk models are exchanging contexts. Report will load momentarily.
                    </p>
                  </div>
                )}
                
                {/* Failed notice */}
                {currentRun.status === 'FAILED' && (
                  <div className="glass-panel" style={{ textAlign: 'center', padding: '40px 20px', borderColor: 'var(--danger)' }}>
                    <AlertTriangle 
                      size={28} 
                      color="var(--danger)" 
                      style={{ margin: '0 auto 12px auto' }} 
                    />
                    <h4 style={{ fontFamily: 'var(--font-family-title)', marginBottom: '8px', color: 'var(--danger)' }}>
                      Orchestration Halted
                    </h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      A node failed to report. See the audit logs above for details. Adjust your configuration variables and retry.
                    </p>
                  </div>
                )}
              </div>
            )
          )}
        </main>
      </div>
    </div>
  );
}
