# 🔐 Darwin API Key Authentication

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Author:** Darwin Team

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Key Format](#api-key-format)
4. [Implementation Details](#implementation-details)
5. [Setup Guide](#setup-guide)
6. [Usage Examples](#usage-examples)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Darwin API uses a **single API key** authentication system to provide secure access to all database operations. This approach:

- ✅ Hides MongoDB credentials from client applications
- ✅ Provides a single point of access control
- ✅ Allows easy revocation if compromised
- ✅ Works in both local development and production environments
- ✅ Enables team collaboration without sharing sensitive credentials

### What Gets Protected

| Resource | Protected By |
|----------|--------------|
| MongoDB Atlas | API Key (indirect access via API) |
| Signals data | API Key |
| UX Issues data | API Key |
| Pull Requests data | API Key |
| Darwin Pipeline triggers | API Key |
| All CRUD operations | API Key |

### What Each Component Knows

| Component | MongoDB URI | API Key | API URL |
|-----------|-------------|---------|---------|
| Darwin API (FastAPI) | ✅ Yes | ✅ Validates | N/A |
| NitroStack MCP Server | ❌ No | ✅ Uses | ✅ Yes |
| NitroStudio | ❌ No | ❌ No | ❌ No |
| Team Members | ❌ No | ✅ Shared | ✅ Yes |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│                                                                          │
│  ┌─────────────────┐         ┌─────────────────┐                        │
│  │  NitroStudio    │         │  Future Clients │                        │
│  │  (Desktop App)  │         │  (Web, Mobile)  │                        │
│  └────────┬────────┘         └────────┬────────┘                        │
│           │                           │                                  │
│           │ MCP Protocol              │                                  │
│           ▼                           │                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              NitroStack MCP Server (TypeScript)                  │    │
│  │                                                                  │    │
│  │  .env:                                                           │    │
│  │  ┌─────────────────────────────────────────────────────────┐    │    │
│  │  │  DARWIN_API_URL=http://localhost:8000                   │    │    │
│  │  │  DARWIN_API_KEY=darwin_sk_xxxxxxxxxxxxxxxxxxxxxxxx      │    │    │
│  │  └─────────────────────────────────────────────────────────┘    │    │
│  │                                                                  │    │
│  │  All requests include:                                           │    │
│  │  Authorization: Bearer darwin_sk_xxxxxxxxxxxxxxxxxxxxxxxx        │    │
│  │                                                                  │    │
│  └──────────────────────────────┬───────────────────────────────────┘    │
│                                 │                                        │
└─────────────────────────────────┼────────────────────────────────────────┘
                                  │
                                  │ HTTPS / HTTP
                                  │ + Authorization Header
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Darwin API (FastAPI)                          │    │
│  │                    http://localhost:8000                         │    │
│  │                                                                  │    │
│  │  ┌─────────────────────────────────────────────────────────┐    │    │
│  │  │  AUTH MIDDLEWARE                                         │    │    │
│  │  │  ─────────────────────────────────────────────────────── │    │    │
│  │  │  1. Extract Authorization header                         │    │    │
│  │  │  2. Validate "Bearer <api_key>" format                   │    │    │
│  │  │  3. Compare with stored DARWIN_API_KEY                   │    │    │
│  │  │  4. Return 401 if invalid, continue if valid             │    │    │
│  │  └─────────────────────────────────────────────────────────┘    │    │
│  │                           │                                      │    │
│  │                           ▼                                      │    │
│  │  ┌─────────────────────────────────────────────────────────┐    │    │
│  │  │  PROTECTED ENDPOINTS                                     │    │    │
│  │  │  ─────────────────────────────────────────────────────── │    │    │
│  │  │  GET  /api/signals           - Fetch signals             │    │    │
│  │  │  GET  /api/ux-issues         - Fetch UX issues           │    │    │
│  │  │  POST /api/ux-issues/:id/approve - Approve fix           │    │    │
│  │  │  POST /api/ux-issues/:id/reject  - Reject fix            │    │    │
│  │  │  GET  /api/pull-requests     - Fetch PRs                 │    │    │
│  │  │  POST /api/darwin/run        - Trigger pipeline          │    │    │
│  │  │  GET  /api/stats             - Get statistics            │    │    │
│  │  └─────────────────────────────────────────────────────────┘    │    │
│  │                           │                                      │    │
│  └───────────────────────────┼──────────────────────────────────────┘    │
│                              │                                           │
└──────────────────────────────┼───────────────────────────────────────────┘
                               │
                               │ MongoDB Driver
                               │ (Credentials stored in API only)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            DATABASE LAYER                                │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    MongoDB Atlas (Cloud)                         │    │
│  │         mongodb+srv://user:pass@cluster0.mongodb.net            │    │
│  │                                                                  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ signals  │ │ux_issues │ │   PRs    │ │ insights │           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Key Format

### Structure

```
darwin_sk_<32_character_random_string>
```

### Components

| Part | Description | Example |
|------|-------------|---------|
| `darwin` | Product identifier | `darwin` |
| `sk` | Secret key indicator | `sk` |
| `_` | Separator | `_` |
| `<random>` | 32-char alphanumeric string | `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6` |

### Example Keys

```bash
# Development key
darwin_sk_dev_a1b2c3d4e5f6g7h8i9j0k1l2m3n4

# Production key
darwin_sk_prod_x9y8z7w6v5u4t3s2r1q0p9o8n7m6

# Team-specific key
darwin_sk_team_heena_2026_feb_hackathon
```

### Generating a New Key

```python
import secrets
import string

def generate_api_key(prefix="darwin_sk"):
    """Generate a secure API key"""
    chars = string.ascii_lowercase + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(32))
    return f"{prefix}_{random_part}"

# Usage
new_key = generate_api_key()
print(new_key)  # darwin_sk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

## Implementation Details

### Darwin API Side (Python/FastAPI)

#### 1. Environment Configuration

```env
# darwin-multi-agent/.env

# API Key for authentication
DARWIN_API_KEY=darwin_sk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# MongoDB (only API knows this)
MONGODB_URI=mongodb+srv://user:password@cluster0.mongodb.net/
MONGODB_DATABASE=darwin

# Other secrets (only API knows these)
POSTHOG_API_KEY=phx_xxxxx
GITHUB_TOKEN=ghp_xxxxx
GEMINI_API_KEY=xxxxx
```

#### 2. Authentication Middleware

```python
# api/middleware/auth.py

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Load API key from environment
DARWIN_API_KEY = os.getenv("DARWIN_API_KEY")

if not DARWIN_API_KEY:
    raise ValueError("DARWIN_API_KEY environment variable is required")

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the API key from the Authorization header.
    
    Expected format: Authorization: Bearer darwin_sk_xxxxx
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use 'Bearer'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if credentials.credentials != DARWIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials


def get_api_key_dependency():
    """Return the API key verification dependency"""
    return Depends(verify_api_key)
```

#### 3. Apply to Routes

```python
# api/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.middleware.auth import verify_api_key
from api.routes import signals, ux_issues, pull_requests, darwin, stats

app = FastAPI(
    title="Darwin API",
    description="REST API for Darwin Multi-Agent System",
    version="1.0.0",
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public endpoints (no auth required)
@app.get("/")
def root():
    return {"message": "Darwin API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Protected endpoints (auth required)
app.include_router(
    signals.router,
    prefix="/api/signals",
    tags=["Signals"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    ux_issues.router,
    prefix="/api/ux-issues",
    tags=["UX Issues"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    pull_requests.router,
    prefix="/api/pull-requests",
    tags=["Pull Requests"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    darwin.router,
    prefix="/api/darwin",
    tags=["Darwin Pipeline"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    stats.router,
    prefix="/api/stats",
    tags=["Statistics"],
    dependencies=[Depends(verify_api_key)]
)
```

### NitroStack Side (TypeScript)

#### 1. Environment Configuration

```env
# darwin-acceleration-engine/.env

# Darwin API connection
DARWIN_API_URL=http://localhost:8000
DARWIN_API_KEY=darwin_sk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

#### 2. API Client

```typescript
// src/api/darwin-client.ts

const API_URL = process.env.DARWIN_API_URL || 'http://localhost:8000';
const API_KEY = process.env.DARWIN_API_KEY;

if (!API_KEY) {
  throw new Error('DARWIN_API_KEY environment variable is required');
}

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * Make an authenticated request to the Darwin API
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (response.status === 401) {
      return { error: 'Invalid API key. Check your DARWIN_API_KEY.' };
    }

    if (!response.ok) {
      return { error: `API Error: ${response.status} ${response.statusText}` };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: `Network error: ${error.message}` };
  }
}

/**
 * Darwin API Client
 */
export const darwinClient = {
  // Signals
  getSignals: (filters?: { severity?: string; processed?: boolean }) =>
    apiRequest<{ signals: any[]; count: number }>('/api/signals', {
      method: 'GET',
    }),

  getSignalById: (id: string) =>
    apiRequest<any>(`/api/signals/${id}`),

  // UX Issues
  getUxIssues: (filters?: { status?: string }) =>
    apiRequest<{ issues: any[]; count: number }>('/api/ux-issues'),

  getUxIssueById: (id: string) =>
    apiRequest<any>(`/api/ux-issues/${id}`),

  approveIssue: (id: string) =>
    apiRequest<{ success: boolean; message: string }>(
      `/api/ux-issues/${id}/approve`,
      { method: 'POST' }
    ),

  rejectIssue: (id: string, reason?: string) =>
    apiRequest<{ success: boolean; message: string }>(
      `/api/ux-issues/${id}/reject`,
      {
        method: 'POST',
        body: JSON.stringify({ reason }),
      }
    ),

  // Pull Requests
  getPullRequests: () =>
    apiRequest<{ pull_requests: any[]; count: number }>('/api/pull-requests'),

  // Darwin Pipeline
  triggerDarwin: (mode: 'analyze' | 'engineer' | 'full') =>
    apiRequest<{ success: boolean; output: string }>(
      '/api/darwin/run',
      {
        method: 'POST',
        body: JSON.stringify({ mode }),
      }
    ),

  // Statistics
  getStats: () =>
    apiRequest<{
      signals: number;
      ux_issues: number;
      pull_requests: number;
      insights: number;
    }>('/api/stats'),
};

export default darwinClient;
```

#### 3. Using the Client in Tools

```typescript
// src/tools/get-signals.ts

import { Tool } from '@anthropic-ai/mcp';
import { darwinClient } from '../api/darwin-client';

export const getSignalsTool = new Tool({
  name: 'get_signals',
  description: 'Fetch UX friction signals from Darwin database',
  
  parameters: {
    severity: {
      type: 'string',
      enum: ['critical', 'high', 'medium', 'low'],
      description: 'Filter by severity level',
      required: false,
    },
  },

  async execute({ severity }) {
    const response = await darwinClient.getSignals({ severity });
    
    if (response.error) {
      return { error: response.error };
    }

    return {
      widget: 'SignalsDashboard',
      data: response.data,
    };
  },
});
```

---

## Setup Guide

### For Main Developer (Heena)

```bash
# 1. Generate API Key
cd darwin-multi-agent
python -c "
import secrets
import string
chars = string.ascii_lowercase + string.digits
key = 'darwin_sk_' + ''.join(secrets.choice(chars) for _ in range(32))
print(f'Your API Key: {key}')
print(f'Add to .env: DARWIN_API_KEY={key}')
"

# 2. Add to darwin-multi-agent/.env
echo "DARWIN_API_KEY=darwin_sk_your_generated_key" >> .env

# 3. Start Darwin API
python scripts/run_api.py

# 4. Test API
curl http://localhost:8000/health
curl -H "Authorization: Bearer darwin_sk_your_key" http://localhost:8000/api/stats
```

### For Team Members (Anand)

```bash
# 1. Clone repositories
git clone https://github.com/heenakousarm-cloud/darwin-multi-agent.git
git clone https://github.com/heenakousarm-cloud/darwin-acceleration-engine.git

# 2. Setup Darwin API
cd darwin-multi-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Create .env (get values from team lead)
cat > .env << 'EOF'
DARWIN_API_KEY=darwin_sk_shared_team_key
MONGODB_URI=mongodb+srv://user:pass@cluster0.mongodb.net/
MONGODB_DATABASE=darwin
EOF

# 4. Start Darwin API
python scripts/run_api.py

# 5. In another terminal - Setup NitroStack
cd darwin-acceleration-engine
npm install

# 6. Create .env
cat > .env << 'EOF'
DARWIN_API_URL=http://localhost:8000
DARWIN_API_KEY=darwin_sk_shared_team_key
EOF

# 7. Start NitroStack
npm run dev

# 8. Open NitroStudio and connect
```

---

## Usage Examples

### cURL Examples

```bash
# Health check (no auth)
curl http://localhost:8000/health

# Get all signals (with auth)
curl -H "Authorization: Bearer darwin_sk_xxxxx" \
     http://localhost:8000/api/signals

# Get high severity signals
curl -H "Authorization: Bearer darwin_sk_xxxxx" \
     "http://localhost:8000/api/signals?severity=high"

# Get UX issues
curl -H "Authorization: Bearer darwin_sk_xxxxx" \
     http://localhost:8000/api/ux-issues

# Approve an issue
curl -X POST \
     -H "Authorization: Bearer darwin_sk_xxxxx" \
     http://localhost:8000/api/ux-issues/65abc123def456/approve

# Trigger Darwin pipeline
curl -X POST \
     -H "Authorization: Bearer darwin_sk_xxxxx" \
     -H "Content-Type: application/json" \
     -d '{"mode": "analyze"}' \
     http://localhost:8000/api/darwin/run

# Get statistics
curl -H "Authorization: Bearer darwin_sk_xxxxx" \
     http://localhost:8000/api/stats
```

### JavaScript/TypeScript Examples

```typescript
// Using fetch
const response = await fetch('http://localhost:8000/api/signals', {
  headers: {
    'Authorization': 'Bearer darwin_sk_xxxxx',
  },
});
const data = await response.json();

// Using the Darwin client
import { darwinClient } from './api/darwin-client';

const signals = await darwinClient.getSignals();
const issues = await darwinClient.getUxIssues({ status: 'diagnosed' });
await darwinClient.approveIssue('65abc123def456');
```

### Python Examples

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "darwin_sk_xxxxx"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Get signals
response = requests.get(f"{API_URL}/api/signals", headers=headers)
signals = response.json()

# Approve issue
response = requests.post(
    f"{API_URL}/api/ux-issues/65abc123def456/approve",
    headers=headers
)
```

---

## Security Best Practices

### DO ✅

1. **Store API key in environment variables**
   ```bash
   export DARWIN_API_KEY=darwin_sk_xxxxx
   ```

2. **Use .env files (gitignored)**
   ```env
   # .env (not committed to git)
   DARWIN_API_KEY=darwin_sk_xxxxx
   ```

3. **Rotate keys periodically**
   - Generate new key
   - Update all .env files
   - Restart services

4. **Use HTTPS in production**
   ```env
   DARWIN_API_URL=https://darwin-api.yourserver.com
   ```

5. **Log API access for auditing**
   ```python
   @app.middleware("http")
   async def log_requests(request: Request, call_next):
       logger.info(f"API Request: {request.method} {request.url.path}")
       return await call_next(request)
   ```

### DON'T ❌

1. **Never commit API keys to git**
   ```bash
   # .gitignore
   .env
   *.env
   .env.*
   ```

2. **Never hardcode keys in source code**
   ```python
   # BAD
   API_KEY = "darwin_sk_xxxxx"
   
   # GOOD
   API_KEY = os.getenv("DARWIN_API_KEY")
   ```

3. **Never share keys in chat/email**
   - Use secure channels (1Password, LastPass, etc.)

4. **Never use the same key for dev and prod**
   ```env
   # Development
   DARWIN_API_KEY=darwin_sk_dev_xxxxx
   
   # Production
   DARWIN_API_KEY=darwin_sk_prod_xxxxx
   ```

---

## Troubleshooting

### Error: 401 Unauthorized

**Cause:** Invalid or missing API key

**Solution:**
```bash
# Check if API key is set
echo $DARWIN_API_KEY

# Verify key matches
# In Darwin API .env
DARWIN_API_KEY=darwin_sk_abc123

# In NitroStack .env (must match!)
DARWIN_API_KEY=darwin_sk_abc123
```

### Error: Connection Refused

**Cause:** Darwin API not running

**Solution:**
```bash
# Start Darwin API
cd darwin-multi-agent
source venv/bin/activate
python scripts/run_api.py

# Verify it's running
curl http://localhost:8000/health
```

### Error: CORS Error (in browser)

**Cause:** CORS not configured

**Solution:**
```python
# In api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error: Network Error

**Cause:** Wrong API URL

**Solution:**
```bash
# Check NitroStack .env
DARWIN_API_URL=http://localhost:8000  # Not https for local

# Test connection
curl http://localhost:8000/health
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                 DARWIN API KEY QUICK REFERENCE              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  API Key Format:                                            │
│  darwin_sk_<32_random_characters>                           │
│                                                             │
│  Header Format:                                             │
│  Authorization: Bearer darwin_sk_xxxxx                      │
│                                                             │
│  Darwin API .env:                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DARWIN_API_KEY=darwin_sk_xxxxx                      │   │
│  │ MONGODB_URI=mongodb+srv://...                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  NitroStack .env:                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DARWIN_API_URL=http://localhost:8000                │   │
│  │ DARWIN_API_KEY=darwin_sk_xxxxx                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Test Commands:                                             │
│  curl http://localhost:8000/health                          │
│  curl -H "Authorization: Bearer darwin_sk_xxxxx" \          │
│       http://localhost:8000/api/stats                       │
│                                                             │
│  Public Endpoints (no auth):                                │
│  GET  /           - API info                                │
│  GET  /health     - Health check                            │
│  GET  /docs       - Swagger documentation                   │
│                                                             │
│  Protected Endpoints (auth required):                       │
│  GET  /api/signals         - Fetch signals                  │
│  GET  /api/ux-issues       - Fetch UX issues                │
│  POST /api/ux-issues/:id/approve - Approve fix              │
│  POST /api/ux-issues/:id/reject  - Reject fix               │
│  GET  /api/pull-requests   - Fetch PRs                      │
│  POST /api/darwin/run      - Trigger pipeline               │
│  GET  /api/stats           - Get statistics                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 7, 2026 | Initial documentation |

---

**Questions?** Contact the Darwin team or refer to the main project documentation.
