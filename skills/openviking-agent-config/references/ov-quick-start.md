# OpenViking Quick Start

Reference from OpenViking documentation. Covers installation, configuration, and first example.

## Prerequisites

- Python 3.10+
- Linux, macOS, or Windows
- Stable network connection

## Installation

### pip (local library)
```bash
pip install openviking --upgrade --force-reinstall
```

### Docker (standalone service)
```yaml
services:
  openviking:
    image: ghcr.io/volcengine/openviking:main
    container_name: openviking
    ports:
      - "1933:1933"
    volumes:
      - ~/.openviking/ov.conf:/app/ov.conf
      - ~/.openviking/data:/app/data
    restart: unless-stopped
```

Mac Docker port forwarding (socat):
```yaml
    ports:
      - "1933:1934"
    command: /bin/sh -c "apt-get update && apt-get install -y socat && socat TCP-LISTEN:1934,fork,reuseaddr TCP:127.0.0.1:1933 & openviking-server"
```

## Configuration

`~/.openviking/ov.conf`:
```json
{
  "embedding": {
    "dense": {
      "api_base": "<api-endpoint>",
      "api_key": "<your-api-key>",
      "provider": "<provider-type>",
      "dimension": 1024,
      "model": "<model-name>"
    }
  },
  "vlm": {
    "api_base": "<api-endpoint>",
    "api_key": "<your-api-key>",
    "provider": "<provider-type>",
    "model": "<model-name>"
  }
}
```

Set custom config path: `export OPENVIKING_CONFIG_FILE=/path/to/your/ov.conf`

## Models Required

| Model Type | Purpose |
|---|---|
| VLM | Image and content understanding |
| Embedding | Vectorization and semantic retrieval |

Supported providers: Volcengine (Doubao), OpenAI, custom OpenAI-compatible services.
