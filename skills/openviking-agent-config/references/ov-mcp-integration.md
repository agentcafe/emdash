# OpenViking MCP Integration Guide

Reference from OpenViking documentation (`docs/en/guides/06-mcp-integration.md`). Covers how OpenViking connects as an MCP server — the transport mode our agent system uses.

## Transport Modes

| Mode | How it works | Multi-session safe | Recommended for |
|---|---|---|---|
| HTTP (SSE) | Single long-running server; clients connect via HTTP | Yes | Production, multi-agent, multi-session |
| stdio | Host spawns a new process per session | No (lock contention) | Single-session local dev only |

**Our system uses HTTP SSE mode** — `openviking-server` runs as a daemon on port 1933, and the MCP server connects via HTTP.

## Available MCP Tools

| Tool | Description |
|---|---|
| `ov_search` | Semantic search across memories and resources |
| `ov_find` | FTS/vector search (simple) |
| `ov_add_memory` | Store a new memory |
| `ov_add_resource` | Add a resource (file, text, URL) |
| `ov_status` | Check system health and component status |
| `ov_ls` / `ov_tree` | Browse stored memories and resources |
| `ov_session_get_or_create` | Create or resume a session |
| `ov_session_commit` | Commit session (archive + memory extraction) |
| `ov_session_add_message` | Add a message to the session |

## Troubleshooting

- **`Transport closed`**: Switch to HTTP mode to avoid contention. The MCP server may have crashed.
- **Connection refused**: Verify `openviking-server` is running: `curl http://localhost:1933/health`
- **Auth errors**: Ensure API key matches between MCP server config and OV server config.
