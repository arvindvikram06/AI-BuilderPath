# NeuraStack Technologies — API Documentation

## Overview
The NeuraStack API (v2) allows developers to programmatically access NeuraSearch, NeuraChat, and NeuraPipeline.

- **Base URL:** `https://api.neurastack.io/v2`
- **Protocol:** HTTPS only (HTTP requests are redirected)
- **Format:** All requests and responses use JSON unless noted otherwise
- **Authentication:** Bearer token (API key) in the Authorization header

```
Authorization: Bearer YOUR_API_KEY
```

---

## Authentication

### Generating an API Key
1. Log in at https://app.neurastack.io
2. Go to **Settings → API Keys → Create New Key**
3. Give it a name (e.g., "production-app") and select the permission scope
4. Copy and store the key securely — it will only be shown once

Each account supports up to **5 active API keys** simultaneously. Keys do not expire unless manually revoked.

### API Key Scopes
| Scope | Access |
|---|---|
| `read` | GET requests only |
| `read_write` | GET, POST, PUT requests |
| `admin` | Full access including DELETE and key management |

---

## HTTP Status Codes & Error Codes

| Code | Status | Meaning | Recommended Action |
|---|---|---|---|
| 200 | OK | Request succeeded | — |
| 201 | Created | Resource created successfully | Use `id` from response |
| 204 | No Content | Deleted successfully | — |
| 400 | Bad Request | Invalid request body or parameters | Check request schema |
| 401 | Unauthorized | Missing or invalid API key | Regenerate API key |
| 403 | Forbidden | API key lacks required permissions | Upgrade plan or key scope |
| 404 | Not Found | Resource does not exist | Verify the resource ID |
| 409 | Conflict | Duplicate resource | Check existing records |
| 422 | Unprocessable Entity | Validation error on input | Fix field-level errors in response |
| 429 | Too Many Requests | Rate limit exceeded | Wait for `Retry-After` seconds |
| 500 | Internal Server Error | NeuraStack server error | Retry after 5s; contact support if persistent |
| 503 | Service Unavailable | Planned maintenance | Check https://status.neurastack.io |

### Error Response Format
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded. You have sent 100 requests this minute.",
    "retry_after": 30
  }
}
```

---

## Rate Limits

| Plan | Requests / Minute | Requests / Day |
|---|---|---|
| Free | 10 | 100 |
| Pro | 100 | 10,000 |
| Enterprise | 1,000 | Unlimited |

When you receive a **429 Too Many Requests**, the response header includes:
```
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1719830400
```

Enterprise accounts receive a **burst capacity** of 2× the standard rate limit for up to 60 seconds before throttling applies.

---

## NeuraChat API

### POST /chat
Send a user query to the RAG chatbot and receive a contextual answer.

**Request Body:**
```json
{
  "query": "What is the vacation leave policy?",
  "session_id": "sess-abc-123",
  "top_k": 5,
  "stream": false
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ | The user's question |
| `session_id` | string | ❌ | Maintain conversation history across turns |
| `top_k` | integer | ❌ | Number of chunks to retrieve (default: 5) |
| `stream` | boolean | ❌ | Stream response tokens (default: false) |

**Response:**
```json
{
  "answer": "Full-time employees at NeuraStack receive 20 paid vacation days per year...",
  "sources": [
    {
      "text": "Full-time employees receive 20 paid vacation days per year...",
      "source": "employee_handbook.md",
      "score": 0.94
    },
    {
      "text": "Vacation requests must be submitted at least 5 business days in advance...",
      "source": "employee_handbook.md",
      "score": 0.87
    }
  ],
  "session_id": "sess-abc-123",
  "tokens_used": 312,
  "model": "llama-3.3-70b-versatile"
}
```

---

### POST /ingest
Upload a document to the knowledge base for indexing.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | ✅ | Document to ingest (.pdf, .docx, .txt, .md) |
| `scope` | string | ❌ | `base` (permanent) or `session` (temporary, default) |

**Response:**
```json
{
  "status": "success",
  "filename": "onboarding_guide.pdf",
  "chunks_indexed": 47,
  "scope": "session"
}
```

Max file size: 50 MB (Pro), 200 MB (Enterprise).

---

### DELETE /knowledge-base/{doc_id}
Remove a document from the permanent knowledge base.

**Response:** `204 No Content`

---

## NeuraSearch API

### GET /search
Perform a semantic search across the knowledge base.

**Query Parameters:**
| Param | Type | Required | Description |
|---|---|---|---|
| `q` | string | ✅ | Natural language search query |
| `top_k` | integer | ❌ | Number of results (default: 5, max: 20) |
| `filter` | string | ❌ | Limit to a specific source file |

**Example Request:**
```
GET /search?q=password+rotation+policy&top_k=3&filter=security_policy.md
```

**Response:**
```json
{
  "query": "password rotation policy",
  "results": [
    {
      "text": "Passwords for all internal systems must be rotated every 90 days...",
      "source": "security_policy.md",
      "score": 0.96
    }
  ],
  "total": 1
}
```

---

## NeuraPipeline API

### GET /pipelines
List all pipelines for the authenticated account.

### POST /pipelines/{id}/run
Trigger a pipeline run manually.

**Response:**
```json
{ "run_id": "run-xyz-789", "status": "queued", "started_at": "2025-06-24T01:00:00Z" }
```

### GET /pipelines/{id}/runs/{run_id}
Get the status and logs of a specific run.

**Run Status Values:** `queued` | `running` | `success` | `failed` | `cancelled`

---

## API Versioning

- Current stable version: **v2** (released January 2025)
- Previous version: **v1** — deprecated, sunset date: **December 31, 2025**
- Breaking changes are announced via email **90 days in advance**
- Version is specified in the URL path: `/api/v1/` or `/api/v2/`
- Non-breaking additions (new fields, new endpoints) are released without version bumps

---

## SDKs & Resources

| Resource | Link |
|---|---|
| Python SDK | `pip install neurastack-sdk` |
| TypeScript SDK | `npm install @neurastack/sdk` |
| Postman Collection | https://docs.neurastack.io/postman |
| Interactive API Docs | https://docs.neurastack.io/api |
| Status Page | https://status.neurastack.io |
| Changelog | https://docs.neurastack.io/changelog |