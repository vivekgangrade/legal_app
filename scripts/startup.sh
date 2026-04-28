#!/bin/bash
# ============================================================
# startup.sh — Container Entry Point
# ============================================================
# This script is the CMD for the Docker container.
# It decides how to start the app based on APP_ENV:
#
#   development → Gradio's built-in dev server (hot reload)
#   production  → Gradio direct (Gradio handles its own ASGI)
#
# Note: Gradio bundles its own Uvicorn server internally.
# Using external Gunicorn with Gradio can cause WebSocket
# issues, so we let Gradio manage its own server.
# ============================================================

set -euo pipefail

APP_ENV="${APP_ENV:-development}"
PORT="${PORT:-10000}"

echo "============================================"
echo "  Legal AI Platform — Starting..."
echo "  Environment: ${APP_ENV}"
echo "  Port: ${PORT}"
echo "============================================"

if [ "${APP_ENV}" = "production" ]; then
    echo "🚀 Starting in PRODUCTION mode..."
    echo "   Server: Gradio (built-in Uvicorn)"
    echo "   Port: ${PORT}"
    exec python app.py
else
    echo "🔧 Starting in DEVELOPMENT mode..."
    echo "   Server: Gradio dev server"
    echo "   Port: ${PORT}"
    exec python app.py
fi
