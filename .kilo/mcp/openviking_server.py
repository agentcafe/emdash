#!/usr/bin/env python3
"""
OpenViking MCP Server — stdio bridge for Kilo Code.

Exposes OpenViking REST API tools via the MCP protocol so agents can
search, read, and write context across sessions.

OpenViking server must be running (default: http://localhost:1933).
"""

import os
import json
import urllib.request
import urllib.error

from mcp.server.fastmcp import FastMCP

# ── Configuration ───────────────────────────────────────────────────────────
OV_API_BASE = os.environ.get("OPENVIKING_API_URL", "http://localhost:1933")
OV_API_KEY = os.environ.get("OPENVIKING_API_KEY", "")
OV_AGENT_ID = os.environ.get("OPENVIKING_AGENT_ID", "default")
TIMEOUT = int(os.environ.get("OPENVIKING_TIMEOUT", "30"))

mcp = FastMCP("openviking", json_response=True)


# ── Helpers ─────────────────────────────────────────────────────────────────
def _ov_request(
	method: str,
	path: str,
	body: dict | None = None,
	agent_id: str | None = None,
) -> dict:
	"""Make an authenticated HTTP request to the OpenViking REST API."""
	url = f"{OV_API_BASE.rstrip('/')}{path}"
	data = None
	headers = {
		"X-API-Key": OV_API_KEY,
		"Accept": "application/json",
	}
	# Per-request agent override takes precedence over the env default
	effective_agent = agent_id if agent_id else OV_AGENT_ID
	if effective_agent and effective_agent != "default":
		headers["X-OpenViking-Agent"] = effective_agent

	if body is not None:
		data = json.dumps(body).encode("utf-8")
		headers["Content-Type"] = "application/json"

	req = urllib.request.Request(url, data=data, headers=headers, method=method)
	try:
		with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
			return json.loads(resp.read().decode("utf-8"))
	except urllib.error.HTTPError as e:
		error_body = e.read().decode("utf-8", errors="replace")
		try:
			err = json.loads(error_body)
			msg = err.get("error", {}).get("message", error_body)
		except json.JSONDecodeError:
			msg = error_body
		raise RuntimeError(f"OpenViking API error {e.code}: {msg}")
	except urllib.error.URLError as e:
		raise RuntimeError(f"OpenViking connection failed: {e.reason}")


def _format_result(data: dict | list) -> str:
	"""Format API result as readable JSON."""
	if isinstance(data, dict):
		# Strip noisy fields for readable output
		clean = {k: v for k, v in data.items() if k not in ("telemetry",)}
		return json.dumps(clean, indent=2, ensure_ascii=False, default=str)
	return json.dumps(data, indent=2, ensure_ascii=False, default=str)


# ── Tools ───────────────────────────────────────────────────────────────────
@mcp.tool()
def ov_status(agent_id: str = "") -> str:
	"""Check OpenViking server health and component status.

	Args:
	    agent_id: Optional agent identity for namespaced access
	"""
	result = _ov_request("GET", "/api/v1/system/status", agent_id=agent_id)
	return _format_result(result)


@mcp.tool()
def ov_ls(uri: str = "viking://", agent_id: str = "") -> str:
	"""List directory contents. Defaults to viking:// (root).

	Args:
	    uri: Viking URI path to list, e.g. 'viking://resources' or 'viking://'
	    agent_id: Optional agent identity for namespaced access
	"""
	result = _ov_request(
		"GET",
		f"/api/v1/fs/ls?uri={urllib.request.quote(uri, safe='/:')}",
		agent_id=agent_id,
	)
	return _format_result(result)


@mcp.tool()
def ov_tree(uri: str = "viking://", depth: int = 2, agent_id: str = "") -> str:
	"""Get directory tree with hierarchical structure.

	Args:
	    uri: Viking URI path to show tree for
	    depth: Maximum depth to traverse (1-5)
	    agent_id: Optional agent identity for namespaced access
	"""
	d = max(1, min(5, depth))
	result = _ov_request(
		"GET",
		f"/api/v1/fs/tree?uri={urllib.request.quote(uri, safe='/:')}&depth={d}",
		agent_id=agent_id,
	)
	return _format_result(result)


