#!/usr/bin/env bash
# build.sh — Render Build Script
# Installs dependencies with memory-optimized settings

set -o errexit

# Install PyTorch CPU (saves massive memory on free tier)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other Python dependencies
pip install --no-cache-dir -r requirements.txt

# Create required directories
mkdir -p outputs logs
