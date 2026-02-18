# Vercel Deployment Guide

## Prerequisites

- GitHub account with repository access
- Vercel account (sign up at [vercel.com](https://vercel.com))
- Backend deployed and accessible

## Step 1: Connect GitHub Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Select **"Import Git Repository"**
4. Connect your GitHub account if not already connected
5. Select the `zordcoder/web` repository (or your fork)
6. Click **"Import"**

## Step 2: Configure Project Settings

1. **Framework Preset**: Next.js (auto-detected)
2. **Root Directory**: `web` (if repo contains multiple projects)
3. **Build Command**: `npm run build` (default)
4. **Output Directory**: `.next` (default)
5. **Install Command**: `npm install` (default)

## Step 3: Set Environment Variables

Click **"Environment Variables"** and add the following:

| Variable | Description | Example Values |
|----------|-------------|----------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | See backend options below |

### Backend URL Options

#### Local Development
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Hugging Face Spaces
```
NEXT_PUBLIC_API_URL=https://your-username-zordcoder-backend.hf.space
```

#### Render
```
NEXT_PUBLIC_API_URL=https://zordcoder-backend.onrender.com
```

#### Fly.io
```
NEXT_PUBLIC_API_URL=https://zordcoder-backend.fly.dev
```

## Step 4: Deploy

1. Review all settings
2. Click **"Deploy"**
3. Wait for build to complete (usually 1-3 minutes)
4. Your app will be live at `https://your-project.vercel.app`

## Step 5: Configure Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed
4. Wait for SSL certificate provisioning

## Environment-Specific Deployments

### Preview Deployments
Every pull request creates a preview deployment with a unique URL.

### Production Branch
- Default: `main` branch
- Change in **Settings** → **Git**

## Updating Environment Variables

1. Go to **Settings** → **Environment Variables**
2. Edit or add variables
3. Select which environments to apply to (Production, Preview, Development)
4. **Important**: Redeploy for changes to take effect
   - Go to **Deployments**
   - Click **"..."** on latest deployment
   - Select **"Redeploy"**

## Connecting to Different Backends

### Switching Backend URL

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Update `NEXT_PUBLIC_API_URL`
4. Redeploy the application

### Backend Requirements

Your backend must:
- Support CORS from your Vercel domain
- Be accessible via HTTPS (required for production)
- Have endpoints: `/api/chat`, `/api/health`, `/api/models`, `/api/stream`

### CORS Configuration for Backend

Add your Vercel domain to your backend's CORS settings:

```python
# FastAPI example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "https://your-custom-domain.com",
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Build Failures
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify Node.js version compatibility

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is running and accessible
- Ensure CORS is configured on backend
- Check browser console for CORS errors

### Environment Variables Not Working
- Variables prefixed with `NEXT_PUBLIC_` are exposed to browser
- Redeploy after changing environment variables
- Check variable names match exactly (case-sensitive)

## CLI Deployment (Alternative)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from web directory
cd web
vercel

# Deploy to production
vercel --prod
```

## Useful Commands

```bash
# View deployment logs
vercel logs [deployment-url]

# List deployments
vercel list

# Open project in browser
vercel open

# Pull environment variables locally
vercel env pull .env.local
```
