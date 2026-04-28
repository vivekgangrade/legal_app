# 🚢 AWS Deployment Guide

Step-by-step guide to deploy the Legal AI Platform on AWS EC2.

---

## Prerequisites

- AWS account with EC2 access
- A key pair (.pem file) for SSH
- API keys for Groq and Tavily

---

## Step 1: Launch EC2 Instance

### Recommended Configuration

| Setting | Value |
|---------|-------|
| **AMI** | Ubuntu 22.04 LTS (x86_64) |
| **Instance Type** | `t3.medium` (2 vCPU, 4GB RAM) — minimum viable |
| **Storage** | 20 GB gp3 SSD |
| **Key Pair** | Create or select existing |

### Security Group Rules

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| SSH | 22 | Your IP | Remote access |
| HTTP | 80 | 0.0.0.0/0 | Web traffic |
| HTTPS | 443 | 0.0.0.0/0 | SSL traffic (future) |

> **Tip:** For testing, you can also open port `10000` to access Gradio directly without Nginx.

---

## Step 2: Connect to Your Instance

```bash
# Make key file read-only
chmod 400 your-key.pem

# SSH into the instance
ssh -i your-key.pem ubuntu@<your-ec2-public-ip>
```

---

## Step 3: Run Setup Script

```bash
# Upload or clone the project
git clone <your-repo-url> /home/ubuntu/legal-ai-platform
cd /home/ubuntu/legal-ai-platform

# Run first-time setup (installs Docker, firewall, etc.)
sudo ./scripts/setup-ec2.sh

# IMPORTANT: Log out and back in for Docker group to take effect
exit
ssh -i your-key.pem ubuntu@<your-ec2-public-ip>
```

---

## Step 4: Configure Environment

```bash
cd /home/ubuntu/legal-ai-platform

# Create .env from template
cp .env.example .env

# Edit with your API keys
nano .env
```

**Minimum required:**
```
GROQ_API_KEY=gsk_your_actual_key_here
TAVILY_API_KEY=tvly_your_actual_key_here
APP_ENV=production
PORT=10000
```

---

## Step 5: Deploy

```bash
# Build and start all services (app + Nginx)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

---

## Step 6: Verify

```bash
# Health check
curl http://localhost/health
# Should return: {"status": "healthy", ...}

# Open in browser
# http://<your-ec2-public-ip>
```

---

## Updating the App

```bash
cd /home/ubuntu/legal-ai-platform

# Option 1: Use deploy script (with rollback)
./scripts/deploy.sh

# Option 2: Manual
git pull origin main
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## Setting Up a Domain Name

1. **Buy a domain** (e.g., Namecheap, GoDaddy, Route 53)
2. **Create A record** pointing to your EC2 Elastic IP
3. **Get SSL certificate** with Certbot:

```bash
# Install Certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certs to Nginx directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Uncomment HTTPS block in nginx/nginx.conf
# Restart Nginx
docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

---

## Monitoring Recommendations

| Tool | Purpose | Cost |
|------|---------|------|
| **CloudWatch** | CPU, memory, disk metrics | Free tier available |
| **UptimeRobot** | Uptime monitoring (ping /health) | Free (50 monitors) |
| **Better Stack** | Log aggregation + alerts | Free tier |
| **Sentry** | Error tracking in Python | Free tier |

### Set Up CloudWatch Alarms

```bash
# CPU > 80% alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "Legal-AI-High-CPU" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

---

## Cost Estimation

| Resource | Monthly Cost (USD) |
|----------|-------------------|
| EC2 t3.medium | ~$30 |
| EBS 20GB gp3 | ~$2 |
| Data transfer (10GB) | ~$1 |
| **Total** | **~$33/month** |

> **Save money:** Use `t3.micro` (free tier) for testing, Reserved Instances for production.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Container won't start | `docker-compose logs app` — check for errors |
| Port 80 not accessible | Check security group allows HTTP |
| Out of memory | Use `t3.medium` or add swap (setup script does this) |
| Health check fails | Ensure API keys are set in `.env` |
| Slow first request | Embedding model downloads on first use (pre-cached in Docker) |
