#!/usr/bin/env bash
# Update a ticket on the live board API.
# Usage: board_set.sh SV0-01.04 Done [message]
set -euo pipefail
KEY="${1:?ticket key}"
STATE="${2:?workflow state}"
MSG="${3:-agent update}"
API="${SVARAA_API:-http://127.0.0.1:18001}"
curl -sS -X POST "${API}/lab/v1/tickets/${KEY}/transition" \
  -H 'Content-Type: application/json' \
  -d "{\"to_state\":\"${STATE}\",\"actor\":\"agent\",\"message\":\"${MSG}\",\"force\":true}"
echo
