#!/bin/bash
set -e #exits when unhandled command fails

cd "$(dirname "$0")/../backend"

.venv/bin/python -m uvicorn app.main:app --reload