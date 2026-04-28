#!/bin/bash
# ============================================================
# deploy.sh — Deployment Script (run on EC2)
# ============================================================
# Pulls latest code, rebuilds containers, and restarts services.
# Supports rollback on failure.
#
# Usage:
#   ./scripts/deploy.sh           # Normal deploy
#   ./scripts/deploy.sh rollback  # Rollback to previous version
# ============================================================

set -euo pipefail

APP_DIR="/home/ubuntu/legal-ai-platform"
COMPOSE_CMD="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

cd "${APP_DIR}"

# ── Rollback Mode ──────────────────────────────────────────
if [ "${1:-}" = "rollback" ]; then
    echo "⏪ Rolling back to previous version..."
    git checkout HEAD~1
    ${COMPOSE_CMD} build --no-cache
    ${COMPOSE_CMD} up -d
    echo "✅ Rollback complete."
    exit 0
fi

# ── Normal Deploy ──────────────────────────────────────────

echo "============================================"
echo "  🚀 Deploying Legal AI Platform"
echo "  Time: ${TIMESTAMP}"
echo "============================================"

# Step 1: Save current commit for rollback
CURRENT_COMMIT=$(git rev-parse HEAD)
echo "📌 Current commit: ${CURRENT_COMMIT}"

# Step 2: Pull latest code
echo ""
echo "📥 Step 1: Pulling latest code..."
git pull origin main

NEW_COMMIT=$(git rev-parse HEAD)
echo "📌 New commit: ${NEW_COMMIT}"

if [ "${CURRENT_COMMIT}" = "${NEW_COMMIT}" ]; then
    echo "ℹ️  No new changes to deploy."
    echo "   Use './scripts/deploy.sh rollback' to force a rebuild."
fi

# Step 3: Build new containers
echo ""
echo "🔨 Step 2: Building containers..."
${COMPOSE_CMD} build

# Step 4: Stop old containers and start new ones
echo ""
echo "🔄 Step 3: Restarting services..."
${COMPOSE_CMD} down
${COMPOSE_CMD} up -d

# Step 5: Wait for health check
echo ""
echo "⏳ Step 4: Waiting for health check (30s)..."
sleep 30

# Step 6: Verify
echo ""
echo "🏥 Step 5: Checking health..."
HEALTH_STATUS=$(curl -sf http://localhost:10000/health || echo "FAILED")

if echo "${HEALTH_STATUS}" | grep -q "healthy"; then
    echo "✅ Health check passed!"
    echo "${HEALTH_STATUS}"
else
    echo "❌ Health check failed! Rolling back..."
    git checkout "${CURRENT_COMMIT}"
    ${COMPOSE_CMD} build
    ${COMPOSE_CMD} up -d
    echo "⏪ Rolled back to ${CURRENT_COMMIT}"
    exit 1
fi

# Step 7: Clean up old images
echo ""
echo "🧹 Step 6: Cleaning up old Docker images..."
docker image prune -f

echo ""
echo "============================================"
echo "  ✅ Deployment Complete!"
echo "  Commit: ${NEW_COMMIT}"
echo "============================================"

# Show running containers
docker-compose ps
