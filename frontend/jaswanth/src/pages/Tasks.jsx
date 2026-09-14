import React, { useState } from 'react';
import { CheckSquare, Plus, Check, Filter } from 'lucide-react';
import { useStore } from '../context/StoreContext';
import { PriorityTasks } from '../components/dashboard/PriorityTasks';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';

export function Tasks() {
  const { tasks, toggleTask } = useStore();
  const [filter, setFilter] = useState('All');
  const [isNewTaskOpen, setIsNewTaskOpen] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState('HIGH');
  const [newTaskAssignee, setNewTaskAssignee] = useState('');

  const filteredTasks = tasks.filter(t => {
    if (filter === 'Active') return !t.completed;
    if (filter === 'Completed') return t.completed;
    return true;
  });

  const getPriorityVariant = (priority) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      default: return 'normal';
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-hero">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CheckSquare size={24} color="var(--cyan)" />
            <h1 className="greeting-title" style={{ fontSize: 22 }}>Store Manager Task Dispatch</h1>
          </div>
          <p className="greeting-subtitle">
            Operational floor assignments, staff allocations, and automated AI task tracking.
          </p>
        </div>

        <Button
          variant="primary"
          icon={Plus}
          onClick={() => setIsNewTaskOpen(true)}
        >
          Create Task
        </Button>
      </div>

      <div className="card">
        {/* Filter bar */}
        <div className="card-header-row" style={{ flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', gap: 6 }}>
            {['All', 'Active', 'Completed'].map(f => (
              <button
                key={f}
                type="button"
                onClick={() => setFilter(f)}
                style={{
                  padding: '5px 12px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: '1px solid',
                  borderColor: filter === f ? 'var(--cyan)' : 'var(--border-subtle)',
                  background: filter === f ? 'var(--cyan-dim)' : 'transparent',
                  color: filter === f ? 'var(--cyan)' : 'var(--text-muted)'
                }}
              >
                {f} ({f === 'All' ? tasks.length : (f === 'Active' ? tasks.filter(t => !t.completed).length : tasks.filter(t => t.completed).length)})
              </button>
            ))}
          </div>
        </div>

        {/* Task List */}
        <div className="task-list" style={{ marginTop: 14 }}>
          {filteredTasks.map(t => (
            <div key={t.id} className="task-row">
              <div className="task-left">
                <button
                  type="button"
                  className={`task-checkbox ${t.completed ? 'checked' : ''}`}
                  onClick={() => toggleTask(t.id)}
                  aria-label={`Toggle task ${t.task}`}
                >
                  {t.completed && <Check size={13} strokeWidth={3} />}
                </button>

                <div>
                  <div className={`task-title-text ${t.completed ? 'completed' : ''}`}>
                    {t.task}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                    {t.department} • Assigned to: <strong style={{ color: 'var(--text-secondary)' }}>{t.assignee}</strong> • Due: {t.due}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <Badge variant={getPriorityVariant(t.priority)}>
                  {t.priority}
                </Badge>

                <button
                  type="button"
                  onClick={() => toggleTask(t.id)}
                  style={{
                    background: 'transparent',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 4,
                    padding: '4px 10px',
                    color: t.completed ? 'var(--text-muted)' : 'var(--cyan)',
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  {t.completed ? 'Mark Active' : 'Mark Done'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Task Modal */}
      {isNewTaskOpen && (
        <Modal
          isOpen={isNewTaskOpen}
          onClose={() => setIsNewTaskOpen(false)}
          title="Dispatch Operational Task"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsNewTaskOpen(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  if (newTaskTitle.trim()) {
                    tasks.push({
                      id: `task-${Date.now()}`,
                      priority: newTaskPriority,
                      task: newTaskTitle,
                      department: 'Sales Floor',
                      assignee: newTaskAssignee || 'Floor Team',
                      due: 'Today 18:00',
                      completed: false,
                      systemGenerated: false
                    });
                    setIsNewTaskOpen(false);
                    setNewTaskTitle('');
                  }
                }}
              >
                Create Task
              </Button>
            </>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                Task Description:
              </label>
              <input
                type="text"
                placeholder="e.g. Clean spill in Aisle 4"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: 'var(--bg-base)',
                  border: '1px solid var(--border-medium)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-white)',
                  fontSize: '13px'
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Priority Level:
                </label>
                <select
                  value={newTaskPriority}
                  onChange={(e) => setNewTaskPriority(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    backgroundColor: 'var(--bg-base)',
                    border: '1px solid var(--border-medium)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-white)',
                    fontSize: '13px'
                  }}
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="LOW">LOW</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Assignee:
                </label>
                <input
                  type="text"
                  placeholder="Associate name"
                  value={newTaskAssignee}
                  onChange={(e) => setNewTaskAssignee(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    backgroundColor: 'var(--bg-base)',
                    border: '1px solid var(--border-medium)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-white)',
                    fontSize: '13px'
                  }}
                />
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
