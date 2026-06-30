# Gemini Flash Responses

To build this functional full-stack Task Management application, we will organize the solution into three explicit, production-grade files: the ASP.NET Core Web API controller (`TaskController.cs`), the TypeScript React component (`App.tsx`), and the multi-container environment script (`docker-compose.yml`).

---

### File 1: C# ASP.NET Core Backend (`TaskController.cs`)

This clean, modern ASP.NET Core API controller uses an in-memory thread-safe storage pattern (`ConcurrentDictionary`) to support accurate concurrency without a physical database engine.

```csharp
using Microsoft.AspNetCore.Mvc;
using System.Collections.Concurrent;

namespace TaskManagerApi.Controllers
{
    // --- Models ---
    public class TodoTask
    {
        public int Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public bool IsCompleted { get; set; }
    }

    public class CreateTaskDto
    {
        public string Title { get; set; } = string.Empty;
    }

    // --- Controller ---
    [ApiController]
    [Route("api/[controller]")]
    public class TasksController : ControllerBase
    {
        // Thread-safe in-memory storage simulating database records
        private static readonly ConcurrentDictionary<int, TodoTask> _tasks = new();
        private static int _nextId = 1;

        static TasksController()
        {
            // Seed sample data for an out-of-the-box working application
            _tasks.TryAdd(_nextId, new TodoTask { Id = _nextId++, Title = "Configure ASP.NET Core backend", IsCompleted = true });
            _tasks.TryAdd(_nextId, new TodoTask { Id = _nextId++, Title = "Build React application shell", IsCompleted = false });
        }

        [HttpGet]
        public ActionResult<IEnumerable<TodoTask>> GetAll()
        {
            return Ok(_tasks.Values.OrderBy(t => t.Id));
        }

        [HttpGet("{id}")]
        public ActionResult<TodoTask> GetById(int id)
        {
            if (!_tasks.TryGetValue(id, out var task))
            {
                return NotFound(new { Message = $"Task with ID {id} was not found." });
            }
            return Ok(task);
        }

        [HttpPost]
        public ActionResult<TodoTask> Create([FromBody] CreateTaskDto dto)
        {
            if (string.IsNullOrWhiteSpace(dto.Title))
            {
                return BadRequest(new { Message = "Task title cannot be empty." });
            }

            int newId = Interlocked.Increment(ref _nextId);
            var newTask = new TodoTask
            {
                Id = newId,
                Title = dto.Title.Trim(),
                IsCompleted = false
            };

            _tasks.TryAdd(newId, newTask);
            return CreatedAtAction(nameof(GetById), new { id = newId }, newTask);
        }

        [HttpPut("{id}")]
        public IActionResult Update(int id, [FromBody] TodoTask updatedTask)
        {
            if (id != updatedTask.Id)
            {
                return BadRequest(new { Message = "Route identifier mismatch." });
            }

            if (!_tasks.ContainsKey(id))
            {
                return NotFound(new { Message = $"Task with ID {id} does not exist." });
            }

            _tasks[id] = updatedTask;
            return NoContent();
        }

        [HttpDelete("{id}")]
        public IActionResult Delete(int id)
        {
            if (!_tasks.TryRemove(id, out _))
            {
                return NotFound(new { Message = $"Task with ID {id} does not exist." });
            }
            return NoContent();
        }
    }
}

```

*Note on CORS Setup: Ensure your `Program.cs` includes policy declarations to allow client-side requests:*

```csharp
// builder.Services.AddCors(options => options.AddDefaultPolicy(p => p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));
// app.UseCors();

```

---

### File 2: React Frontend (`App.tsx`)

This React standard functional component handles CRUD interaction loops against the .NET API. It uses semantic structures and inline styles resembling tailwind utility layers.

