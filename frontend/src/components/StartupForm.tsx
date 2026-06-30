import React, { useState } from 'react';
import { Sparkles, Play } from 'lucide-react';

interface StartupFormProps {
  onSubmit: (idea: string) => void;
  isLoading: boolean;
}

export default function StartupForm({ onSubmit, isLoading }: StartupFormProps) {
  const [idea, setIdea] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (idea.trim()) {
      onSubmit(idea);
    }
  };

  const loadExample = () => {
    setIdea("I want to build an AI-powered fitness platform for college students.");
  };

  return (
    <div className="glass-panel">
      <form onSubmit={handleSubmit} className="startup-form">
        <label className="form-label" htmlFor="startup-idea-input">
          Validate Your Startup Idea
        </label>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '8px' }}>
          Describe your product, target audience, and business model in a few sentences. Our multi-agent AI system will evaluate competitors, estimate TAM/SAM/SOM, assess feasibility, and recommend a tech stack.
        </p>
        
        <textarea
          id="startup-idea-input"
          className="form-textarea"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Enter your startup concept here... (e.g., 'A subscription platform for renting premium tools locally...')"
          disabled={isLoading}
        />
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            type="submit"
            className="form-submit-btn"
            disabled={isLoading || !idea.trim()}
          >
            {isLoading ? (
              <>
                <Sparkles className="animate-spin" size={16} />
                Analyzing...
              </>
            ) : (
              <>
                <Play size={16} />
                Analyze Idea
              </>
            )}
          </button>
          
          {!isLoading && (
            <button
              type="button"
              onClick={loadExample}
              style={{
                background: 'transparent',
                border: '1px dashed rgba(255, 255, 255, 0.15)',
                color: 'var(--text-muted)',
                borderRadius: '10px',
                padding: '12px 18px',
                cursor: 'pointer',
                fontFamily: 'var(--font-family-title)',
                fontSize: '0.9rem',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--primary-color)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                e.currentTarget.style.color = 'var(--text-muted)';
              }}
            >
              Try Example
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
