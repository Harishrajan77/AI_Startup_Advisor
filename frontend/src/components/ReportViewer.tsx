import { useState } from 'react';
import { LayoutDashboard, Users, Cpu, FileText, CheckCircle, TrendingUp, Download } from 'lucide-react';

interface Competitor {
  name: string;
  url: string;
  description: string;
  strengths: string;
  weaknesses: string;
}

interface MarketAnalysis {
  tam?: string;
  sam?: string;
  som?: string;
  target_audience?: string;
  monetization?: string;
  sizing_breakdown?: string;
}

interface Swot {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

interface RiskMatrixRow {
  risk_category: string;
  description: string;
  probability: string;
  impact: string;
  mitigation: string;
}

interface Risks {
  swot?: Swot;
  matrix?: RiskMatrixRow[];
}

interface TechStack {
  frontend?: string;
  backend?: string;
  database?: string;
  infrastructure_hosting?: string;
  mvp_features?: string[];
  cost_estimate?: string;
  justification?: string;
}

interface ReportViewerProps {
  report: string;
  competitors: Competitor[];
  marketAnalysis: MarketAnalysis;
  risks: Risks;
  techStack: TechStack;
}

export default function ReportViewer({
  report,
  competitors = [],
  marketAnalysis = {},
  risks = {},
  techStack = {},
}: ReportViewerProps) {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'competitors' | 'tech' | 'report'>('dashboard');

  const swot = risks.swot || { strengths: [], weaknesses: [], opportunities: [], threats: [] };
  const riskMatrix = risks.matrix || [];

  const formatCurrency = (val: any): string => {
    if (val === null || val === undefined) return '$0';
    const str = String(val).trim();
    if (str.includes('$') || /[a-zA-Z]/.test(str)) {
      return str;
    }
    const num = parseFloat(str.replace(/,/g, ''));
    if (isNaN(num)) return str;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(num);
  };

  const renderSizingBreakdown = (val: any): React.ReactNode => {
    if (val === null || val === undefined) return null;
    
    if (typeof val === 'string') {
      const trimmed = val.trim();
      if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        try {
          const parsed = JSON.parse(trimmed);
          return renderSizingBreakdown(parsed);
        } catch {
          // ignore parse error and render as string
        }
      }
      return <div style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>{val}</div>;
    }
    
    if (typeof val === 'object') {
      if (Array.isArray(val)) {
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '10px' }}>
            {val.map((item, idx) => (
              <div key={idx} className="glass-panel" style={{ background: 'rgba(255, 255, 255, 0.01)', padding: '16px', fontSize: '0.85rem', border: '1px solid rgba(255,255,255,0.05)' }}>
                {renderSizingBreakdown(item)}
              </div>
            ))}
          </div>
        );
      }
      
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {Object.entries(val).map(([k, v]) => {
            const capitalizedKey = k.charAt(0).toUpperCase() + k.slice(1).replace(/_/g, ' ');
            if (typeof v === 'object' && v !== null) {
              return (
                <div key={k} style={{ marginBottom: '10px' }}>
                  <strong style={{ color: 'var(--text-highlight)', fontSize: '0.9rem', display: 'block', marginBottom: '6px' }}>{capitalizedKey}</strong>
                  <div style={{ paddingLeft: '14px', borderLeft: '2px solid var(--primary-color)' }}>
                    {renderSizingBreakdown(v)}
                  </div>
                </div>
              );
            }
            return (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '6px', fontSize: '0.85rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>{capitalizedKey}</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>{formatCurrency(v)}</span>
              </div>
            );
          })}
        </div>
      );
    }
    
    return String(val);
  };

  const downloadMarkdown = () => {
    if (!report || report.trim() === "") {
      console.warn("Report is not ready yet.");
      return;
    }
    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `startup-validation-report.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderObjectOrString = (val: any): string => {
    if (val === null || val === undefined) return '';
    if (typeof val === 'string') return val;
    if (typeof val === 'object') {
      if (Array.isArray(val)) {
        return val.map(item => renderObjectOrString(item)).join(', ');
      }
      return Object.entries(val)
        .map(([k, v]) => {
          const capitalizedKey = k.charAt(0).toUpperCase() + k.slice(1).replace(/_/g, ' ');
          const formattedVal = typeof v === 'object' ? JSON.stringify(v) : String(v);
          return `${capitalizedKey}: ${formattedVal}`;
        })
        .join('\n');
    }
    return String(val);
  };

  // Helper to format text markdown highlights into basic HTML (e.g. bold, bullet lists)
  const formatMarkdownToHtml = (md: string) => {
    if (!md) return '';
    
    // Normalize newlines
    let html = md.replace(/\r\n/g, '\n');
    
    // Parse tables
    const lines = html.split('\n');
    let inTable = false;
    let tableRows: string[] = [];
    let processedLines: string[] = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Table detection
      if (line.startsWith('|') && line.endsWith('|')) {
        // Skip separator lines like |---|---|
        if (line.includes('---') || line.includes(':---')) {
          continue;
        }
        inTable = true;
        const cells = line.split('|').slice(1, -1).map(c => c.trim());
        tableRows.push(cells.map(c => `<td>${c}</td>`).join(''));
        continue;
      } else {
        if (inTable) {
          // Close table
          let tableHtml = '<div style="overflow-x:auto; margin: 20px 0;"><table class="report-table">';
          if (tableRows.length > 0) {
            // First row as header
            tableHtml += `<thead><tr>${tableRows[0].replace(/td>/g, 'th>')}</tr></thead>`;
            tableHtml += '<tbody>';
            for (let r = 1; r < tableRows.length; r++) {
              tableHtml += `<tr>${tableRows[r]}</tr>`;
            }
            tableHtml += '</tbody>';
          }
          tableHtml += '</table></div>';
          processedLines.push(tableHtml);
          tableRows = [];
          inTable = false;
        }
      }
      
      processedLines.push(lines[i]);
    }
    
    if (inTable) {
      let tableHtml = '<div style="overflow-x:auto; margin: 20px 0;"><table class="report-table">';
      if (tableRows.length > 0) {
        tableHtml += `<thead><tr>${tableRows[0].replace(/td>/g, 'th>')}</tr></thead>`;
        tableHtml += '<tbody>';
        for (let r = 1; r < tableRows.length; r++) {
          tableHtml += `<tr>${tableRows[r]}</tr>`;
        }
        tableHtml += '</tbody>';
      }
      tableHtml += '</table></div>';
      processedLines.push(tableHtml);
    }
    
    html = processedLines.join('\n');
    
    // Parse headers
    html = html.replace(/^# (.*)$/gm, '<h1 class="report-h1">$1</h1>');
    html = html.replace(/^## (.*)$/gm, '<h2 class="report-h2">$1</h2>');
    html = html.replace(/^### (.*)$/gm, '<h3 class="report-h3">$1</h3>');
    html = html.replace(/^#### (.*)$/gm, '<h4 class="report-h4">$1</h4>');
    
    // Parse bold & italics
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // Group consecutive bullet points into <ul> list wrappers
    const finalLines = html.split('\n');
    let inList = false;
    let listLines: string[] = [];
    
    for (let i = 0; i < finalLines.length; i++) {
      const line = finalLines[i];
      const bulletMatch = line.match(/^(\s*)([-*+])\s+(.*)$/);
      
      if (bulletMatch) {
        inList = true;
        listLines.push(`<li>${bulletMatch[3]}</li>`);
      } else {
        if (inList) {
          finalLines[i - 1] = `<ul class="report-ul">${listLines.join('')}</ul>`;
          listLines = [];
          inList = false;
        }
      }
    }
    if (inList && finalLines.length > 0) {
      finalLines[finalLines.length - 1] = `<ul class="report-ul">${listLines.join('')}</ul>`;
    }
    
    // Remove empty lines and join back with br for standard paragraphs
    return finalLines
      .filter(line => !line.match(/^(\s*)([-*+])\s+(.*)$/))
      .map(line => {
        const trimmed = line.trim();
        if (!trimmed) return '<br/>';
        if (trimmed.startsWith('<h') || trimmed.startsWith('<ul') || trimmed.startsWith('<div') || trimmed.startsWith('<table')) {
          return line;
        }
        return `<p class="report-p">${line}</p>`;
      })
      .join('\n')
      .replace(/(<br\/>\s*)+/g, '<br/>');
  };

  return (
    <div className="glass-panel report-workspace">
      {/* Tab Navigation and Download Actions */}
      <div className="workspace-tabs" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '4px' }}>
          <button
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={16} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            Dashboard Overview
          </button>
          <button
            className={`tab-btn ${activeTab === 'competitors' ? 'active' : ''}`}
            onClick={() => setActiveTab('competitors')}
          >
            <Users size={16} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            Competitors Matrix
          </button>
          <button
            className={`tab-btn ${activeTab === 'tech' ? 'active' : ''}`}
            onClick={() => setActiveTab('tech')}
          >
            <Cpu size={16} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            CTO Blueprint
          </button>
          <button
            className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('report')}
          >
            <FileText size={16} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            Full Report
          </button>
        </div>

        <div style={{ display: 'flex', gap: '8px', paddingBottom: '4px' }} className="download-actions-row">
          <button
            onClick={downloadMarkdown}
            disabled={!report || report.trim() === ""}
            className="export-btn"
            style={{
              background: (report && report.trim() !== "")
                ? 'linear-gradient(135deg, var(--primary-color) 0%, #7c3aed 100%)'
                : 'rgba(255, 255, 255, 0.05)',
              border: (report && report.trim() !== "") ? 'none' : '1px solid rgba(255, 255, 255, 0.1)',
              color: (report && report.trim() !== "") ? 'white' : 'var(--text-muted)',
              borderRadius: '8px',
              padding: '8px 16px',
              cursor: (report && report.trim() !== "") ? 'pointer' : 'not-allowed',
              fontSize: '0.85rem',
              fontWeight: '600',
              fontFamily: 'var(--font-family-title)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease',
              boxShadow: (report && report.trim() !== "") ? '0 4px 12px rgba(139, 92, 246, 0.25)' : 'none',
              opacity: (report && report.trim() !== "") ? 1 : 0.6,
            }}
            title={(report && report.trim() !== "") ? "Download full validation report as Markdown file" : "Report is generating. Please wait..."}
          >
            <Download size={15} />
            {(report && report.trim() !== "") ? "Download Report" : "Generating Report..."}
          </button>
        </div>
      </div>

      {/* Tab Contents */}
      <div className="tab-content-panel">
        {activeTab === 'dashboard' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Market Sizing Metrics */}
            <div>
              <h4 className="history-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={18} color="var(--secondary-color)" />
                Market Sizing (Bottom-Up)
              </h4>
              <div className="metrics-row">
                <div className="metric-card">
                  <div className="metric-label">TAM (Total Addressable)</div>
                  <div className="metric-value">{formatCurrency(marketAnalysis.tam)}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">SAM (Serviceable Addressable)</div>
                  <div className="metric-value">{formatCurrency(marketAnalysis.sam)}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">SOM (Serviceable Obtainable)</div>
                  <div className="metric-value">{formatCurrency(marketAnalysis.som)}</div>
                </div>
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '10px' }}>
                {renderSizingBreakdown(marketAnalysis.sizing_breakdown)}
              </div>
            </div>

            {/* SWOT Matrix Grid */}
            <div>
              <h4 className="history-title">SWOT Diagnostics</h4>
              <div className="swot-grid">
                <div className="swot-card strengths">
                  <div className="swot-card-title">Strengths (Internal)</div>
                  <ul className="swot-list">
                    {swot.strengths.length > 0 ? (
                      swot.strengths.map((s, idx) => <li key={idx}>{s}</li>)
                    ) : (
                      <li>Unique Value Proposition features</li>
                    )}
                  </ul>
                </div>
                <div className="swot-card weaknesses">
                  <div className="swot-card-title">Weaknesses (Internal)</div>
                  <ul className="swot-list">
                    {swot.weaknesses.length > 0 ? (
                      swot.weaknesses.map((w, idx) => <li key={idx}>{w}</li>)
                    ) : (
                      <li>Early execution dependency bounds</li>
                    )}
                  </ul>
                </div>
                <div className="swot-card opportunities">
                  <div className="swot-card-title">Opportunities (External)</div>
                  <ul className="swot-list">
                    {swot.opportunities.length > 0 ? (
                      swot.opportunities.map((o, idx) => <li key={idx}>{o}</li>)
                    ) : (
                      <li>Market gaps and target audience trends</li>
                    )}
                  </ul>
                </div>
                <div className="swot-card threats">
                  <div className="swot-card-title">Threats (External)</div>
                  <ul className="swot-list">
                    {swot.threats.length > 0 ? (
                      swot.threats.map((t, idx) => <li key={idx}>{t}</li>)
                    ) : (
                      <li>Competitor reaction & user acquisition costs</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>

            {/* Summary details */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div className="glass-panel" style={{ background: 'rgba(255,255,255,0.01)', borderStyle: 'dashed' }}>
                <h5 style={{ fontFamily: 'var(--font-family-title)', marginBottom: '8px', color: 'var(--text-highlight)' }}>
                  Target Demographics
                </h5>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', whiteSpace: 'pre-line' }}>
                  {renderObjectOrString(marketAnalysis.target_audience)}
                </p>
              </div>
              <div className="glass-panel" style={{ background: 'rgba(255,255,255,0.01)', borderStyle: 'dashed' }}>
                <h5 style={{ fontFamily: 'var(--font-family-title)', marginBottom: '8px', color: 'var(--text-highlight)' }}>
                  Monetization Structure
                </h5>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', whiteSpace: 'pre-line' }}>
                  {renderObjectOrString(marketAnalysis.monetization)}
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'competitors' && (
          <div>
            <h4 className="history-title" style={{ marginBottom: '16px' }}>Competitor Landscapes</h4>
            {competitors.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No competitor listings found.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {competitors.map((comp, idx) => (
                  <div key={idx} className="glass-panel" style={{ background: 'rgba(255, 255, 255, 0.01)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <h5 style={{ fontSize: '1.1rem', fontFamily: 'var(--font-family-title)', color: 'var(--text-highlight)' }}>
                        {comp.name}
                      </h5>
                      {comp.url && (
                        <a 
                          href={comp.url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          style={{ color: 'var(--secondary-color)', fontSize: '0.8rem', textDecoration: 'none' }}
                        >
                          Visit website &rarr;
                        </a>
                      )}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                      {comp.description}
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.8rem' }}>
                      <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                        <span style={{ color: 'var(--success)', fontWeight: '600', display: 'block', marginBottom: '4px' }}>Strength</span>
                        {comp.strengths}
                      </div>
                      <div style={{ background: 'rgba(239, 68, 68, 0.05)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.1)' }}>
                        <span style={{ color: 'var(--danger)', fontWeight: '600', display: 'block', marginBottom: '4px' }}>Weakness / Gap</span>
                        {comp.weaknesses}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'tech' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h4 className="history-title">CTO Engineering Blueprint</h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div>
                <h5 style={{ fontFamily: 'var(--font-family-title)', color: 'var(--text-highlight)', marginBottom: '10px' }}>
                  Technology Selection
                </h5>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem', whiteSpace: 'pre-line' }}>
                  <div><strong>Frontend:</strong> {renderObjectOrString(techStack.frontend)}</div>
                  <div><strong>Backend API:</strong> {renderObjectOrString(techStack.backend)}</div>
                  <div><strong>Database:</strong> {renderObjectOrString(techStack.database)}</div>
                  <div><strong>Infrastructure:</strong> {renderObjectOrString(techStack.infrastructure_hosting)}</div>
                </div>
              </div>
              
              <div>
                <h5 style={{ fontFamily: 'var(--font-family-title)', color: 'var(--text-highlight)', marginBottom: '10px' }}>
                  Infrastructure Budget
                </h5>
                <div style={{ background: 'rgba(139, 92, 246, 0.05)', border: '1px solid rgba(139, 92, 246, 0.1)', padding: '16px', borderRadius: '10px' }}>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--primary-color)', marginBottom: '4px' }}>
                    {techStack.cost_estimate || 'Calculated during run'}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Estimated monthly spend for first 1,000 active users</span>
                </div>
              </div>
            </div>

            <div>
              <h5 style={{ fontFamily: 'var(--font-family-title)', color: 'var(--text-highlight)', marginBottom: '10px' }}>
                Technical Justification
              </h5>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                {techStack.justification}
              </p>
            </div>

            {/* MVP Scope List */}
            <div>
              <h5 style={{ fontFamily: 'var(--font-family-title)', color: 'var(--text-highlight)', marginBottom: '10px' }}>
                Recommended MVP Scope (Must-Haves)
              </h5>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {techStack.mvp_features?.map((feat, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    <CheckCircle size={14} color="var(--success)" />
                    {feat}
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Prioritization Matrix Table */}
            {riskMatrix.length > 0 && (
              <div>
                <h5 style={{ fontFamily: 'var(--font-family-title)', color: 'var(--text-highlight)', marginBottom: '10px' }}>
                  Critical Risk Mitigations
                </h5>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                    <thead>
                      <tr>
                        <th style={{ background: 'rgba(255,255,255,0.02)', padding: '10px', textAlign: 'left', color: 'var(--text-highlight)' }}>Risk Category</th>
                        <th style={{ background: 'rgba(255,255,255,0.02)', padding: '10px', textAlign: 'left', color: 'var(--text-highlight)' }}>Description</th>
                        <th style={{ background: 'rgba(255,255,255,0.02)', padding: '10px', textAlign: 'center', color: 'var(--text-highlight)' }}>Probability</th>
                        <th style={{ background: 'rgba(255,255,255,0.02)', padding: '10px', textAlign: 'center', color: 'var(--text-highlight)' }}>Impact</th>
                        <th style={{ background: 'rgba(255,255,255,0.02)', padding: '10px', textAlign: 'left', color: 'var(--text-highlight)' }}>Mitigation Strategy</th>
                      </tr>
                    </thead>
                    <tbody>
                      {riskMatrix.map((risk, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '10px', fontWeight: 'bold' }}>{risk.risk_category}</td>
                          <td style={{ padding: '10px', color: 'var(--text-muted)' }}>{risk.description}</td>
                          <td style={{ padding: '10px', textAlign: 'center' }}>
                            <span style={{ 
                              color: risk.probability === 'High' ? 'var(--danger)' : risk.probability === 'Medium' ? 'var(--warning)' : 'var(--success)',
                              fontWeight: '600'
                            }}>{risk.probability}</span>
                          </td>
                          <td style={{ padding: '10px', textAlign: 'center' }}>
                            <span style={{ 
                              color: risk.impact === 'High' ? 'var(--danger)' : risk.impact === 'Medium' ? 'var(--warning)' : 'var(--success)',
                              fontWeight: '600'
                            }}>{risk.impact}</span>
                          </td>
                          <td style={{ padding: '10px', color: 'var(--text-muted)' }}>{risk.mitigation}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'report' && (
          <div 
            className="report-markdown"
            dangerouslySetInnerHTML={{ __html: formatMarkdownToHtml(report) }} 
          />
        )}
      </div>
    </div>
  );
}