@mcp.tool()
def ov_search(query: str, limit: int = 5, agent_id: str = "") -> str:
	"""Semantic search across all OpenViking memories and resources.
	Returns ranked results with abstracts and scores.

	Args:
	    query: Search query string
	    limit: Maximum number of results (1-20)
	    agent_id: Optional agent identity for namespaced access
	"""
	body = {
		"query": query,
		"limit": max(1, min(20, limit)),
	}
	result = _ov_request("POST", "/api/v1/search/search", body, agent_id=agent_id)
	return _format_result(result)


@mcp.tool()
def ov_find(query: str, limit: int = 10, agent_id: str = "") -> str:
	"""Find content by exact or full-text match (PostgreSQL FTS).
	Faster than semantic search for exact terms.

	Args:
	    query: Search terms
	    limit: Maximum number of results (1-50)
	    agent_id: Optional agent identity for namespaced access
	"""
	body = {
		"query": query,
		"limit": max(1, min(50, limit)),
	}
	result = _ov_request("POST", "/api/v1/search/find", body, agent_id=agent_id)
	return _format_result(result)


@mcp.tool()
def ov_grep(pattern: str, uri: str | None = None, agent_id: str = "") -> str:
	"""Regex pattern search through file contents.

	Args:
	    pattern: Regular expression pattern to search for
	    uri: Optional Viking URI directory to scope search to
	    agent_id: Optional agent identity for namespaced access
	"""
	params = [("query", pattern)]
	if uri:
		params.append(("uri", uri))
	qs = "&".join(f"{k}={urllib.request.quote(v)}" for k, v in params)
	result = _ov_request("GET", f"/api/v1/search/grep?{qs}", agent_id=agent_id)
	return _format_result(result)


@mcp.tool()
def ov_abstract(uri: str, agent_id: str = "") -> str:
	"""Read the L0 abstract (1-2 sentence summary) of a resource.

	Args:
	    uri: Full Viking URI of the resource
	    agent_id: Optional agent identity for namespaced access
	"""
	result = _ov_request(
		"GET",
		f"/api/v1/content/abstract?uri={urllib.request.quote(uri, safe='/:')}",
		agent_id=agent_id,
	)
	return _format_result(result)


@mcp.tool()
def ov_overview(uri: str, agent_id: str = "") -> str:
	"""Read the L1 overview (~2K token structural summary) of a resource.

	Args:
	    uri: Full Viking URI of the resource
	    agent_id: Optional agent identity for namespaced access
	"""
	result = _ov_request(
		"GET",
		f"/api/v1/content/overview?uri={urllib.request.quote(uri, safe='/:')}",
		agent_id=agent_id,
	)
	return _format_result(result)


@mcp.tool()
def ov_read(uri: str, agent_id: str = "") -> str:
	"""Read full L2 content of a resource.

	Args:
	    uri: Full Viking URI of the resource
	    agent_id: Optional agent identity for namespaced access
	"""
	result = _ov_request(
		"GET",
		f"/api/v1/content/read?uri={urllib.request.quote(uri, safe='/:')}",
		agent_id=agent_id,
	)
	return _format_result(result)


@mcp.tool()
def ov_add_resource(
	path: str, to: str = "viking://resources", agent_id: str = ""
) -> str:
	"""Add a resource to OpenViking for indexing.
	Accepts file paths, URLs, or text snippets.
	The resource will be asynchronously processed: chunked, embedded, and summarized.

	Args:
	    path: File path, URL, or text content to index
	    to: Target Viking URI directory (default: viking://resources)
	    agent_id: Optional agent identity for namespaced access
	"""
	result = _ov_request(
		"POST",
		"/api/v1/resources",
		{"path": path, "to": to},
		agent_id=agent_id,
	)
	return _format_result(result)


