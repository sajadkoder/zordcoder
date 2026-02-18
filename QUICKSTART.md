# Quick Start Guide for Zord Coder

## Windows Setup

### Method 1: Using Batch Files (Recommended)

The project includes batch files that automatically find Python with llama-cpp-python:

```powershell
# Start the API server
.\start_server.bat

# Run the CLI
.\run_cli.bat --interactive

# Test the system
C:\Users\abdul\miniconda3\python.exe test_system.py
```

### Method 2: Using Miniconda Python Directly

```powershell
# Start the API server
C:\Users\abdul\miniconda3\python.exe web\server.py

# Run the CLI
C:\Users\abdul\miniconda3\python.exe scripts\zord_cli.py --interactive
```

## Web Interface

1. Start the backend server:
```powershell
.\start_server.bat
```

2. In a new terminal, start the frontend:
```powershell
cd web
npm install
npm run dev
```

3. Visit http://localhost:3000

## API Endpoints

- GET / - Server info
- GET /health - Health check
- POST /generate - Generate response

### Example API Call

```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/generate' -Method Post -ContentType 'application/json' -Body '{"prompt":"Write hello world in Python","temperature":0.1,"max_tokens":100}'
```

## Troubleshooting

If you see "llama-cpp-python not installed":

1. Make sure you have miniconda installed
2. Or install llama-cpp-python: `pip install llama-cpp-python`
3. Use the provided batch files which auto-detect the correct Python
