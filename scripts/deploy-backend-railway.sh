#!/usr/bin/env bash
set -euo pipefail

if ! command -v railway >/dev/null 2>&1; then
  echo "railway CLI not found. Install with: npm i -g @railway/cli"
  exit 1
fi

echo "Deploying backend/ service to Railway..."
cd backend
railway up