@mcp.tool()
def ov_add_memory(
	content: str, uri: str | None = None, agent_id: str = ""
) -> str:
	"""Store a persistent memory in the user's memory space.
	Use for session handoffs, decisions, preferences, and lessons learned.

	Uses the temp_upload + add_resource flow (content/write only updates existing files).

	Args:
	    content: Memory content (markdown or plain text)
	    uri: Optional Viking URI path for the memory.
	         Defaults to auto-generated under viking://resources/
	    agent_id: Optional agent identity for namespaced access
	"""
	import uuid

	# Default to resources tree if no URI given
	if not uri:
		timestamp = __import__("time").strftime("%Y-%m-%d-%H%M%S")
		short_id = str(uuid.uuid4())[:8]
		uri = f"viking://resources/work/emdash/kilo/architecture/decisions/memory-{timestamp}-{short_id}.md"

	# Ensure parent directory exists
	parts = uri.split("/")
	parent_uri = "/".join(parts[:-1])
	dir_check = _ov_request("GET", f"/api/v1/fs/ls?uri={parent_uri}", agent_id=agent_id)
	if isinstance(dir_check, dict) and dir_check.get("status") == "error":
		# Directory doesn't exist — memory goes to the default decisions directory
		timestamp = __import__("time").strftime("%Y-%m-%d-%H%M%S")
		short_id = str(uuid.uuid4())[:8]
		uri = f"viking://resources/work/emdash/kilo/architecture/decisions/memory-{timestamp}-{short_id}.md"

	# Step 1: Upload content as temp file
	boundary = "----OvMem"
	filename = f"memory-{__import__('time').strftime('%Y%m%d-%H%M%S')}.md"
	import urllib.request as _urlreq

	body_bytes = b""
	body_bytes += f"--{boundary}\r\n".encode()
	body_bytes += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
	body_bytes += b"Content-Type: application/octet-stream\r\n\r\n"
	body_bytes += content.encode("utf-8")
	body_bytes += f"\r\n--{boundary}--\r\n".encode()

	temp_url = f"{OV_API_BASE.rstrip('/')}/api/v1/resources/temp_upload"
	temp_headers = {
		"X-API-Key": OV_API_KEY,
		"Content-Type": f"multipart/form-data; boundary={boundary}",
		"Accept": "application/json",
	}
	# Propagate agent identity to the temp-upload endpoint too
	effective_agent = agent_id if agent_id else OV_AGENT_ID
	if effective_agent and effective_agent != "default":
		temp_headers["X-OpenViking-Agent"] = effective_agent

	req = _urlreq.Request(temp_url, data=body_bytes, headers=temp_headers, method="POST")
	try:
		with _urlreq.urlopen(req, timeout=TIMEOUT) as resp:
			upload_result = __import__("json").loads(resp.read().decode("utf-8"))
	except _urlreq.HTTPError as e:
		return f"Error uploading memory: {e.code} {e.read().decode(errors='replace')[:200]}"

	if upload_result.get("status") != "ok":
		return f"Failed to upload memory: {upload_result}"

	temp_id = upload_result["result"]["temp_file_id"]

	# Step 2: Add as resource at the target URI
	result = _ov_request(
		"POST",
		"/api/v1/resources",
		{"temp_file_id": temp_id, "to": uri},
		agent_id=agent_id,
	)
	if result.get("status") == "ok":
		return f"Memory stored: {uri}\nContent will be embedded and summarized asynchronously."
	else:
		return f"Failed to add resource: {result}"


@mcp.tool()
def ov_stats(agent_id: str = "") -> str:
	"""Get memory statistics: file counts, storage size, sync status.

	Args:
	    agent_id: Optional agent identity for namespaced access
	"""
	result = _ov_request("GET", "/api/v1/stats/memories", agent_id=agent_id)
	return _format_result(result)


# ── Session Tools ────────────────────────────────────────────────────────────
# Session tools enable agent memory continuity across conversations.
# Named sessions persist on disk via the OpenViking bind mount.
# If OpenViking is unreachable, tools fall back gracefully so the
# agent can continue with the handoff file.

SESSION_TOKEN_BUDGET = int(os.environ.get("OPENVIKING_SESSION_TOKEN_BUDGET", "4000"))


def _session_fallback(reason: str) -> str:
	"""Return a fallback message when session operations fail."""
	return json.dumps({
		"warning": "Session context unavailable — OpenViking may be down.",
		"error": reason,
		"fallback": "Read .kilo/handoff/current.md for prior context.",
	})


