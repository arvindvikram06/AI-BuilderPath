# Claude Sonnet Responses

### 1. C# Backend (ASP.NET Core Web API)

**Models/TaskItem.cs**
```csharp
namespace TaskManagerApi.Models
{
    public class TaskItem
    {
        public int Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public bool IsCompleted { get; set; }
    }
}
```

**Controllers/TaskController.cs**
```csharp
using Microsoft.AspNetCore.Mvc;
using TaskManagerApi.Models;

namespace TaskManagerApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TasksController : ControllerBase
    {
        // In-memory store. Static so it persists across requests within the
        // process lifetime (resets on restart -- fine for a demo/mini-app).
        private static readonly List<TaskItem> _tasks = new();
        private static int _nextId = 1;
        private static readonly object _lock = new();

        // GET: api/tasks
        [HttpGet]
        public ActionResult<IEnumerable<TaskItem>> GetAll()
        {
            lock (_lock)
            {
                return Ok(_tasks.OrderBy(t => t.Id).ToList());
            }
        }

        // GET: api/tasks/5
        [HttpGet("{id}")]
        public ActionResult<TaskItem> GetById(int id)
        {
            lock (_lock)
            {
                var task = _tasks.FirstOrDefault(t => t.Id == id);
                if (task == null)
                {
                    return NotFound(new { message = $"Task with id {id} not found." });
                }
                return Ok(task);
            }
        }

        // POST: api/tasks
        [HttpPost]
        public ActionResult<TaskItem> Create([FromBody] TaskItem newTask)
        {
            if (string.IsNullOrWhiteSpace(newTask.Title))
            {
                return BadRequest(new { message = "Title is required." });
            }

            if (newTask.Title.Length > 200)
            {
                return BadRequest(new { message = "Title must be 200 characters or fewer." });
            }

            lock (_lock)
            {
                var task = new TaskItem
                {
                    Id = _nextId++,
                    Title = newTask.Title.Trim(),
                    IsCompleted = newTask.IsCompleted
                };
                _tasks.Add(task);
                return CreatedAtAction(nameof(GetById), new { id = task.Id }, task);
            }
        }

        // PUT: api/tasks/5
        [HttpPut("{id}")]
        public ActionResult<TaskItem> Update(int id, [FromBody] TaskItem updatedTask)
        {
            lock (_lock)
            {
                var task = _tasks.FirstOrDefault(t => t.Id == id);
                if (task == null)
                {
                    return NotFound(new { message = $"Task with id {id} not found." });
                }

                if (!string.IsNullOrWhiteSpace(updatedTask.Title))
                {
                    if (updatedTask.Title.Length > 200)
                    {
                        return BadRequest(new { message = "Title must be 200 characters or fewer." });
                    }
                    task.Title = updatedTask.Title.Trim();
                }

                task.IsCompleted = updatedTask.IsCompleted;
                return Ok(task);
            }
        }

        // DELETE: api/tasks/5
        [HttpDelete("{id}")]
        public IActionResult Delete(int id)
        {
            lock (_lock)
            {
                var task = _tasks.FirstOrDefault(t => t.Id == id);
                if (task == null)
                {
                    return NotFound(new { message = $"Task with id {id} not found." });
                }
                _tasks.Remove(task);
                return NoContent();
            }
        }
    }
}
```

**Program.cs**
```csharp
var builder = WebApplication.CreateBuilder(args);

// --- Services ---
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// CORS: allow the React dev server (and a configurable frontend origin)
// to call this API from the browser.
const string CorsPolicyName = "AllowFrontend";
builder.Services.AddCors(options =>
{
    options.AddPolicy(CorsPolicyName, policy =>
    {
        policy
            .WithOrigins(
                "http://localhost:3000",   // React dev server
                "http://frontend:3000"     // docker-compose service name, if proxied
            )
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

var app = builder.Build();

// --- Middleware pipeline ---
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors(CorsPolicyName);
app.UseAuthorization();
app.MapControllers();

// Bind to all interfaces inside the container so port mapping works
app.Urls.Add("http://0.0.0.0:5000");

app.Run();
```

**TaskManagerApi.csproj** (minimal, needed for the Dockerfile build below)
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.6.2" />
  </ItemGroup>
</Project>
```

---

### 2. React Frontend (TypeScript)

**App.tsx**
```tsx
import React, { useState, useEffect, FormEvent } from "react";

