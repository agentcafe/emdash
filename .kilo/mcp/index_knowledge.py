#!/usr/bin/env python3
"""
Index EmDash knowledge base into OpenViking.
Uploads files via temp_upload → add_resource flow.
"""

import os
import json
import time
import urllib.request
import urllib.error
import mimetypes

OV_API_BASE = "http://localhost:1933"
OV_API_KEY = os.environ.get("OPENVIKING_API_KEY", "dc68bc30f99207b9f07085cf84037abb05529f63d87e2be5b495adffdf5e4099")
PROJECT_ROOT = "/Users/agentcafe/Developer/emdash"
TARGET = "viking://resources/work/emdash"

ROOTS = [
    (os.path.join(PROJECT_ROOT, ".kilo/agent"), "kilo/agent"),
    (os.path.join(PROJECT_ROOT, ".kilo/command"), "kilo/command"),
    (os.path.join(PROJECT_ROOT, ".kilo/handoff"), "kilo/handoff"),
    (os.path.join(PROJECT_ROOT, ".kilo/plans"), "kilo/plans"),
    (os.path.join(PROJECT_ROOT, ".kilo/mcp"), "kilo/mcp"),
    (os.path.join(PROJECT_ROOT, "skills"), "skills"),
]

ROOT_FILES = [
    os.path.join(PROJECT_ROOT, "AGENTS.md"),
    os.path.join(PROJECT_ROOT, "CONTRIBUTING.md"),
]

SKIP_DIRS = {"__pycache__", "node_modules", ".git", "screenshots"}
SKIP_EXTENSIONS = {".pyc"}
VALID_EXTENSIONS = {".md", ".ts", ".tsx", ".js", ".py", ".jsonc", ".yaml", ".yml", ".toml", ".json", ".d.ts"}


def should_skip(fp):
    for d in SKIP_DIRS:
        if f"/{d}/" in fp or fp.endswith(f"/{d}"):
            return True
    ext = os.path.splitext(fp)[1]
    if ext in SKIP_EXTENSIONS:
        return True
    if ext and ext not in VALID_EXTENSIONS:
        return True
    return False


def discover():
    files = []
    for abs_root, uri_suffix in ROOTS:
        for dirpath, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            rel = os.path.relpath(dirpath, abs_root)
            uri_dir = f"{TARGET}/{uri_suffix}" if rel == "." else f"{TARGET}/{uri_suffix}/{rel.replace(os.sep, '/')}"
            for fn in sorted(filenames):
                fp = os.path.join(dirpath, fn)
                if not should_skip(fp):
                    files.append((fp, f"{uri_dir}/{fn}"))
    for fp in ROOT_FILES:
        if os.path.isfile(fp) and not should_skip(fp):
            files.append((fp, f"{TARGET}/{os.path.basename(fp)}"))
    return files


def temp_upload(file_path):
    """Upload file to temp storage, return temp_file_id."""
    boundary = "----OpenVikingUpload"
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    # Build multipart body manually
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += file_data
    body += f"\r\n--{boundary}--\r\n".encode()

    url = f"{OV_API_BASE}/api/v1/resources/temp_upload"
    headers = {
        "X-API-Key": OV_API_KEY,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "application/json",
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            if result.get("status") == "ok":
                return result["result"]["temp_file_id"]
            return None
    except urllib.error.HTTPError as e:
        print(f"    upload error {e.code}: {e.read().decode(errors='replace')[:200]}")
        return None


def add_resource(temp_file_id, to_uri):
    """Add temp resource to the target URI."""
    url = f"{OV_API_BASE}/api/v1/resources"
    body = json.dumps({"temp_file_id": temp_file_id, "to": to_uri}).encode()
    headers = {
        "X-API-Key": OV_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result
    except urllib.error.HTTPError as e:
        return {"status": "error", "msg": e.read().decode(errors="replace")[:200]}


# ── Main ────────────────────────────────────────────────────────────────────
files = discover()
print(f"Indexing {len(files)} files to {TARGET}\n{'-'*60}")

ok = err = 0
for i, (fp, uri) in enumerate(files, 1):
    rel = os.path.relpath(fp, PROJECT_ROOT)
    print(f"[{i}/{len(files)}] {rel}")

    tid = temp_upload(fp)
    if not tid:
        print(f"  ✗ upload failed")
        err += 1
        continue

    result = add_resource(tid, uri)
    if result.get("status") == "ok":
        print(f"  ✓ {result.get('result', {}).get('root_uri', uri)}")
        ok += 1
    else:
        print(f"  ✗ {result.get('msg', json.dumps(result)[:150])}")
        err += 1

    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"Done: {ok} queued, {err} errors")
print("OpenViking is now generating embeddings + summaries asynchronously.")
print("VLM: o4-mini (free tier, 2.5M tokens/day)")
