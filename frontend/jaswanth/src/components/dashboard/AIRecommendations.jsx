import React from 'react';
import { Sparkles, Brain, ArrowUpRight, CheckCircle2, TrendingUp } from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';

export function AIRecommendations() {
  const { recommendations, executeRecommendation, isLoading } = useStore();

  return (
    <div className="card ai-section">
      <div className="card-header-row" style={{ flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="ai-header-badge">
              <Brain size={13} />
              <span>Neural Store Engine</span>
            </div>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Confidence Avg: 92%
            </span>
          </div>
          <div className="card-title" style={{ marginTop: 6, fontSize: 18 }}>
            <span>AI Recommendations</span>
          </div>
          <div className="card-subtitle">
            Actions prioritized by predicted store conditions and revenue impact.
          </div>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <EmptyState
          icon={CheckCircle2}
          title="No AI recommendations at this time"
          subtitle="Autonomous models detect no high-priority bottlenecks."
        />
      ) : (
        <div className="recommendations-grid">
          {recommendations.map(rec => (
            <div key={rec.id} className="recommendation-card">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="rec-badge-tag">{rec.badge || rec.category}</span>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 700,
                      color: 'var(--cyan)',
                      background: 'rgba(6,182,212,0.1)',
                      padding: '2px 6px',
                      borderRadius: 4
                    }}
                  >
                    {rec.confidence}% AI Confidence
                  </span>
                </div>

                <div className="rec-title">{rec.title}</div>
                <div className="rec-reason">{rec.reason}</div>
              </div>

              <div>
                {rec.estimatedImpact && (
                  <div className="rec-meta-box" style={{ marginBottom: 12 }}>
                    <TrendingUp size={13} />
                    <span>{rec.estimatedImpact}</span>
                  </div>
                )}

                <Button
                  variant="primary"
                  icon={ArrowUpRight}
                  onClick={() => executeRecommendation(rec)}
                  disabled={isLoading}
                  style={{ width: '100%' }}
                >
                  {rec.buttonText}
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