interface Task {
  id: number;
  title: string;
  isCompleted: boolean;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/api/tasks";

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: 480,
    margin: "60px auto",
    fontFamily: "Segoe UI, sans-serif",
    padding: "0 20px",
  },
  heading: { fontSize: 24, marginBottom: 20, color: "#1f2937" },
  form: { display: "flex", gap: 8, marginBottom: 20 },
  input: {
    flex: 1,
    padding: "10px 12px",
    fontSize: 14,
    border: "1px solid #d1d5db",
    borderRadius: 6,
    outline: "none",
  },
  addButton: {
    padding: "10px 16px",
    border: "none",
    borderRadius: 6,
    background: "#2563eb",
    color: "#fff",
    fontWeight: 600,
    cursor: "pointer",
  },
  list: { listStyle: "none", padding: 0, margin: 0 },
  item: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "10px 12px",
    background: "#f9fafb",
    border: "1px solid #e5e7eb",
    borderRadius: 6,
    marginBottom: 8,
  },
  title: { flex: 1, fontSize: 14, color: "#111827" },
  completedTitle: { textDecoration: "line-through", color: "#9ca3af" },
  deleteButton: {
    border: "none",
    background: "#fee2e2",
    color: "#dc2626",
    borderRadius: 4,
    padding: "4px 10px",
    fontSize: 12,
    cursor: "pointer",
  },
  status: { fontSize: 13, color: "#6b7280", marginBottom: 12 },
  error: { fontSize: 13, color: "#dc2626", marginBottom: 12 },
};

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTitle, setNewTitle] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(API_BASE_URL);
      if (!res.ok) throw new Error(`Failed to load tasks (status ${res.status})`);
      const data: Task[] = await res.json();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleAddTask = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = newTitle.trim();
    if (!trimmed) return;

    try {
      setError(null);
      const res = await fetch(API_BASE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: trimmed, isCompleted: false }),
      });
      if (!res.ok) throw new Error("Failed to create task.");
      const created: Task = await res.json();
      setTasks((prev) => [...prev, created]);
      setNewTitle("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task.");
    }
  };

  const handleToggleComplete = async (task: Task) => {
    const updated = { ...task, isCompleted: !task.isCompleted };
    // Optimistic update
    setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));

    try {
      const res = await fetch(`${API_BASE_URL}/${task.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updated),
      });
      if (!res.ok) throw new Error("Failed to update task.");
    } catch (err) {
      // Revert on failure
      setTasks((prev) => prev.map((t) => (t.id === task.id ? task : t)));
      setError(err instanceof Error ? err.message : "Failed to update task.");
    }
  };

  const handleDelete = async (id: number) => {
    const previous = tasks;
    setTasks((prev) => prev.filter((t) => t.id !== id));

    try {
      const res = await fetch(`${API_BASE_URL}/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete task.");
    } catch (err) {
      setTasks(previous); // revert
      setError(err instanceof Error ? err.message : "Failed to delete task.");
    }
  };

  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Task Manager</h1>

      <form style={styles.form} onSubmit={handleAddTask}>
        <input
          style={styles.input}
          type="text"
          placeholder="Add a new task..."
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
        />
        <button style={styles.addButton} type="submit">
          Add
        </button>
      </form>

      {error && <div style={styles.error}>{error}</div>}
      {loading ? (
        <div style={styles.status}>Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div style={styles.status}>No tasks yet. Add one above!</div>
      ) : (
        <ul style={styles.list}>
          {tasks.map((task) => (
            <li key={task.id} style={styles.item}>
              <input
                type="checkbox"
                checked={task.isCompleted}
                onChange={() => handleToggleComplete(task)}
              />
              <span
                style={{
                  ...styles.title,
                  ...(task.isCompleted ? styles.completedTitle : {}),
                }}
              >
                {task.title}
              </span>
              <button style={styles.deleteButton} onClick={() => handleDelete(task.id)}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default App;
```

Notes: toggle and delete use optimistic UI updates (state changes immediately, then reverts if the API call fails) for snappier perceived performance. `API_BASE_URL` is read from an env var with a sensible localhost fallback, since the actual backend host differs between local dev and Docker Compose.

---

### 3. docker-compose.yml

This assumes the backend project lives under `./backend` (containing `TaskManagerApi.csproj`, `Program.cs`, `Controllers/`, `Models/`) and the frontend lives under `./frontend` (a standard `create-react-app`-style project containing this `App.tsx`). Two small Dockerfiles are needed alongside the compose file.

**backend/Dockerfile**
```dockerfile
# --- Build stage ---
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY *.csproj ./
RUN dotnet restore

COPY . ./
RUN dotnet publish -c Release -o /app/publish

# --- Runtime stage ---
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .

EXPOSE 5000
ENV ASPNETCORE_URLS=http://0.0.0.0:5000

ENTRYPOINT ["dotnet", "TaskManagerApi.dll"]
```

**frontend/Dockerfile**
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000
ENV CHOKIDAR_USEPOLLING=true

CMD ["npm", "start"]
```

**docker-compose.yml**
```yaml
version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: taskmanager-backend
    ports:
      - "5000:5000"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
    networks:
      - taskmanager-net

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: taskmanager-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000/api/tasks
    depends_on:
      - backend
    networks:
      - taskmanager-net

networks:
  taskmanager-net:
    driver: bridge
```

Design notes: `REACT_APP_API_URL` points to `http://localhost:5000` rather than `http://backend:5000` because the API call happens in the *browser* on the host machine, not inside the frontend container — `frontend` as a hostname only resolves within the Docker network, not from your browser. `depends_on` ensures the backend container starts first, though since ASP.NET Core takes a moment to bind, you may still see a brief failed fetch on first load if you hit the page before the backend's fully up; for production you'd want a proper healthcheck-based wait instead of relying on container start order alone. CORS in `Program.cs` explicitly allowlists `http://localhost:3000` to match how the frontend will actually be accessed from the browser.

To run: `docker-compose up --build`, then visit `http://localhost:3000`.
