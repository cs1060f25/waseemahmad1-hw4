#!/usr/bin/env bash
set -euo pipefail

API="${API:-https://waseemahmad1-hw4.vercel.app/county_data}"
ROOT="${ROOT:-https://waseemahmad1-hw4.vercel.app}"
CT='content-type: application/json'

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing dep: $1" >&2; exit 1; }
}
require curl
require jq

pass() { echo "✅ $*"; }
fail() { echo "❌ $*"; exit 1; }

# helper: status + json check
check_status() {
  local expected="$1"; shift
  local out status body
  out=$(curl -sS -H "$CT" -d "$*" -w "|||%{http_code}" "$API")
  status="${out##*|||}"
  body="${out%|||*}"
  [ "$status" = "$expected" ] || { echo "Expected $expected, got $status. Body: $body"; exit 1; }
  # if 200, ensure valid JSON array
  if [ "$status" = "200" ]; then
    echo "$body" | jq -e 'type=="array"' >/dev/null || fail "200 body not a JSON array"
  else
    echo "$body" | jq -e . >/dev/null || fail "Non-200 body is not valid JSON"
  fi
}

echo "1) Happy path -> expect 200 and JSON array"
check_status 200 '{"zip":"02138","measure_name":"Adult obesity"}'
pass "Happy path ok"

echo "2) Teapot precedence -> expect 418 even if keys missing"
out=$(curl -sS -H "$CT" -d '{"coffee":"teapot"}' -w "|||%{http_code}" "$API")
status="${out##*|||}"
[ "$status" = "418" ] || fail "teapot not 418 (got $status)"
pass "Teapot ok"

echo "3) Missing key -> 400"
check_status 400 '{"zip":"02138"}'
pass "Missing key ok"

echo "4) Bad measure -> 404"
check_status 404 '{"zip":"02138","measure_name":"Not real"}'
pass "Bad measure ok"

echo "5) Injection-ish measure -> 404 (blocked by whitelist)"
check_status 404 '{"zip":"02138","measure_name":"Adult obesity\" OR \"1\"=\"1"}'
pass "Injection blocked ok"

echo "6) Bad zip format -> 400 (zip must be 5-digit string)"
check_status 400 '{"zip":"2138","measure_name":"Adult obesity"}'
check_status 400 '{"zip":"021380","measure_name":"Adult obesity"}'
check_status 400 '{"zip":2138,"measure_name":"Adult obesity"}'
pass "Zip validation ok"

echo "7) GET /county_data -> expect 405 if helper added (or 404 if not)"
code=$(curl -s -o /dev/null -w "%{http_code}" "$ROOT/county_data")
if [ "$code" = "405" ] || [ "$code" = "404" ]; then
  pass "GET /county_data returned $code as expected"
else
  fail "GET /county_data returned $code"
fi

echo "8) Wrong path -> 404"
code=$(curl -s -o /dev/null -w "%{http_code}" "$ROOT/not_a_route")
[ "$code" = "404" ] || fail "Wrong path not 404 (got $code)"
pass "Wrong path 404 ok"

echo "All tests passed ✅"
