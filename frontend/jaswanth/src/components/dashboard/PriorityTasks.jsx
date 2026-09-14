import React from 'react';
import { CheckSquare, Check, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useStore } from '../../context/StoreContext';
import { Badge } from '../common/Badge';

export function PriorityTasks({ limit = 4, showViewAll = true }) {
  const { tasks, toggleTask, executeRecommendation, recommendations } = useStore();

  const getPriorityVariant = (priority) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      default: return 'normal';
    }
  };

  const handleTaskQuickAction = (task) => {
    if (task.completed) {
      toggleTask(task.id);
      return;
    }

    // Attempt to execute associated AI action if applicable
    if (task.task.toLowerCase().includes('milk')) {
      const rec = recommendations.find(r => r.actionType === 'replenish_milk');
      if (rec) executeRecommendation(rec);
    } else if (task.task.toLowerCase().includes('checkout')) {
      const rec = recommendations.find(r => r.actionType === 'open_checkout');
      if (rec) executeRecommendation(rec);
    } else if (task.task.toLowerCase().includes('bread')) {
      const rec = recommendations.find(r => r.actionType === 'verify_bread');
      if (rec) executeRecommendation(rec);
    }

    toggleTask(task.id);
  };

  const displayedTasks = limit ? tasks.slice(0, limit) : tasks;

  return (
    <div className="card">
      <div className="card-header-row">
        <div>
          <div className="card-title">
            <CheckSquare size={18} color="var(--cyan)" />
            <span>Priority Tasks</span>
          </div>
          <div className="card-subtitle">Operational checklist for current shift</div>
        </div>

        {showViewAll && (
          <Link
            to="/tasks"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              fontSize: 12,
              fontWeight: 600,
              color: 'var(--cyan)',
              textDecoration: 'none'
            }}
          >
            <span>All Tasks</span>
            <ArrowRight size={14} />
          </Link>
        )}
      </div>

      <div className="task-list" style={{ marginTop: 12 }}>
        {displayedTasks.map(t => (
          <div key={t.id} className="task-row">
            <div className="task-left">
              <button
                type="button"
                className={`task-checkbox ${t.completed ? 'checked' : ''}`}
                onClick={() => handleTaskQuickAction(t)}
                aria-label={`Toggle task: ${t.task}`}
              >
                {t.completed && <Check size={13} strokeWidth={3} />}
              </button>

              <div>
                <div className={`task-title-text ${t.completed ? 'completed' : ''}`}>
                  {t.task}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {t.assignee} • Due {t.due}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Badge variant={getPriorityVariant(t.priority)}>
                {t.priority}
              </Badge>

              <button
                type="button"
                onClick={() => handleTaskQuickAction(t)}
                style={{
                  background: 'transparent',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 4,
                  padding: '4px 8px',
                  color: t.completed ? 'var(--text-muted)' : 'var(--text-primary)',
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {t.completed ? 'Undo' : 'Complete'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
