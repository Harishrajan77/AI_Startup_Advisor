import { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

interface AgentLogsProps {
  logs: string[];
}

export default function AgentLogs({ logs }: AgentLogsProps) {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Autoscroll terminal as logs grow
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  // Helper to format log text with highlighted agents/prefixes
  const parseLog = (log: string) => {
    const timeMatch = log.match(/^\[.*?\]/);
    let rest = log;
    let timeStr = "";
    
    if (timeMatch) {
      timeStr = timeMatch[0];
      rest = log.substring(timeStr.length).trim();
    }
    
    const splitIndex = rest.indexOf(':');
    if (splitIndex !== -1) {
      const agent = rest.substring(0, splitIndex);
      const message = rest.substring(splitIndex + 1);
      return { timeStr, agent, message };
    }
    
    return { timeStr, agent: "", message: rest };
  };

  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      <div className="terminal-title">
        <Terminal size={14} />
        Live Agent Audit Trail
      </div>
      
      <div ref={terminalRef} className="terminal-panel">
        {logs.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
            Awaiting instructions... Terminal idle.
          </div>
        ) : (
          logs.map((log, index) => {
            const { agent, message } = parseLog(log);
            return (
              <div key={index} className="terminal-log-row">
                <span className="time">&gt;</span>
                {agent && <span className="agent">{agent}:</span>}
                <span style={{ color: log.includes("CRITICAL ERROR") ? 'var(--danger)' : 'var(--text-primary)' }}>
                  {message}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
