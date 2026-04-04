#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:5002}"
REQUESTS="${2:-50}"
DELAY_MS="${3:-0}"

post_ok=0
post_err=0
get_ok=0
get_err=0

sleep_ms() {
  local ms="$1"
  if [[ "$ms" == "0" ]]; then
    return 0
  fi
  # bash sleep uses seconds; support ms with awk
  awk -v ms="$ms" 'BEGIN { printf "%.3f", ms/1000 }' | xargs -I{} sleep {}
}

echo "Generating traffic against order service at $BASE_URL ($REQUESTS iterations)..."

for ((i=1; i<=REQUESTS; i++)); do
  user_id=$(( (RANDOM % 5) + 1 ))

  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BASE_URL/orders" \
    -H "Content-Type: application/json" \
    --data "{\"user_id\":\"$user_id\"}" || echo "000")

  if [[ "$code" =~ ^2 ]]; then
    post_ok=$((post_ok+1))
  else
    post_err=$((post_err+1))
  fi

  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "$BASE_URL/orders" || echo "000")

  if [[ "$code" =~ ^2 ]]; then
    get_ok=$((get_ok+1))
  else
    get_err=$((get_err+1))
  fi

  sleep_ms "$DELAY_MS"
done

echo "Done."
echo "POST /orders: ok=$post_ok err=$post_err"
echo "GET  /orders: ok=$get_ok  err=$get_err"
echo "Now check Grafana dashboards (Logs/Traces) for fresh data."
