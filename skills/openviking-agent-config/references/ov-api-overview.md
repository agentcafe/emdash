# OpenViking API Overview

Reference from OpenViking documentation. Covers connection modes, response formats, error codes, and all API endpoints.

## Connection Modes

| Mode | Use Case | Description |
|---|---|---|
| Embedded | Local development, single process | Runs locally with local data storage |
| HTTP | Connect to OpenViking Server | Connects to remote server via HTTP |
| CLI | Shell scripting, agent tool-use | Connects via CLI commands |

### HTTP Client (used by Kilo MCP server)
```python
client = ov.SyncHTTPClient(
    url="http://localhost:1933",
    api_key="your-key",
    agent_id="my-agent",     # Critical for namespace isolation
    timeout=120.0,
)
```

### Embedded Client
```python
client = ov.OpenViking(path="./data")
client.initialize()
```

## Response Format

```json
{"status": "ok", "result": {...}, "time": 0.123}
{"status": "error", "error": {"code": "NOT_FOUND", "message": "..."}, "time": 0.01}
```

## Error Codes Relevant to Agents

| Code | HTTP | Description | Agent Impact |
|---|---|---|---|
| PERMISSION_DENIED | 403 | Insufficient permissions | Cross-agent namespace access blocked |
| NOT_FOUND | 404 | Resource not found | Namespace not yet created (expected) |
| UNAUTHENTICATED | 401 | Missing/invalid API key | Server auth issue |
| SESSION_EXPIRED | 410 | Session no longer exists | Re-create session |

## API Endpoints Used by Agent MCP Tools

| MCP Tool | Endpoint | Method |
|---|---|---|
| ov_status | GET /api/v1/system/status | Health check |
| ov_ls | GET /api/v1/fs/ls | List directory |
| ov_tree | GET /api/v1/fs/tree | Directory tree |
| ov_read | POST /api/v1/content/read | Read L2 content |
| ov_abstract | POST /api/v1/content/abstract | Read L0 abstract |
| ov_overview | POST /api/v1/content/overview | Read L1 overview |
| ov_search | POST /api/v1/search/search | Semantic search (LLM intent analysis + vector rerank) |
| ov_find | POST /api/v1/search/find | Full-text search (PostgreSQL FTS, no session context) |
| ov_grep | POST /api/v1/search/grep | Pattern search |
| ov_add_resource | POST /api/v1/resources | Add resource |
| ov_add_memory | POST /api/v1/resources | Add memory (via temp_upload + add_resource) |
| ov_session_get_or_create | POST /api/v1/sessions + GET | Create/get session |
| ov_session_commit | POST /api/v1/sessions/{id}/commit | Commit session |
| ov_session_add_message | POST /api/v1/sessions/{id}/messages | Add message |

## Admin Endpoints (Multi-tenant)

OpenViking supports multi-tenant workspaces with ROOT and ADMIN roles. The agent system uses a single workspace (`agentcafe`) with per-agent API keys for namespace isolation. See Authentication Guide for key management.
