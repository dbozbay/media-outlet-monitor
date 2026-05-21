#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(dirname "$0")"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

while IFS= read -r pyproject; do
  dir="$(dirname "$pyproject")"
  echo "Testing ${dir#"$ROOT"/}..."
  (cd "$dir" && uv run pytest)
done < <(find "$ROOT/services" -name "pyproject.toml" -type f)

echo "All tests passed."