```tsx
import React, { useState, useEffect } from 'react';

// --- Interface Types ---
interface TodoTask {
  id: number;
  title: string;
  isCompleted: boolean;
}

const API_BASE_URL = 'http://localhost:5000/api/tasks';

export const App: React.FC = () => {
  const [tasks, setTasks] = useState<TodoTask[]>([]);
  const [newTitle, setNewTitle] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // --- Read ---
  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_BASE_URL);
      if (!response.ok) throw new Error('Failed to retrieve tasks from server.');
      const data = await response.json();
      setTasks(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'An error occurred while calling the API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // --- Create ---
  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      const response = await fetch(API_BASE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle.trim() }),
      });
      
      if (!response.ok) throw new Error('Could not create the new task record.');
      const createdTask = await response.json();
      setTasks((prev) => [...prev, createdTask]);
      setNewTitle('');
    } catch (err: any) {
      alert(err.message);
    }
  };

  // --- Update (Toggle Complete) ---
  const handleToggleComplete = async (task: TodoTask) => {
    const updatedTask = { ...task, isCompleted: !task.isCompleted };
    
    try {
      const response = await fetch(`${API_BASE_URL}/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedTask),
      });

      if (!response.ok) throw new Error('Failed to update task state.');
      
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? updatedTask : t))
      );
    } catch (err: any) {
      alert(err.message);
    }
  };

  // --- Delete ---
  const handleDeleteTask = async (id: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to remove targeted task.');

      setTasks((prev) => prev.filter((task) => task.id !== id));
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div style={styles.wrapper}>
      <header style={styles.card}>
        <h1 style={styles.headerTitle}>Task Manager Application</h1>
        
        {/* Entry Form */}
        <form onSubmit={handleAddTask} style={styles.formGroup}>
          <input
            type="text"
            placeholder="Add a new milestone or chore..."
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            style={styles.textInput}
          />
          <button type="submit" style={styles.submitBtn}>Add Task</button>
        </form>

        {/* Dynamic State Feedback Rendering */}
        {error && <div style={styles.errorBanner}>{error}</div>}
        {loading ? (
          <p style={styles.placeholderText}>Loading system operational stack...</p>
        ) : tasks.length === 0 ? (
          <p style={styles.placeholderText}>Your queue is clean! No current items pending.</p>
        ) : (
          <div style={styles.listContainer}>
            {tasks.map((task) => (
              <div key={task.id} style={styles.taskItem}>
                <div style={styles.leftMeta}>
                  <input
                    type="checkbox"
                    checked={task.isCompleted}
                    onChange={() => handleToggleComplete(task)}
                    style={styles.checkboxControl}
                  />
                  <span style={{
                    ...styles.taskText,
                    textDecoration: task.isCompleted ? 'line-through' : 'none',
                    color: task.isCompleted ? '#94a3b8' : '#1e293b'
                  }}>
                    {task.title}
                  </span>
                </div>
                <button
                  onClick={() => handleDeleteTask(task.id)}
                  style={styles.deleteBtn}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </header>
    </div>
  );
};

// --- CSS-In-JS Stylesheet Object ---
const styles: { [key: string]: React.CSSProperties } = {
  wrapper: {
    minHeight: '100vh',
    backgroundColor: '#f8fafc',
    padding: '40px 16px',
    fontFamily: 'Segoe UI, system-ui, sans-serif'
  },
  card: {
    maxWidth: '540px',
    margin: '0 auto',
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
    padding: '32px'
  },
  headerTitle: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#0f172a',
    margin: '0 0 24px 0',
    textAlign: 'center'
  },
  formGroup: {
    display: 'flex',
    gap: '12px',
    marginBottom: '24px'
  },
  textInput: {
    flex: 1,
    padding: '12px 16px',
    borderRadius: '8px',
    border: '1px solid #cbd5e1',
    fontSize: '15px',
    outline: 'none'
  },
  submitBtn: {
    backgroundColor: '#4f46e5',
    color: '#ffffff',
    fontWeight: '600',
    padding: '12px 20px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer'
  },
  errorBanner: {
    backgroundColor: '#fef2f2',
    color: '#dc2626',
    padding: '12px',
    borderRadius: '6px',
    marginBottom: '16px',
    fontSize: '14px'
  },
  placeholderText: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: '15px',
    fontStyle: 'italic'
  },
  listContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  taskItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 16px',
    backgroundColor: '#f1f5f9',
    borderRadius: '8px',
    border: '1px solid #e2e8f0'
  },
  leftMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '14px',
    flex: 1
  },
  checkboxControl: {
    width: '18px',
    height: '18px',
    cursor: 'pointer'
  },
  taskText: {
    fontSize: '15px',
    fontWeight: '500',
    wordBreak: 'break-word'
  },
  deleteBtn: {
    backgroundColor: '#ef4444',
    color: '#ffffff',
    border: 'none',
    borderRadius: '6px',
    padding: '6px 12px',
    fontSize: '13px',
    cursor: 'pointer',
    fontWeight: '600'
  }
};

```

---

### File 3: Orchestration Layer (`docker-compose.yml`)

This production-grade multi-stage container build mounts multi-environment configurations, resolving proper runtime exposures and enabling multi-container service discovery via an identical network bridge.

```yaml
version: '3.8'

services:
  backend-api:
    image: mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
    container_name: task_manager_backend
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_URLS=http://+:5000
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
    working_dir: /app
    # Multi-stage inline build approach to run source directly in development profile context
    command: dotnet watch run --no-launch-profile

  frontend-ui:
    image: node:20-alpine
    container_name: task_manager_frontend
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    working_dir: /app
    # Ensures dependent node packages layer properly upon initial deployment script trigger
    command: sh -c "npm install && npm start"
    depends_on:
      - backend-api
    stdin_open: true
    tty: true

```
