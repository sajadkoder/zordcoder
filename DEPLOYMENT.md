# Zord Coder Deployment Guide

Complete guide for deploying Zord Coder to various hosting platforms.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Start Recommendation](#2-quick-start-recommendation)
3. [HuggingFace Spaces Deployment](#3-huggingface-spaces-deployment)
4. [Render Deployment](#4-render-deployment)
5. [Fly.io Deployment (GPU)](#5-flyio-deployment-gpu)
6. [Local + Tunnel (Development)](#6-local--tunnel-development)
7. [Frontend Deployment (Vercel)](#7-frontend-deployment-vercel)
8. [Architecture Diagrams](#8-architecture-diagrams)
9. [Cost Comparison](#9-cost-comparison)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Overview

### Hosting Options Comparison

| Platform | Cost | Performance | Complexity | GPU Support | Best For |
|----------|------|-------------|------------|-------------|----------|
| **HuggingFace Spaces** | Free | Medium | Low | No (CPU only) | Quick demo, public API |
| **Render** | Free / $7+/mo | Medium | Medium | No | Production API, reliable uptime |
| **Fly.io** | $0-5+/mo | High | High | Yes | GPU inference, low latency |
| **Local + Tunnel** | Free | High | Low | Yes | Development, testing |
| **Vercel (Frontend)** | Free / $20+/mo | High | Low | N/A | Frontend hosting |

### Detailed Feature Matrix

| Feature | HuggingFace | Render | Fly.io | Local |
|---------|-------------|--------|--------|-------|
| Free tier available | Yes | Yes | $5 credit | Yes |
| Custom domain | Yes | Yes | Yes | Via tunnel |
| Auto-scaling | No | Yes | Yes | N/A |
| Persistent storage | No | Yes (disk) | Yes (vol) | Yes |
| Cold start time | ~30s | ~60s | ~10s | Instant |
| Max RAM (free) | 16GB | 512MB | N/A | Unlimited |
| SSL/HTTPS | Auto | Auto | Auto | Via tunnel |
| Rate limiting | Built-in | Custom | Custom | Custom |

---

## 2. Quick Start Recommendation

### Choose Your Path

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHAT DO YOU NEED?                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "I want to test it quickly"                                    │
│  ───────────────────────────                                    │
│  → HuggingFace Spaces (5 min setup, free)                       │
│                                                                 │
│  "I need a reliable production API"                             │
│  ───────────────────────────────                                │
│  → Render (Free tier or $7/mo Starter)                          │
│                                                                 │
│  "I need fast GPU inference"                                    │
│  ─────────────────────────                                      │
│  → Fly.io with GPU ($0.50/hr A100)                              │
│                                                                 │
│  "I'm developing and testing"                                   │
│  ─────────────────────────                                      │
│  → Local + ngrok/Cloudflare Tunnel                              │
│                                                                 │
│  "I want a public web interface"                                │
│  ───────────────────────────────                                │
│  → Vercel (frontend) + Render/Fly.io (backend)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Decision Tree

```
START
  │
  ├── Need GPU for faster inference?
  │     ├── Yes → Fly.io (GPU instances)
  │     └── No ↓
  │
  ├── Need always-on production service?
  │     ├── Yes → Render (Starter plan $7/mo)
  │     └── No ↓
  │
  ├── Just testing/demo?
  │     ├── Yes → HuggingFace Spaces (Free)
  │     └── No ↓
  │
  └── Development/Personal use?
        └── Local + Tunnel (Free)
```

---

## 3. HuggingFace Spaces Deployment

### Overview

HuggingFace Spaces provides free CPU hosting with automatic model download and easy public sharing.

| Aspect | Details |
|--------|---------|
| **Cost** | Free |
| **RAM** | Up to 16GB (free tier) |
| **Storage** | Ephemeral (model re-downloads on restart) |
| **Performance** | 5-15 tokens/sec |
| **URL Format** | `https://YOUR-SPACE.hf.space` |

### Step-by-Step Instructions

#### Step 1: Create HuggingFace Account

1. Go to https://huggingface.co
2. Click "Sign Up" and create a free account
3. Verify your email

#### Step 2: Create a New Space

1. Click your profile avatar → "New Space"
2. Fill in the details:
   - **Name**: `zordcoder` (or your preferred name)
   - **SDK**: Select "Docker"
   - **License**: MIT
   - **Visibility**: Public (required for free tier)
3. Click "Create Space"

#### Step 3: Prepare Files

Create these files in your Space repository:

**README.md** (Space metadata):
```markdown
---
title: Zord Coder v1
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Zord Coder v1

A multilingual coding assistant powered by DeepSeek Coder.
```

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    llama-cpp-python==0.2.90 \
    flask==3.0.0 \
    huggingface-hub==0.20.0

COPY app.py /app/app.py

RUN mkdir -p /app/models

ENV MODEL_REPO=TheBloke/deepseek-coder-1.3b-instruct-GGUF
ENV MODEL_FILE=deepseek-coder-1.3b-instruct-q4_k_m.gguf
ENV MODEL_PATH=/app/models/model.gguf
ENV PORT=7860
ENV HOST=0.0.0.0

EXPOSE 7860

CMD ["python", "app.py"]
```

**app.py** (see `deploy/huggingface/app.py` in repository)

#### Step 4: Upload Files

**Via Web Interface:**
1. Go to your Space page
2. Click "Files" → "Add file" → "Upload files"
3. Upload `Dockerfile`, `app.py`, and `README.md`

**Via Git:**
```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/zordcoder
cd zordcoder

# Copy files
cp /path/to/zordcoder/deploy/huggingface/Dockerfile .
cp /path/to/zordcoder/deploy/huggingface/app.py .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### Step 5: Wait for Build

- Build takes 5-10 minutes
- Model downloads automatically (~833MB)
- Watch logs in the "Logs" tab

### Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MODEL_REPO` | TheBloke/deepseek-coder-1.3b-instruct-GGUF | HuggingFace model repo |
| `MODEL_FILE` | deepseek-coder-1.3b-instruct-q4_k_m.gguf | GGUF model filename |
| `MODEL_PATH` | /app/models/model.gguf | Local model path |
| `PORT` | 7860 | Server port |
| `HOST` | 0.0.0.0 | Server host |

### API Usage

```bash
# Health check
curl https://YOUR_USERNAME-zordcoder.hf.space/health

# Generate code
curl -X POST https://YOUR_USERNAME-zordcoder.hf.space/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to reverse a string",
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Cost Breakdown

| Item | Cost |
|------|------|
| CPU Space (Free tier) | $0/month |
| Custom domain | Free |
| SSL certificate | Free |
| **Total** | **$0/month** |

### Limitations

- Public visibility required (free tier)
- Cold starts after 48h inactivity
- Ephemeral storage (model re-downloads)
- Rate limited: 50 messages/day per IP

---

## 4. Render Deployment

### Overview

Render provides reliable cloud hosting with automatic SSL, custom domains, and persistent storage.

| Aspect | Details |
|--------|---------|
| **Free Tier** | 512MB RAM, spins down after inactivity |
| **Starter Plan** | $7/month, 512MB RAM, always on |
| **Standard Plan** | $25/month, 2GB RAM |
| **Performance** | 5-10 tokens/sec (CPU) |

### Step-by-Step Instructions

#### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub, GitLab, or email
3. Verify your account

#### Step 2: Prepare Repository

Ensure your repository has:
- `Dockerfile` at `deploy/render/Dockerfile`
- `render.yaml` at `deploy/render/render.yaml`
- `start.sh` at `deploy/render/start.sh`

#### Step 3: Create Web Service

**Via Blueprint (Recommended):**
1. Go to Render Dashboard → "New" → "Blueprint"
2. Connect your GitHub/GitLab repository
3. Render detects `render.yaml` automatically
4. Click "Apply" to create services

**Via Dashboard:**
1. Go to Render Dashboard → "New" → "Web Service"
2. Connect repository
3. Configure:
   - **Name**: zordcoder-api
   - **Runtime**: Docker
   - **Dockerfile Path**: `./deploy/render/Dockerfile`
   - **Plan**: Free (or Starter)

#### Step 4: Configure Environment

Set these environment variables in Render dashboard:

```
PYTHONUNBUFFERED=1
ZORD_MODEL_PATH=/app/models/zordcoder-v1-q4_k_m.gguf
ZORD_N_CTX=2048
ZORD_N_THREADS=2
```

#### Step 5: Deploy

1. Click "Create Web Service"
2. Wait for build (5-10 minutes)
3. Check logs for "Server running"
4. Service URL: `https://zordcoder-api.onrender.com`

### Free Tier Limitations

| Limitation | Impact |
|------------|--------|
| 512MB RAM | May crash with large models |
| Spins down after 15 min inactivity | Cold start ~60 seconds |
| 400 hours/month | ~13 hours/day average |
| No persistent disk | Model re-downloads |

### Paid Tier Options

| Plan | RAM | CPU | Price | Best For |
|------|-----|-----|-------|----------|
| Starter | 512MB | 0.5 CPU | $7/mo | Always-on hobby projects |
| Standard | 2GB | 1 CPU | $25/mo | Small production |
| Pro | 4GB | 2 CPU | $85/mo | Production workloads |

### Configuration Files

**render.yaml**:
```yaml
services:
  - type: web
    name: zordcoder-api
    runtime: docker
    dockerfilePath: ./deploy/render/Dockerfile
    dockerContext: .
    plan: free
    healthCheckPath: /health
    envVars:
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: ZORD_MODEL_PATH
        value: /app/models/zordcoder-v1-q4_k_m.gguf
      - key: ZORD_N_CTX
        value: "2048"
      - key: ZORD_N_THREADS
        value: "2"
    disk:
      name: model-storage
      mountPath: /app/models
      sizeGB: 1
```

**start.sh**:
```bash
#!/bin/bash
set -e

# Download model if not present
if [ ! -f "$ZORD_MODEL_PATH" ]; then
    echo "Downloading model..."
    python scripts/download_model.py
fi

# Start server
echo "Starting server..."
python web/server.py --host 0.0.0.0 --port ${PORT:-10000}
```

---

## 5. Fly.io Deployment (GPU)

### Overview

Fly.io offers GPU instances for high-performance inference with pay-per-second billing.

| Instance Type | GPU | RAM | Price |
|---------------|-----|-----|-------|
| a100-40gb | A100 40GB | 80GB | $2.50/hr |
| a100-80gb | A100 80GB | 160GB | $4.00/hr |
| l4 | L4 24GB | 48GB | $0.50/hr |
| shared-cpu | None | 256MB-8GB | Free tier |

### Step-by-Step Instructions

#### Step 1: Install Fly CLI

**Windows:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**macOS:**
```bash
brew install flyctl
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

#### Step 2: Create Account & Login

```bash
# Create account
fly auth signup

# Login
fly auth login
```

#### Step 3: Configure Application

Create `fly.toml` in your project root:

```toml
app = "zordcoder"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"
  MODEL_CACHE_DIR = "/data/models"

[mounts]
  source = "model_cache"
  destination = "/data/models"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 2
  memory_mb = 4096

[checks]
  [checks.health]
    grace_period = "30s"
    interval = "15s"
    method = "get"
    path = "/health"
    port = 8080
    timeout = "10s"
    type = "http"
```

#### Step 4: Create Persistent Volume

```bash
# Create volume for model cache (1GB)
fly volumes create model_cache --region ord --size 1
```

#### Step 5: Deploy

```bash
# First deploy
fly launch

# Or redeploy
fly deploy
```

#### Step 6: Scale (Optional)

```bash
# Scale to GPU
fly machine update --vm-gpu-kind a100-40gb

# Scale CPU/Memory
fly scale vm shared-cpu-2x --memory 4096
```

### GPU Instance Types

| Type | Use Case | Performance | Cost/hr |
|------|----------|-------------|---------|
| **L4** | Development, testing | 50+ tokens/sec | $0.50 |
| **A100 40GB** | Production | 100+ tokens/sec | $2.50 |
| **A100 80GB** | Large models, batch | 150+ tokens/sec | $4.00 |

### Cost Optimization Tips

#### 1. Use Scale-to-Zero

```toml
# fly.toml
[http_service]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
```

This stops machines when idle, only paying for active time.

#### 2. Use Smaller Quantization

```bash
# Use Q4_K_M instead of Q8
# Saves memory, slightly lower quality
MODEL_FILE=deepseek-coder-1.3b-instruct-q4_k_m.gguf
```

#### 3. Regional Selection

Choose regions closer to your users:
- `ord` - Chicago (US Central)
- `lax` - Los Angeles (US West)
- `fra` - Frankfurt (EU)
- `sin` - Singapore (Asia)

#### 4. Use Fallback to CPU

```bash
# Start with CPU, scale to GPU when needed
fly scale vm shared-cpu-2x --memory 2048

# When traffic increases
fly scale vm performance-2x --memory 4096
```

### Monthly Cost Estimates

| Usage Pattern | Configuration | Estimated Cost |
|---------------|---------------|----------------|
| Testing (5 hrs/week) | L4 GPU | ~$10/month |
| Light use (2 hrs/day) | L4 GPU | ~$30/month |
| Moderate (8 hrs/day) | A100 40GB | ~$600/month |
| Heavy (24/7) | A100 40GB | ~$1,800/month |
| Development | CPU shared | Free-$5/month |

---

## 6. Local + Tunnel (Development)

### Overview

Run Zord Coder locally and expose it via a tunnel for external access.

| Method | Cost | Speed | Security | Custom Domain |
|--------|------|-------|----------|---------------|
| **ngrok** | Free/Paid | Fast | Good | Paid |
| **Cloudflare Tunnel** | Free | Fast | Excellent | Yes |
| **Tailscale** | Free | Fast | Excellent | Via Funnel |

### ngrok Setup

#### Installation

**Windows:**
```powershell
# Using Chocolatey
choco install ngrok

# Or download from https://ngrok.com/download
```

**macOS:**
```bash
brew install ngrok/ngrok/ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

#### Configuration

1. Create account at https://ngrok.com
2. Get your authtoken from dashboard
3. Configure:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

#### Usage

```bash
# Start local server
python web/server.py

# In another terminal, start tunnel
ngrok http 8000
```

Output:
```
Session Status                online
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

Use `https://abc123.ngrok.io` as your public URL.

#### ngrok Configuration File

`~/.ngrok2/ngrok.yml`:

```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN

tunnels:
  zordcoder:
    proto: http
    addr: 8000
    inspect: true
    basic_auth:
      - "user:password"
```

Start with:
```bash
ngrok start zordcoder
```

### Cloudflare Tunnel Setup

#### Installation

**Windows:**
```powershell
winget install cloudflare.cloudflared
```

**macOS:**
```bash
brew install cloudflared
```

**Linux:**
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

#### Quick Tunnel (No Account)

```bash
# Start local server
python web/server.py

# Quick tunnel (no account needed)
cloudflared tunnel --url http://localhost:8000
```

Output:
```
Your quick Tunnel has been created! Visit it at:
https://random-name-xxxx.trycloudflare.com
```

#### Named Tunnel (With Account)

1. Login:
```bash
cloudflared tunnel login
```

2. Create tunnel:
```bash
cloudflared tunnel create zordcoder
```

3. Configure DNS:
```bash
cloudflared tunnel route dns zordcoder zordcoder.yourdomain.com
```

4. Run tunnel:
```bash
cloudflared tunnel run zordcoder
```

#### Configuration File

`~/.cloudflared/config.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /path/to/credentials.json

ingress:
  - hostname: zordcoder.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

### Tailscale Setup

#### Installation

**Windows:**
```powershell
winget install Tailscale.Tailscale
```

**macOS:**
```bash
brew install tailscale
```

**Linux:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

#### Configuration

1. Create account at https://tailscale.com
2. Authenticate:

```bash
tailscale up
```

#### Serve Locally

```bash
# Start local server
python web/server.py

# Serve on Tailscale network
tailscale serve http://localhost:8000

# Or run in background
tailscale serve --bg http://localhost:8000
```

#### Public Access (Funnel)

```bash
# Enable public access
tailscale funnel --bg --https=:443 http://localhost:8000
```

Your public URL will be:
- `https://<machine-name>.tailnet-name.ts.net`

### Security Considerations

#### 1. Authentication

```bash
# ngrok basic auth
ngrok http -auth="admin:secretpass" 8000

# Cloudflare Access (in dashboard)
# Add email/SSO authentication
```

#### 2. Rate Limiting

Add rate limiting to your server:

```python
from flask import Flask, request, jsonify
from functools import wraps
import time

app = Flask(__name__)

def rate_limit(max_requests=60, window=60):
    requests = {}
    
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            
            if ip not in requests:
                requests[ip] = []
            
            requests[ip] = [t for t in requests[ip] if now - t < window]
            
            if len(requests[ip]) >= max_requests:
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            requests[ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator
```

#### 3. HTTPS Only

All tunnel services provide HTTPS automatically:
- ngrok: `https://*.ngrok.io`
- Cloudflare: `https://*.trycloudflare.com`
- Tailscale: `https://*.ts.net`

#### 4. Network Security

```bash
# Only bind to localhost
python web/server.py --host 127.0.0.1

# Use firewall to restrict access
# Windows
netsh advfirewall firewall add rule name="ZordCoder" dir=in action=allow protocol=TCP localport=8000

# Linux
sudo ufw allow 8000/tcp
```

### Comparison Table

| Feature | ngrok | Cloudflare | Tailscale |
|---------|-------|------------|-----------|
| **Free tier** | Yes | Yes | Yes |
| **Account required** | Yes | No (quick) | Yes |
| **Custom domain** | $8/mo | Free | Free (Funnel) |
| **Bandwidth limit** | No | No | No |
| **Persistent URL** | Paid | Yes | Yes |
| **Best for** | Quick testing | Production | Team access |

---

## 7. Frontend Deployment (Vercel)

### Overview

Deploy the Next.js frontend to Vercel for a complete web application.

### Step-by-Step Instructions

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Login

```bash
vercel login
```

#### Step 3: Configure Environment

Create `vercel.json` in `web/` directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "BACKEND_URL": "https://your-backend-url.com"
  }
}
```

#### Step 4: Deploy

**From `web/` directory:**

```bash
cd web
vercel
```

**Or deploy from root:**

```bash
vercel --cwd web
```

### Environment Variables Setup

#### Via Vercel Dashboard

1. Go to Project → Settings → Environment Variables
2. Add:
   - `BACKEND_URL`: Your backend API URL
   - `NEXT_PUBLIC_API_URL`: Public API URL (optional)

#### Via CLI

```bash
vercel env add BACKEND_URL
# Enter value when prompted
```

#### Via vercel.json

```json
{
  "env": {
    "BACKEND_URL": "https://zordcoder-api.onrender.com"
  }
}
```

### Connecting to Backend

#### Option 1: Direct Backend URL

```typescript
// web/src/lib/api.ts
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function generateCode(prompt: string, options = {}) {
  const response = await fetch(`${BACKEND_URL}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, ...options })
  });
  return response.json();
}
```

#### Option 2: Via Next.js API Route

```typescript
// web/src/app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  const response = await fetch(`${BACKEND_URL}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  
  const data = await response.json();
  return NextResponse.json(data);
}
```

### Custom Domain Setup

1. Go to Project → Settings → Domains
2. Add your domain (e.g., `zordcoder.yourdomain.com`)
3. Configure DNS:
   - A record: `76.76.21.21`
   - Or CNAME: `cname.vercel-dns.com`

### Production Checklist

- [ ] Set `BACKEND_URL` environment variable
- [ ] Configure CORS on backend to allow Vercel domain
- [ ] Enable HTTPS (automatic on Vercel)
- [ ] Set up custom domain (optional)
- [ ] Configure build settings if needed

### Vercel Pricing

| Plan | Price | Best For |
|------|-------|----------|
| Hobby | Free | Personal projects |
| Pro | $20/user/mo | Team projects |
| Enterprise | Custom | Large teams |

---

## 8. Architecture Diagrams

### Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ZORD CODER ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │    END USERS    │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
           │  Web Browser  │  │  CLI Client   │  │  API Client   │
           └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
                   │                  │                  │
                   ▼                  │                  │
    ┌──────────────────────────┐      │                  │
    │    NEXT.JS FRONTEND      │      │                  │
    │  ┌────────────────────┐  │      │                  │
    │  │   React Components │  │      │                  │
    │  │   - Chat UI        │  │      │                  │
    │  │   - Settings Panel │  │      │                  │
    │  │   - Usage Tracker  │  │      │                  │
    │  └─────────┬──────────┘  │      │                  │
    │            │             │      │                  │
    │  ┌─────────▼──────────┐  │      │                  │
    │  │   API Routes       │  │      │                  │
    │  │   /api/chat        │  │      │                  │
    │  └─────────┬──────────┘  │      │                  │
    └────────────┼─────────────┘      │                  │
                 │                    │                  │
                 └────────────────────┼──────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │         PYTHON BACKEND              │
                    │  ┌───────────────────────────────┐  │
                    │  │      web/server.py            │  │
                    │  │  - FastAPI/HTTP Server        │  │
                    │  │  - Usage Tracking             │  │
                    │  │  - CORS Handling              │  │
                    │  └───────────────┬───────────────┘  │
                    │                  │                  │
                    │  ┌───────────────▼───────────────┐  │
                    │  │      src/zord_core.py         │  │
                    │  │  - Model Management           │  │
                    │  │  - Prompt Formatting          │  │
                    │  │  - Response Generation        │  │
                    │  └───────────────┬───────────────┘  │
                    │                  │                  │
                    │  ┌───────────────▼───────────────┐  │
                    │  │    llama-cpp-python           │  │
                    │  │  - GGUF Inference             │  │
                    │  │  - CPU/GPU Support            │  │
                    │  └───────────────┬───────────────┘  │
                    └──────────────────┼──────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │         GGUF MODEL FILE             │
                    │  zordcoder-v1-q4_k_m.gguf (~833MB)  │
                    │  - DeepSeek Coder 1.3B Quantized    │
                    └─────────────────────────────────────┘
```

### Deployment Architecture Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT ARCHITECTURES                                 │
└─────────────────────────────────────────────────────────────────────────────┘

HUGGINGFACE SPACES
─────────────────────────────────
┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Client    │────▶│  HF Space (Docker)  │────▶│  GGUF Model     │
└─────────────┘     │  - Python 3.10      │     │  (Downloaded)   │
                    │  - 16GB RAM         │     └─────────────────┘
                    │  - Port 7860        │
                    └─────────────────────┘


RENDER
─────────────────────────────────
┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Client    │────▶│  Render Container   │────▶│  Persistent     │
└─────────────┘     │  - Docker Runtime   │     │  Disk (Model)   │
                    │  - Auto SSL         │     └─────────────────┘
                    │  - Health Checks    │
                    └─────────────────────┘


FLY.IO
─────────────────────────────────
┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Client    │────▶│  Fly.io Machine     │────▶│  Volume         │
└─────────────┘     │  - GPU/CPU Options  │     │  (Model Cache)  │
                    │  - Auto Scale       │     └─────────────────┘
                    │  - Global Regions   │
                    └─────────────────────┘


LOCAL + TUNNEL
─────────────────────────────────
┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Client    │────▶│  Tunnel Service     │────▶│  Local Machine  │
└─────────────┘     │  - ngrok            │     │  - Server       │
                    │  - Cloudflare       │     │  - Model        │
                    │  - Tailscale        │     └─────────────────┘
                    └─────────────────────┘


FULL STACK (Vercel + Backend)
─────────────────────────────────
┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Client    │────▶│  Vercel (Frontend)  │     │  Render/Fly.io  │
└─────────────┘     │  - Next.js          │────▶│  (Backend API)  │
                    │  - Edge Network     │     │  - Model        │
                    └─────────────────────┘     └─────────────────┘
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          REQUEST FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────┘

User Input: "Write a Python hello world"
                    │
                    ▼
┌─────────────────────────────────────┐
│  1. FRONTEND (Next.js)              │
│  ┌─────────────────────────────────┐│
│  │ User types message              ││
│  │ → Component state update        ││
│  │ → API call initiated            ││
│  └─────────────────────────────────┘│
└───────────────┬─────────────────────┘
                │ POST /api/chat
                ▼
┌─────────────────────────────────────┐
│  2. API ROUTE (Next.js)             │
│  ┌─────────────────────────────────┐│
│  │ Receive request                 ││
│  │ → Validate input                ││
│  │ → Forward to backend            ││
│  └─────────────────────────────────┘│
└───────────────┬─────────────────────┘
                │ POST /generate
                ▼
┌─────────────────────────────────────┐
│  3. BACKEND (server.py)             │
│  ┌─────────────────────────────────┐│
│  │ Check rate limits               ││
│  │ → Format prompt (Llama 3 style) ││
│  │ → Call zord_core.generate()     ││
│  └─────────────────────────────────┘│
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  4. INFERENCE (zord_core.py)        │
│  ┌─────────────────────────────────┐│
│  │ Load model if needed            ││
│  │ → Create Llama instance         ││
│  │ → Generate tokens               ││
│  │ → Stream or return response     ││
│  └─────────────────────────────────┘│
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  5. RESPONSE                        │
│  ┌─────────────────────────────────┐│
│  │ {                               ││
│  │   "response": "print('Hello!')",││
│  │   "tokens_generated": 15,       ││
│  │   "model": "ZordCoder-v1"       ││
│  │ }                               ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

---

## 9. Cost Comparison

### Monthly Cost Estimates

| Usage Level | HuggingFace | Render | Fly.io (CPU) | Fly.io (GPU) | Local |
|-------------|-------------|--------|--------------|--------------|-------|
| **Testing** (5 hrs/wk) | Free | Free | ~$1 | ~$10 | Free |
| **Light** (2 hrs/day) | Free | Free | ~$3 | ~$30 | Free |
| **Moderate** (8 hrs/day) | Free | $7 | ~$15 | ~$240 | Free* |
| **Heavy** (24/7) | Free** | $25 | ~$50 | ~$720 | Free* |

*Requires your own hardware
**Subject to usage limits

### Detailed Cost Breakdown

#### HuggingFace Spaces

| Item | Cost |
|------|------|
| CPU Space | Free |
| GPU Space | $0.60/hour |
| Storage | Free (ephemeral) |
| Custom domain | Free |
| **Total (CPU)** | **$0/month** |

#### Render

| Plan | RAM | Cost/month |
|------|-----|------------|
| Free | 512MB | $0 |
| Starter | 512MB | $7 |
| Standard | 2GB | $25 |
| Pro | 4GB | $85 |
| Pro Plus | 8GB | $170 |

#### Fly.io

| Resource | Cost |
|----------|------|
| VM (shared-cpu-1x) | $1.94/month |
| VM (shared-cpu-2x) | $3.89/month |
| VM (performance-2x) | $15.56/month |
| Volume (1GB) | $0.15/month |
| L4 GPU | $0.50/hour |
| A100 40GB GPU | $2.50/hour |
| A100 80GB GPU | $4.00/hour |
| Bandwidth | $0.02/GB |

#### Vercel (Frontend)

| Plan | Cost/month |
|------|------------|
| Hobby | Free |
| Pro | $20/user |
| Enterprise | Custom |

### Cost Optimization Strategies

#### 1. Use Scale-to-Zero (Fly.io)

```
┌─────────────────────────────────────┐
│  Traditional Server (24/7)          │
│  ────────────────────────────────   │
│  ████████████████████████████████   │  ← Always paying
│                                     │
│  Scale-to-Zero                      │
│  ────────────────────────────────   │
│  ████░░░░░░░░░░░░░░░░░░░░░░░████    │  ← Only pay for usage
│       ▲                   ▲         │
│       │                   │         │
│    Request            Request       │
└─────────────────────────────────────┘

Savings: Up to 80% on low-traffic apps
```

#### 2. Use Smaller Models

| Model | Size | Quality | RAM Needed | Cost Impact |
|-------|------|---------|------------|-------------|
| Q8_0 | ~1.4GB | Best | 4GB | Higher |
| Q5_K_M | ~900MB | Good | 3GB | Medium |
| Q4_K_M | ~833MB | Good | 2GB | Lower |
| Q3_K_M | ~700MB | Fair | 2GB | Lowest |

#### 3. Optimize Context Length

```bash
# Lower context = less memory = cheaper instances
export ZORD_N_CTX=1024  # Instead of 2048
```

---

## 10. Troubleshooting

### Common Issues & Solutions

#### Model Download Issues

**Problem:** Model fails to download
```
Error: Failed to download model from HuggingFace
```

**Solutions:**
```bash
# Manual download
pip install huggingface-hub
python -c "from huggingface_hub import hf_hub_download; \
  hf_hub_download('TheBloke/deepseek-coder-1.3b-instruct-GGUF', \
  'deepseek-coder-1.3b-instruct-q4_k_m.gguf', local_dir='./models')"

# Set HF token if rate limited
export HF_TOKEN=your_token_here
```

#### Memory Issues

**Problem:** Out of memory error
```
RuntimeError: CUDA out of memory / malloc failed
```

**Solutions:**
```bash
# Reduce context length
export ZORD_N_CTX=1024

# Use smaller quantization
# Download Q3_K_M instead of Q4_K_M

# Reduce batch size
export ZORD_N_BATCH=256

# For GPU, reduce layers
export ZORD_N_GPU_LAYERS=20
```

#### Cold Start Issues

**Problem:** Slow first response

**Solutions:**

For HuggingFace:
- Use `pinned: true` in README metadata (paid feature)
- Accept cold start as normal behavior

For Render:
- Upgrade to Starter plan ($7/mo) for no cold start
- Use a cron job to ping every 10 minutes

For Fly.io:
```bash
# Set minimum machines running
fly scale count 1 --region ord
```

#### Connection Issues

**Problem:** "Backend not connected" in web UI

**Solutions:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check environment variable
echo $BACKEND_URL

# Update .env file
echo "BACKEND_URL=http://localhost:8000" > web/.env
```

#### CORS Errors

**Problem:** CORS policy blocking requests

**Solution:** Update server to allow your domain:
```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://your-frontend.vercel.app"])
```

#### Port Conflicts

**Problem:** "Address already in use"

**Solutions:**
```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000

# Kill process or use different port
python web/server.py --port 8001
```

#### Docker Build Failures

**Problem:** Docker build fails on Render/Fly.io

**Solutions:**
```bash
# Test locally first
docker build -f deploy/render/Dockerfile -t zordcoder .

# Run locally
docker run -p 8000:8000 zordcoder

# Check for missing files
docker run -it zordcoder /bin/bash
ls -la /app
```

#### Slow Inference

**Problem:** Very slow token generation

**Solutions:**
```bash
# Increase thread count
export ZORD_N_THREADS=8

# Enable GPU (if available)
export ZORD_N_GPU_LAYERS=35

# Use smaller model
# Q4_K_M instead of Q8

# Check CPU usage
top -p $(pgrep -f server.py)
```

### Platform-Specific Issues

#### HuggingFace Spaces

| Issue | Solution |
|-------|----------|
| Space sleeps | Upgrade to GPU or use webhook pings |
| Model not found | Check MODEL_PATH in Dockerfile |
| Build timeout | Reduce dependencies, use smaller base image |

#### Render

| Issue | Solution |
|-------|----------|
| Memory limit exceeded | Upgrade plan or reduce model size |
| Health check fails | Increase grace period in render.yaml |
| Disk full | Clear model cache, use persistent disk |

#### Fly.io

| Issue | Solution |
|-------|----------|
| Machine won't start | Check logs: `fly logs` |
| Volume not mounted | Verify volume name matches fly.toml |
| GPU unavailable | Check region availability: `fly platform vm-sizes` |

#### Vercel

| Issue | Solution |
|-------|----------|
| Build fails | Check Node.js version, update dependencies |
| API timeout | Use edge functions for longer timeouts |
| Env vars missing | Add in dashboard or via CLI |

### Getting Help

1. **Check Logs:**
   ```bash
   # HuggingFace: View in "Logs" tab
   # Render: Dashboard → Service → Logs
   # Fly.io: fly logs
   # Vercel: vercel logs
   ```

2. **Debug Mode:**
   ```bash
   # Enable verbose logging
   export ZORD_DEBUG=1
   python web/server.py --debug
   ```

3. **Community Support:**
   - GitHub Issues: https://github.com/sajadkoder/zordcoder/issues
   - HuggingFace Discord
   - Render Discord
   - Fly.io Community

---

## Quick Reference

### Essential Commands

```bash
# Local development
python web/server.py                    # Start backend
cd web && npm run dev                   # Start frontend

# HuggingFace
git push hf main                        # Deploy to HF

# Render
git push render main                    # Deploy to Render

# Fly.io
fly deploy                              # Deploy to Fly.io
fly logs                                # View logs
fly ssh console                         # SSH into machine

# Vercel
vercel                                  # Deploy to Vercel
vercel --prod                           # Production deploy
vercel logs                             # View logs

# Tunnels
ngrok http 8000                         # ngrok tunnel
cloudflared tunnel --url http://localhost:8000  # Cloudflare quick tunnel
tailscale serve http://localhost:8000   # Tailscale serve
```

### Environment Variables Summary

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORD_MODEL_PATH` | models/zordcoder-v1-q4_k_m.gguf | Model file path |
| `ZORD_N_THREADS` | 4 | CPU threads |
| `ZORD_N_GPU_LAYERS` | 0 | GPU layers (0=CPU only) |
| `ZORD_N_CTX` | 2048 | Context length |
| `ZORD_N_BATCH` | 512 | Batch size |
| `BACKEND_URL` | http://localhost:8000 | Backend API URL |
| `PORT` | 8000 | Server port |

---

<p align="center">
  <strong>Zord Coder v1 - Deployment Guide</strong><br>
  Built by SaJad
</p>