@mcp.tool()
def ov_session_get_or_create(
	session_id: str = "kilo-context",
	agent_id: str = "",
) -> str:
	"""Get or create a named session and return its compiled context.

	Call this at the START of every conversation to load prior decisions,
	open questions, and next steps. The session persists across restarts.

	Returns structured context with:
	- latest_archive_overview: Full summary of most recent session
	- pre_archive_abstracts: One-line summaries of older sessions
	- task state: current goal, progress, blockers, next step
	- estimatedTokens: Context size

	Args:
	    session_id: Session name (default: "kilo-context")
	    agent_id: Optional agent identity for namespaced access
	"""
	try:
		# Try to get existing session
		result = _ov_request("GET", f"/api/v1/sessions/{session_id}", agent_id=agent_id)
		if isinstance(result, dict) and result.get("status") == "error":
			error_code = result.get("error", {}).get("code", "")
			if error_code == "NOT_FOUND":
				# Create new session
				result = _ov_request(
					"POST",
					"/api/v1/sessions",
					{"session_id": session_id},
					agent_id=agent_id,
				)

		# Get compiled context
		ctx = _ov_request(
			"GET",
			f"/api/v1/sessions/{session_id}/context?token_budget={SESSION_TOKEN_BUDGET}",
			agent_id=agent_id,
		)
		return _format_result(ctx)
	except RuntimeError as e:
		return _session_fallback(str(e))


@mcp.tool()
def ov_session_add_message(
	session_id: str,
	role: str,
	content: str,
	agent_id: str = "",
) -> str:
	"""Add a message to the session for later commit.

	Use this mid-conversation to capture important decisions or preferences
	that should survive into the archive summary and memory extraction.

	The message is attributed to the current agent so memories route to
	the correct agent namespace.

	Args:
	    session_id: Session name (default: "kilo-context")
	    role: "user" or "assistant"
	    content: Message text to persist
	    agent_id: Optional agent identity for namespaced access
	"""
	try:
		body = {"role": role, "content": content}
		# Route memories to the correct agent by setting role_id explicitly
		effective_agent = agent_id if agent_id else OV_AGENT_ID
		if role == "assistant" and effective_agent and effective_agent != "default":
			body["role_id"] = effective_agent
		result = _ov_request(
			"POST",
			f"/api/v1/sessions/{session_id}/messages",
			body,
			agent_id=agent_id,
		)
		return _format_result(result)
	except RuntimeError as e:
		return _session_fallback(str(e))


@mcp.tool()
def ov_session_commit(
	session_id: str = "kilo-context",
	agent_id: str = "",
) -> str:
	"""Commit the session — archive messages and start background memory extraction.

	Call this at the END of every conversation.

	Phase 1 (synchronous, ~12ms): Archives messages to history.
	Phase 2 (background, ~8s): LLM generates summaries and extracts
	    memories across 8 categories (profile, preferences, entities,
	    events, cases, patterns, tools, skills).

	Returns a task_id for optional polling via ov_session_get_task.

	Args:
	    session_id: Session name (default: "kilo-context")
	    agent_id: Optional agent identity for namespaced access
	"""
	try:
		result = _ov_request(
			"POST",
			f"/api/v1/sessions/{session_id}/commit",
			agent_id=agent_id,
		)
		return _format_result(result)
	except RuntimeError as e:
		return _session_fallback(str(e))


@mcp.tool()
def ov_session_get_task(task_id: str, agent_id: str = "") -> str:
	"""Poll a background task from ov_session_commit.

	Returns task status and, when completed, memory extraction results
	with per-category counts.

	Args:
	    task_id: Task ID returned by ov_session_commit
	    agent_id: Optional agent identity for namespaced access
	"""
	try:
		result = _ov_request("GET", f"/api/v1/tasks/{task_id}", agent_id=agent_id)
		return _format_result(result)
	except RuntimeError as e:
		return _session_fallback(str(e))


# ── Entrypoint ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
	mcp.run(transport="stdio")
