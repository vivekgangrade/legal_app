#!/bin/bash
# ============================================================
# setup-ec2.sh — First-Time EC2 Instance Setup
# ============================================================
# Run this ONCE on a fresh Ubuntu EC2 instance.
#
# Usage:
#   chmod +x scripts/setup-ec2.sh
#   sudo ./scripts/setup-ec2.sh
#
# What it does:
#   1. Updates system packages
#   2. Installs Docker & Docker Compose
#   3. Installs Nginx (optional, for non-Docker Nginx)
#   4. Creates app user and directory structure
#   5. Configures firewall
#   6. Creates swap file (for small instances)
#   7. Sets up log rotation
# ============================================================

set -euo pipefail

echo "============================================"
echo "  Legal AI Platform — EC2 Setup Script"
echo "============================================"

# ── 1. System Update ────────────────────────────────────────
echo ""
echo "📦 Step 1: Updating system packages..."
apt-get update -y
apt-get upgrade -y
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    nano \
    ufw \
    fail2ban

# ── 2. Install Docker ──────────────────────────────────────
echo ""
echo "🐳 Step 2: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh

    # Allow current user to run Docker without sudo
    usermod -aG docker ubuntu
    echo "Docker installed successfully."
else
    echo "Docker already installed."
fi

# ── 3. Install Docker Compose ──────────────────────────────
echo ""
echo "🐳 Step 3: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose ${COMPOSE_VERSION} installed."
else
    echo "Docker Compose already installed."
fi

# ── 4. Configure Firewall ──────────────────────────────────
echo ""
echo "🔥 Step 4: Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh          # Port 22
ufw allow http         # Port 80
ufw allow https        # Port 443
ufw --force enable
echo "Firewall configured: SSH, HTTP, HTTPS allowed."

# ── 5. Create App Directory ────────────────────────────────
echo ""
echo "📁 Step 5: Creating app directory..."
APP_DIR="/home/ubuntu/legal-ai-platform"
mkdir -p "${APP_DIR}"
chown -R ubuntu:ubuntu "${APP_DIR}"
echo "App directory: ${APP_DIR}"

# ── 6. Create Swap File (for t2.micro/small instances) ─────
echo ""
echo "💾 Step 6: Setting up swap file..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "2GB swap file created."
else
    echo "Swap file already exists."
fi

# ── 7. Log Rotation ───────────────────────────────────────
echo ""
echo "📋 Step 7: Setting up log rotation..."
cat > /etc/logrotate.d/legal-ai << 'EOF'
/home/ubuntu/legal-ai-platform/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
}
EOF
echo "Log rotation configured (14 days, compressed)."

# ── 8. Enable Docker on boot ──────────────────────────────
echo ""
echo "⚡ Step 8: Enabling Docker on boot..."
systemctl enable docker
systemctl start docker

# ── Done ───────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  ✅ EC2 Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. cd ${APP_DIR}"
echo "  2. git clone <your-repo-url> ."
echo "  3. cp .env.example .env && nano .env"
echo "  4. docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
echo ""
echo "⚠️  Log out and log back in for Docker group changes to take effect."
echo ""
