# Tunnel Setup Guide

This guide covers setting up different tunneling solutions for exposing your local server to the internet.

## Table of Contents

1. [ngrok](#ngrok)
2. [Cloudflare Tunnel](#cloudflare-tunnel)
3. [Tailscale](#tailscale)

---

## Quick Start

Run the local deployment script from the project root:

**Windows:**
```cmd
deploy\local\start_local.bat
```

**Linux/macOS:**
```bash
./deploy/local/start_local.sh
```

The script will:
1. Find Python with llama-cpp-python installed
2. Start the Zord Coder server (`web/server.py`) on port 8000
3. Prompt you to select a tunnel option

---

## ngrok

### Installation

**Windows:**
```powershell
# Using Chocolatey
choco install ngrok

# Or download from https://ngrok.com/download
# Extract and add to PATH
```

**macOS:**
```bash
brew install ngrok/ngrok/ngrok
```

**Linux:**
```bash
# Download from https://ngrok.com/download
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### Setup

1. Create a free account at [ngrok.com](https://ngrok.com)
2. Get your authtoken from the dashboard
3. Configure ngrok:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Usage

```bash
# Basic usage
ngrok http 8000

# With custom configuration
ngrok start --all

# With basic auth
ngrok http -auth="user:password" 8000
```

### Configuration File

Place `ngrok.yml` in:
- Windows: `%USERPROFILE%\.ngrok2\ngrok.yml`
- Linux/macOS: `~/.ngrok2/ngrok.yml`

---

## Cloudflare Tunnel

### Installation

**Windows:**
```powershell
# Using winget
winget install cloudflare.cloudflared

# Or download from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
```

**macOS:**
```bash
brew install cloudflared
```

**Linux:**
```bash
# Debian/Ubuntu
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

### Setup

1. Create a free Cloudflare account
2. Add a domain to Cloudflare (optional for quick tunnels)
3. Authenticate:

```bash
cloudflared tunnel login
```

### Usage

**Quick Tunnel (no account required):**
```bash
cloudflared tunnel --url http://localhost:8000
```

**Named Tunnel (with account):**
```bash
# Create tunnel
cloudflared tunnel create my-tunnel

# Route tunnel to domain
cloudflared tunnel route dns my-tunnel myapp.yourdomain.com

# Run tunnel
cloudflared tunnel run my-tunnel
```

### Configuration File

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /path/to/credentials.json

ingress:
  - hostname: myapp.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

---

## Tailscale

### Installation

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

### Setup

1. Create account at [tailscale.com](https://tailscale.com)
2. Authenticate:

```bash
tailscale up
```

### Usage

**Basic serve:**
```bash
# Serve on Tailscale network
tailscale serve http://localhost:8000

# Background mode
tailscale serve --bg http://localhost:8000

# With HTTPS
tailscale serve --bg --https=:443 http://localhost:8000
```

**Funnel (public internet access):**
```bash
# Enable funnel
tailscale funnel --bg --https=:443 http://localhost:8000
```

### Getting Your Tailscale URL

```bash
# Get Tailscale IP
tailscale ip -4

# Your URL will be
# https://<tailscale-ip> or https://<machine-name>.tailnet-name.ts.net
```

---

## Comparison

| Feature | ngrok | Cloudflare Tunnel | Tailscale |
|---------|-------|-------------------|-----------|
| Free tier | Yes (limited) | Yes | Yes |
| Custom domain | Paid | Yes | Yes (Funnel) |
| No account needed | No (for HTTP) | Yes | No |
| Speed | Fast | Fast | Fast |
| Security | Good | Excellent | Excellent |
| Best for | Quick testing | Production | Team access |

---

## Troubleshooting

### ngrok shows "ERR_NGROK_108"
Your authtoken is not configured. Run:
```bash
ngrok config add-authtoken YOUR_TOKEN
```

### Cloudflare Tunnel not connecting
Check your firewall and ensure cloudflared can access the internet.

### Tailscale not connecting
```bash
# Check status
tailscale status

# Restart
sudo tailscaled restart
```

### Port already in use
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000

# Linux/macOS:
lsof -i :8000
```

### Python not found with llama-cpp-python
The start_local scripts search for Python in:
- Miniconda (`~/miniconda3/python.exe` on Windows)
- Standard Python installations (C:\Python312, C:\Python311, C:\Python310)
- System default `python` command

Make sure llama-cpp-python is installed in one of these Python environments:
```bash
pip install llama-cpp-python
# or
conda install -c conda-forge llama-cpp-python
```
