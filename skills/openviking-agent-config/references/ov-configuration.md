# OpenViking Configuration Guide

Reference from OpenViking documentation. Core configuration sections and provider options.

## Configuration File

Default path: `~/.openviking/ov.conf` (JSON format). Set custom path via `OPENVIKING_CONFIG_FILE` env var.

## Minimal Configuration

```json
{
  "storage": {
    "workspace": "./data",
    "vectordb": {
      "name": "context",
      "backend": "local"
    },
    "agfs": {
      "port": 1833,
      "log_level": "warn",
      "backend": "local"
    }
  },
  "embedding": {
    "dense": {
      "api_base": "https://ark.cn-beijing.volces.com/api/v3",
      "api_key": "<your-api-key>",
      "provider": "volcengine",
      "dimension": 1024,
      "model": "doubao-embedding-vision-250615"
    }
  },
  "vlm": {
    "api_base": "https://ark.cn-beijing.volces.com/api/v3",
    "api_key": "<your-api-key>",
    "provider": "volcengine",
    "model": "doubao-seed-2-0-pro-260215"
  }
}
```

## Core Sections

### `embedding`
Vector embedding model for semantic search.

| Field | Description |
|---|---|
| `provider` | `"volcengine"`, `"openai"`, `"vikingdb"`, `"jina"`, `"voyage"`, `"minimax"`, `"gemini"` |
| `input` | `"text"` or `"multimodal"` (use `"multimodal"` for doubao-embedding-vision models) |
| `dimension` | Vector dimension (e.g., 1024) |
| `model` | Model name |

### `vlm`
Vision Language Model for content understanding (L0/L1 generation, memory extraction).

| Field | Description |
|---|---|
| `provider` | `"volcengine"`, `"openai"`, `"gemini"`, `"vllm"` |
| `model` | Model name |
| `max_retries` | Retry count on failure |

### `storage`
Controls data storage behavior.

| Field | Description |
|---|---|
| `workspace` | Root directory for data storage |
| `vectordb.backend` | `"local"` or remote |
| `agfs.port` | AGFS port |
| `agfs.backend` | `"local"` |
| `transaction.lock_timeout` | Lock acquisition timeout in seconds (0 = fail immediately) |
| `transaction.lock_expire` | Stale lock expiry threshold in seconds (default 300) |
