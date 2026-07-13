#!/usr/bin/env bash
set -euo pipefail

for cmd in docker kubectl kind helm terraform ansible git; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] $cmd -> $($cmd version 2>/dev/null | head -n 1 || $cmd --version | head -n 1)"
  else
    echo "[MISSING] $cmd"
    exit 1
  fi
done
