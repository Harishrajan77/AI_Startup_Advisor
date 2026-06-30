import { CheckCircle, AlertCircle, Loader2, Calendar } from 'lucide-react';

interface HistoryItem {
  id: string;
  idea: string;
  status: string;
  created_at: string;
}

interface HistoryPanelProps {
  history: HistoryItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export default function HistoryPanel({ history, selectedId, onSelect }: HistoryPanelProps) {
  const formatDate = (isoStr: string) => {
    if (!isoStr) return '';
    const date = new Date(isoStr);
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle size={14} color="var(--success)" />;
      case 'FAILED':
        return <AlertCircle size={14} color="var(--danger)" />;
      case 'RUNNING':
        return <Loader2 size={14} className="animate-spin" color="var(--primary-color)" />;
      default:
        return <Loader2 size={14} color="var(--text-muted)" />;
    }
  };

  return (
    <div className="glass-panel history-panel">
      <h3 className="history-title">Validation History</h3>
      
      <div className="history-list">
        {history.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '20px 0' }}>
            No previous runs found.
          </div>
        ) : (
          history.map((item) => (
            <div
              key={item.id}
              className={`history-item ${selectedId === item.id ? 'active' : ''}`}
              onClick={() => onSelect(item.id)}
            >
              <div className="history-item-idea" title={item.idea}>
                {item.idea}
              </div>
              <div className="history-item-meta">
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Calendar size={11} />
                  {formatDate(item.created_at)}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {getStatusIcon(item.status)}
                  <span style={{ fontSize: '0.7rem', textTransform: 'capitalize' }}>
                    {item.status.toLowerCase()}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
