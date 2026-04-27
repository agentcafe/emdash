# OpenViking Server Mode

Reference from OpenViking documentation. Covers HTTP server startup, client connections, and cloud deployment.

## Server Startup

```bash
# Default config path
openviking-server

# Custom config
openviking-server --config /path/to/ov.conf --port 8000
```

Verify: `curl http://localhost:1933/health` → `{"status": "ok"}`

## Client Connections

### Python SDK (HTTP)
```python
import openviking as ov
client = ov.SyncHTTPClient(url="http://localhost:1933", api_key="your-key", agent_id="my-agent")
```

The `agent_id` parameter is critical for namespace isolation — it determines which `viking://agent/{name}/` namespace the client operates in.

### CLI
`~/.openviking/ovcli.conf`:
```json
{
  "url": "http://localhost:1933",
  "api_key": "your-key"
}
```

```bash
openviking observer system              # Health check
openviking add-resource <url or path>   # Add to memory
openviking ls viking://resources        # List resources
openviking find "query"                # Search
```

### curl
```bash
curl -X POST http://localhost:1933/api/v1/resources \
  -H "Content-Type: application/json" \
  -d '{"path": "https://..."}'

curl -X POST http://localhost:1933/api/v1/search/find \
  -H "Content-Type: application/json" \
  -d '{"query": "what is openviking"}'
```

## Cloud Deployment (Volcengine ECS)

Recommended: veLinux 2.0, compute-optimized c3a (2 vCPU, 4GiB+), 256 GB data disk.

```bash
# Install uv and OpenViking
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install openviking --upgrade

# Configure ~/.openviking/ov.conf with embedding + VLM models
# Start as daemon
nohup openviking-server > /data/log/openviking.log 2>&1 &
```
