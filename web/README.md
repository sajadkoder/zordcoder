# Zord Coder Web

Modern Next.js web interface for Zord Coder AI Assistant.

## Quick Start

### Option 1: Run Both Frontend & Backend

```bash
# 1. Install web dependencies
cd web
npm install

# 2. Start Python backend (in one terminal)
cd ..
python web/server.py

# 3. Start Next.js frontend (in another terminal)
cd web
npm run dev
```

Visit: http://localhost:3000

### Option 2: Frontend Only (Demo Mode)

```bash
cd web
npm install
npm run dev
```

The frontend will work in demo mode. Connect to a backend for real AI responses.

## Environment Variables

Create `.env.local`:

```env
BACKEND_URL=http://localhost:8000
```

## Deployment

### Vercel (Recommended)

```bash
npm i -g vercel
vercel
```

### Build for Production

```bash
npm run build
npm start
```

## Features

- 💬 Modern chat interface
- 🎨 Beautiful dark/light themes
- 📱 Responsive design
- ⚡ Fast and smooth animations
- 🔒 Usage limits (50 msg/day, 50K tokens/day)
- 🧠 Reasoning mode
- ⚙️ Customizable settings

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion
- Python (Backend)

## Project Structure

```
web/
├── src/
│   ├── app/
│   │   ├── api/chat/    # API routes
│   │   ├── globals.css    # Global styles
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Main page
│   └── components/        # React components
├── server.py             # Python backend
├── package.json
├── tailwind.config.js
└── tsconfig.json
```
