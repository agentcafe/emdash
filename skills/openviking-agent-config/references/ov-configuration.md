# Configuration Guide

OpenViking uses a JSON configuration file (`ov.conf`) for settings. It supports configuration for Embedding, VLM, Rerank, Storage, Parsers, and more.

## Quick Start

Create `~/.openviking/ov.conf` in your project directory:

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

### embedding

Embedding model configuration for vector search.

- `provider`: "volcengine", "openai", "vikingdb", "jina", "voyage", "minimax", or "gemini".
- `input`: "text" or "multimodal".

### vlm

Vision Language Model configuration for content understanding.

- `provider`: "volcengine", "openai", "gemini", or "vllm".

### storage

Controls data storage behavior.

- `workspace`: Root directory for data storage.
- `vectordb`: Vector database backend (local or remote).
- `agfs`: Content storage backend.
