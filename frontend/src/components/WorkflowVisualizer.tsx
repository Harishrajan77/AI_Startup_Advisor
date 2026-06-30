import React from 'react';
import { Compass, Search, BarChart3, ShieldAlert, Cpu, FileText, Check, Loader2 } from 'lucide-react';

interface WorkflowVisualizerProps {
  currentAgent: string;
  status: string;
}

interface Node {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
}

const NODES: Node[] = [
  { id: 'planner', label: 'Planner Agent', icon: Compass },
  { id: 'researcher', label: 'Competitor Researcher', icon: Search },
  { id: 'market_analyst', label: 'Market Analyst', icon: BarChart3 },
  { id: 'risk_assessor', label: 'Risk Assessor', icon: ShieldAlert },
  { id: 'tech_advisor', label: 'Technology Advisor', icon: Cpu },
  { id: 'report_generator', label: 'Report Generator', icon: FileText }
];

export default function WorkflowVisualizer({ currentAgent, status }: WorkflowVisualizerProps) {
  
  const getNodeStatus = (nodeId: string) => {
    if (status === 'COMPLETED' || currentAgent === 'done') {
      return 'completed';
    }
    if (status === 'FAILED') {
      return 'failed';
    }
    
    const currentIndex = NODES.findIndex(n => n.id === currentAgent);
    const nodeIndex = NODES.findIndex(n => n.id === nodeId);
    
    if (nodeIndex < currentIndex) return 'completed';
    if (nodeIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="glass-panel pipeline-visualizer">
      <div className="pipeline-header">
        <h3 className="history-title" style={{ margin: 0 }}>LangGraph Multi-Agent Pipeline</h3>
        <span className={`pipeline-status ${status === 'COMPLETED' ? 'completed' : ''}`}>
          {status === 'RUNNING' && <Loader2 className="animate-spin" size={12} />}
          {status}
        </span>
      </div>

      <div className="pipeline-nodes-container">
        {NODES.map((node, index) => {
          const Icon = node.icon;
          const nodeStatus = getNodeStatus(node.id);
          
          return (
            <React.Fragment key={node.id}>
              {/* Connector line (not before first node) */}
              {index > 0 && (
                <div 
                  className={`pipeline-connector ${
                    nodeStatus === 'completed' || nodeStatus === 'active' ? 'active' : ''
                  }`} 
                />
              )}
              
              {/* Node Card */}
              <div className={`pipeline-node ${nodeStatus}`}>
                <div className="node-icon-circle">
                  {nodeStatus === 'completed' ? (
                    <Check size={20} />
                  ) : nodeStatus === 'active' && status === 'RUNNING' ? (
                    <Loader2 className="animate-spin" size={20} />
                  ) : (
                    <Icon size={20} />
                  )}
                </div>
                <div className="node-label">{node.label}</div>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
