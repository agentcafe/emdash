#!/bin/bash
set -e

DOCS_DIR="/Users/agentcafe/.vscode/extensions/kilocode.kilo-code-7.2.25-darwin-arm64/docs"
OV_HOST="${OPENVIKING_HOST:-http://localhost:8080}"
API_KEY="${OPENVIKING_API_KEY:-}"
QUEUE_URL="$OV_HOST/_emdash/api/observer/queue"

# Get all .md files sorted into array
while IFS= read -r line; do
  FILES+=("$line")
done < <(find "$DOCS_DIR" -type f -name "*.md" | sort)

TOTAL=${#FILES[@]}
echo "Found $TOTAL files to index"

BATCH=0
INDEXED=0
ERRORS=0

index_file() {
  local FILE="$1"
  local DEST="viking://resources/kb/kilo/docs/$(basename "$FILE")"
  local RESP
  RESP=$(curl -s -X POST "$OV_HOST/_emdash/api/v1/resource/add" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    --data-binary "{\"path\":\"$FILE\",\"to\":\"$DEST\"}" 2>/dev/null)
  echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('status')=='ok' else 'FAIL: '+str(d))" 2>/dev/null || echo "FAIL: curl error"
}

check_queue() {
  curl -s "$QUEUE_URL" -H "Authorization: Bearer $API_KEY" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2))" 2>/dev/null || echo "{}"
}

for FILE in "${FILES[@]}"; do
  BATCH=$((BATCH % 10 + 1))
  echo -n "[$((INDEXED+1))/$TOTAL] $(basename $FILE) ... "
  if index_file "$FILE"; then
    INDEXED=$((INDEXED+1))
  else
    ERRORS=$((ERRORS+1))
  fi

  if [ $BATCH -eq 10 ]; then
    echo ""
    echo "=== Batch done ($INDEXED indexed so far). Checking queue ==="
    check_queue
    sleep 3
    echo ""
  fi
done

echo ""
echo "=== Done. Indexed: $INDEXED, Errors: $ERRORS ==="
echo "=== Final queue state ==="
check_queue