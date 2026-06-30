# ChatGPT Responses

Below is a complete minimal full-stack Task Manager consisting of three files.

---

### 1. Program.cs (ASP.NET Core Backend)

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.UseCors("AllowFrontend");

List<TaskItem> tasks =
[
    new TaskItem { Id = 1, Title = "Learn ASP.NET Core", IsCompleted = false },
    new TaskItem { Id = 2, Title = "Build React App", IsCompleted = true }
];

app.MapGet("/tasks", () =>
{
    return Results.Ok(tasks);
});

app.MapPost("/tasks", ([FromBody] TaskItem task) =>
{
    task.Id = tasks.Count == 0 ? 1 : tasks.Max(t => t.Id) + 1;
    tasks.Add(task);
    return Results.Created($"/tasks/{task.Id}", task);
});

app.MapPut("/tasks/{id:int}", (int id, [FromBody] TaskItem updatedTask) =>
{
    var task = tasks.FirstOrDefault(t => t.Id == id);

    if (task == null)
        return Results.NotFound();

    task.Title = updatedTask.Title;
    task.IsCompleted = updatedTask.IsCompleted;

    return Results.Ok(task);
});

app.MapDelete("/tasks/{id:int}", (int id) =>
{
    var task = tasks.FirstOrDefault(t => t.Id == id);

    if (task == null)
        return Results.NotFound();

    tasks.Remove(task);

    return Results.NoContent();
});

app.Run();

public class TaskItem
{
    public int Id { get; set; }

    public string Title { get; set; } = "";

    public bool IsCompleted { get; set; }
}
```

---

### 2. App.tsx (React + TypeScript)

```tsx
import { useEffect, useState } from "react";

interface Task {
  id: number;
  title: string;
  isCompleted: boolean;
}

const API = "http://localhost:5000/tasks";

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState("");

  const loadTasks = async () => {
    const res = await fetch(API);
    const data = await res.json();
    setTasks(data);
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const addTask = async () => {
    if (!title.trim()) return;

    await fetch(API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title,
        isCompleted: false,
      }),
    });

    setTitle("");
    loadTasks();
  };

  const toggleTask = async (task: Task) => {
    await fetch(`${API}/${task.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...task,
        isCompleted: !task.isCompleted,
      }),
    });

    loadTasks();
  };

  const deleteTask = async (id: number) => {
    await fetch(`${API}/${id}`, {
      method: "DELETE",
    });

    loadTasks();
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "40px auto",
        fontFamily: "Arial",
      }}
    >
      <h1>Task Manager</h1>

      <div style={{ display: "flex", gap: 10 }}>
        <input
          style={{
            flex: 1,
            padding: 10,
          }}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task..."
        />

        <button
          onClick={addTask}
          style={{
            padding: "10px 20px",
            cursor: "pointer",
          }}
        >
          Add
        </button>
      </div>

      <ul
        style={{
          listStyle: "none",
          padding: 0,
          marginTop: 20,
        }}
      >
        {tasks.map((task) => (
          <li
            key={task.id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 10,
              padding: 10,
              border: "1px solid #ddd",
              borderRadius: 6,
            }}
          >
            <span
              onClick={() => toggleTask(task)}
              style={{
                cursor: "pointer",
                textDecoration: task.isCompleted
                  ? "line-through"
                  : "none",
              }}
            >
              {task.title}
            </span>

            <button
              style={{
                background: "red",
                color: "white",
                border: "none",
                padding: "6px 10px",
                cursor: "pointer",
              }}
              onClick={() => deleteTask(task.id)}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

### 3. docker-compose.yml

```yaml
version: "3.9"

services:

  backend:
    image: mcr.microsoft.com/dotnet/sdk:8.0
    container_name: task-backend
    working_dir: /app

    volumes:
      - ./backend:/app

    command: >
      sh -c "
      dotnet restore &&
      dotnet run --urls=http://0.0.0.0:5000
      "

    ports:
      - "5000:5000"

  frontend:
    image: node:20
    container_name: task-frontend
    working_dir: /app

    volumes:
      - ./frontend:/app

    command: >
      sh -c "
      npm install &&
      npm start
      "

    ports:
      - "3000:3000"

    environment:
      CHOKIDAR_USEPOLLING: "true"

    depends_on:
      - backend
```

#### Suggested project structure

```text
TaskManager/
│
├── docker-compose.yml
│
├── backend/
│   ├── Program.cs
│   ├── TaskManager.csproj
│   └── ...
│
└── frontend/
    ├── src/
    │   └── App.tsx
    ├── package.json
    └── ...
```
