# 🧬 Darwin - Final Implementation Roadmap

> **The Self-Evolving Product Engine**  
> *"Darwin doesn't just REPORT the weather. It FIXES the roof."*

**Last Updated:** February 7, 2026  
**Team:** heenakousarm-cloud, anands@wekancode.com

---

## 🆕 Latest Updates (Feb 7, 2026)

| Component | Status | Details |
|-----------|--------|---------|
| **Darwin Agents (Python)** | ✅ Complete | All 3 agents working |
| **MongoDB Atlas** | ✅ Complete | Cloud DB for team collaboration |
| **Darwin REST API** | ✅ Complete | FastAPI with API key auth |
| **NitroStack MCP** | ⬜ Next | Tools will call Darwin API |

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Tech Stack](#3-tech-stack)
4. [Credentials & Environment](#4-credentials--environment)
5. [Architecture](#5-architecture)
6. [Data Models](#6-data-models)
7. [**CrewAI Agents & Tools**](#7-crewai-agents--tools) ⭐ NEW
8. [**Darwin REST API**](#8-darwin-rest-api) ⭐ NEW
9. [Implementation Phases](#9-implementation-phases)
10. [Bug Injection (Luxora)](#10-bug-injection-luxora)
11. [Demo Flow](#11-demo-flow)
12. [Quick Start Guide](#12-quick-start-guide)

---

## 1. Project Overview

### 1.1 What is Darwin?

Darwin is an **Autonomous Growth Engineer** that:
- 🕵️ **Observes** user behavior via PostHog (rage clicks, drop-offs, errors)
- 🧠 **Analyzes** root causes using AI (Gemini)
- 📋 **Proposes** code fixes with confidence scores
- 👩‍💻 **Executes** via GitHub PRs (with human approval)

### 1.2 The Three Agents

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Watcher** 🕵️ | Detect friction signals | PostHog analytics | Signals in MongoDB |
| **Analyst** 🧠 | Diagnose root cause | Signals + Code | UX Issues in MongoDB |
| **Engineer** 👩‍💻 | Generate & deploy fix | Approved Issues | GitHub Pull Request |

### 1.3 Key Differentiator

```
Traditional Flow:  Analytics → PM reviews → Jira ticket → Sprint planning → Dev → PR → Deploy
                   (2-4 WEEKS)

Darwin Flow:       PostHog → Watcher → Analyst → Approve → Engineer → PR
                   (MINUTES)
```

---

## 2. Repository Structure

### 2.1 Three Separate Repositories

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THREE SEPARATE REPOSITORIES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  REPO 1: darwin-multi-agent/           REPO 2: darwin-acceleration-engine/  │
│  ────────────────────────────          ────────────────────────────────────  │
│  Language: Python 3.11+                Language: TypeScript                  │
│  Purpose: AI Agents + REST API         Purpose: NitroStack MCP Server        │
│  Status: ✅ COMPLETE                   Status: ⬜ TO BUILD                   │
│                                                                              │
│  /src/agents                           /src/tools (calls Darwin API)         │
│    ├── watcher.py ✅                     ├── get_signals.ts                  │
│    ├── analyst.py ✅                     ├── get_ux_issues.ts                │
│    └── engineer.py ✅                    ├── approve_fix.ts                  │
│                                          └── trigger_darwin.ts               │
│  /api (NEW - REST API) ✅                                                    │
│    ├── main.py                         /src/widgets                          │
│    ├── middleware/auth.py                ├── signals-dashboard/              │
│    └── routes/                           ├── decision-center/                │
│        ├── signals.py                    └── pr-viewer/                      │
│        ├── ux_issues.py                                                      │
│        └── darwin.py                                                         │
│                                                                              │
│                    ┌─────────────────────────────────┐                       │
│                    │      MongoDB Atlas (Cloud)      │                       │
│                    │  URI: mongodb+srv://...         │                       │
│                    │  DB: darwin                     │                       │
│                    └─────────────────────────────────┘                       │
│                                  │                                           │
│                                  ▼                                           │
│                    ┌─────────────────────────────────┐                       │
│                    │   Darwin REST API ✅ COMPLETE   │                       │
│                    │   http://localhost:8000         │                       │
│                    │   Auth: Bearer DARWIN_API_KEY   │                       │
│                    └─────────────────────────────────┘                       │
│                                                                              │
│                    REPO 3: Luxora_ReactNative/                               │
│                    ────────────────────────────                              │
│                    (Existing e-commerce app)                                 │
│                    GitHub: heenakousarm-cloud/Luxora_ReactNative             │
│                    PostHog: Integrated for analytics                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Local Folder Structure

```
/Users/heena/Desktop/Hackathon/
├── DARWIN_EXECUTION_PLAN.md           # Detailed execution plan
├── DARWIN_FINAL_ROADMAP.md            # This file
│
├── darwin-multi-agent/                # REPO 1: Python + CrewAI Agents
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py            # Environment & config loading
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── enums.py               # SignalType, Severity, Status enums
│   │   │   ├── signal.py              # Signal Pydantic model
│   │   │   ├── ux_issue.py            # UXIssue Pydantic model
│   │   │   ├── task.py                # Task Pydantic model
│   │   │   └── pull_request.py        # PullRequest Pydantic model
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── mongodb.py             # MongoDB client & operations
│   │   │
│   │   ├── tools/                     # CrewAI Custom Tools
│   │   │   ├── __init__.py
│   │   │   ├── posthog_tools.py       # PostHog query tools
│   │   │   ├── github_tools.py        # GitHub read/write tools
│   │   │   └── mongodb_tools.py       # MongoDB CRUD tools
│   │   │
│   │   ├── agents/                    # CrewAI Agent Definitions
│   │   │   ├── __init__.py
│   │   │   ├── watcher.py             # Watcher Agent (Eyes) 🕵️
│   │   │   ├── analyst.py             # Analyst Agent (Brain) 🧠
│   │   │   └── engineer.py            # Engineer Agent (Hands) 👩‍💻
│   │   │
│   │   ├── tasks/                     # CrewAI Task Definitions
│   │   │   ├── __init__.py
│   │   │   ├── detect_signals.py      # Watcher's task
│   │   │   ├── analyze_issues.py      # Analyst's task
│   │   │   └── create_fixes.py        # Engineer's task
│   │   │
│   │   └── crew/
│   │       ├── __init__.py
│   │       └── darwin_crew.py         # Main Crew orchestration
│   │
│   ├── scripts/
│   │   ├── run_darwin.py              # 🚀 Main entry: runs full pipeline
│   │   ├── seed_data.py               # Seed MongoDB with demo data
│   │   └── test_connections.py        # Test all API connections
│   │
│   └── data/
│       └── mock/
│           ├── signals.json           # Sample signals
│           └── ux_issues.json         # Sample UX issues
│
└── darwin-acceleration-engine/        # REPO 2: NitroStack MCP
    ├── README.md
    ├── package.json
    ├── tsconfig.json
    ├── .env.example
    ├── .gitignore
    │
    └── src/
        ├── index.ts                   # NitroStack server entry
        ├── db/
        │   └── mongodb.ts             # MongoDB client
        ├── resources/
        │   ├── uxIntelligence.ts      # UX Issues resource
        │   ├── signalsAlerts.ts       # Signals resource
        │   └── decisionCenter.ts      # Recommendations resource
        └── tools/
            ├── createTask.ts          # "Create Task" → triggers Engineer
            ├── investigate.ts         # "Investigate" signal
            └── addToRoadmap.ts        # "Add to Roadmap"
```

---

## 3. Tech Stack

### 3.1 darwin-multi-agent (Python + CrewAI)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.11+ | Core runtime |
| **Agent Framework** | **CrewAI** | **0.28+** | **Multi-agent orchestration** |
| LLM Integration | LangChain + Gemini | Latest | AI reasoning |
| AI/LLM | Google Gemini | gemini-pro | Analysis & code gen |
| Database | MongoDB | Local (Compass) | State management |
| Analytics | PostHog API | REST API | Friction detection |
| GitHub | PyGithub | Latest | PR creation |
| Models | Pydantic | v2 | Data validation |

**Dependencies (requirements.txt):**
```
# ═══════════════════════════════════════════════════════════════
# DARWIN MULTI-AGENT DEPENDENCIES
# ═══════════════════════════════════════════════════════════════

# CrewAI - Multi-Agent Framework
crewai>=0.28.0
crewai-tools>=0.1.0

# LangChain + Gemini Integration
langchain>=0.1.0
langchain-google-genai>=0.0.6
google-generativeai>=0.3.0

# Database
pymongo>=4.6.0

# Data Models
pydantic>=2.0.0

# GitHub Integration
PyGithub>=2.1.0

# HTTP & Environment
requests>=2.31.0
python-dotenv>=1.0.0

# Utilities
rich>=13.0.0           # Beautiful terminal output
```

### 3.2 darwin-acceleration-engine (TypeScript)

| Component | Technology |
|-----------|------------|
| Framework | NitroStack SDK |
| Language | TypeScript |
| Runtime | Node.js 18+ |
| Database | mongodb (npm) |

**Dependencies (package.json):**
```json
{
  "dependencies": {
    "nitrostack": "latest",
    "mongodb": "^6.0.0",
    "dotenv": "^16.0.0"
  }
}
```

### 3.3 Luxora_ReactNative (Existing)

| Component | Technology |
|-----------|------------|
| Framework | React Native |
| Platform | Expo |
| Analytics | PostHog (already integrated) |

---

## 4. Credentials & Environment

### 4.1 Environment Variables Template

**darwin-multi-agent/.env.example:**
```env
# ═══════════════════════════════════════════════════════════════
# DARWIN MULTI-AGENT ENVIRONMENT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# PostHog (Analytics)
POSTHOG_PERSONAL_API_KEY=phx_your_personal_api_key
POSTHOG_PROJECT_ID=your_project_id
POSTHOG_HOST=https://us.posthog.com

# MongoDB (Local)
MONGODB_URI=mongodb://localhost:27017/darwin

# GitHub (for PR creation)
GITHUB_TOKEN=ghp_your_github_token
GITHUB_REPO_OWNER=heenakousarm-cloud
GITHUB_REPO_NAME=Luxora_ReactNative

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key
```

**darwin-acceleration-engine/.env.example:**
```env
# ═══════════════════════════════════════════════════════════════
# DARWIN NITROSTACK ENVIRONMENT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# MongoDB (Local - same as agents)
MONGODB_URI=mongodb://localhost:27017/darwin
```

### 4.2 Actual Credentials (DO NOT COMMIT!)

| Service | Key Type | Status |
|---------|----------|--------|
| PostHog Personal API | `phx_*` | ✅ Obtained |
| PostHog Project ID | `289987` | ✅ Confirmed |
| MongoDB | Local | ✅ Using Compass |
| GitHub Token | `ghp_*` | ✅ Obtained |
| Gemini API | `AIza*` | ✅ Obtained |

---

## 5. Architecture

### 5.1 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DARWIN COMPLETE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ┌─────────────────┐                             │
│                              │    PostHog      │                             │
│                              │  Project 289987 │                             │
│                              │                 │                             │
│                              │ • product_viewed│                             │
│                              │ • add_to_cart   │                             │
│                              │ • $rageclick    │                             │
│                              │ • $autocapture  │                             │
│                              └────────┬────────┘                             │
│                                       │ Query API                            │
│                                       ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                 DARWIN-MULTI-AGENT (Python)                          │    │
│  │                                                                      │    │
│  │   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │    │
│  │   │   WATCHER    │     │   ANALYST    │     │   ENGINEER   │        │    │
│  │   │   🕵️ Eyes    │     │   🧠 Brain   │     │  👩‍💻 Hands   │        │    │
│  │   │              │     │              │     │              │        │    │
│  │   │ • Query PH   │     │ • Read code  │     │ • Gen code   │        │    │
│  │   │ • Detect     │     │ • Use Gemini │     │ • Create PR  │        │    │
│  │   │   rage clicks│     │ • Root cause │     │              │        │    │
│  │   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘        │    │
│  │          │                    │                    │                 │    │
│  │          ▼                    ▼                    ▼                 │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                    MongoDB (Local)                           │   │    │
│  │   │                    Database: darwin                          │   │    │
│  │   │                                                              │   │    │
│  │   │  signals          ux_issues          insights                │   │    │
│  │   │  collection       collection         collection              │   │    │
│  │   └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                       │                                      │
│                                       │ Read/Write                           │
│                                       ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │           DARWIN-ACCELERATION-ENGINE (NitroStack)                    │    │
│  │                                                                      │    │
│  │   @Resource('ux_intelligence')    @Tool('create_task')              │    │
│  │      │                                │                              │    │
│  │      ▼                                ▼                              │    │
│  │   Reads ux_issues              Updates status to                    │    │
│  │   from MongoDB                 TASK_CREATED                         │    │
│  │                                       │                              │    │
│  │                                       │ Triggers                     │    │
│  │                                       ▼                              │    │
│  │                              Engineer Agent                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                       │                                      │
│                                       │ Creates PR                           │
│                                       ▼                                      │
│                              ┌─────────────────┐                             │
│                              │     GitHub      │                             │
│                              │                 │                             │
│                              │ Luxora_React    │                             │
│                              │ Native          │                             │
│                              │                 │                             │
│                              │ PR: "🧬 Darwin  │                             │
│                              │ Fix: Add to     │                             │
│                              │ Cart button"    │                             │
│                              └─────────────────┘                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow Sequence

```
1. USER interacts with Luxora app
   └─► PostHog captures events (product_viewed, add_to_cart, rage clicks)

2. WATCHER AGENT runs (manual or cron)
   └─► Queries PostHog API for friction signals
   └─► Detects: "234 rage clicks on Add to Cart button"
   └─► Writes Signal to MongoDB

3. ANALYST AGENT runs (triggered by new signal)
   └─► Reads Signal from MongoDB
   └─► Fetches source code from GitHub
   └─► Uses Gemini to analyze root cause
   └─► Writes UX Issue to MongoDB (status: PENDING)

4. USER opens NitroStack UI (NitroStudio/NitroChat)
   └─► Sees UX Intelligence page
   └─► Reviews issue card with analysis
   └─► Clicks "Create Task" button

5. NITROSTACK TOOL executes
   └─► Updates MongoDB: status = TASK_CREATED

6. ENGINEER AGENT runs (watches for TASK_CREATED)
   └─► Reads approved issue from MongoDB
   └─► Fetches current code from GitHub
   └─► Uses Gemini to generate fix
   └─► Creates branch, commits fix, opens PR

7. GITHUB PR appears
   └─► "🧬 Darwin Fix: Add to Cart button touch target"
   └─► Shows analysis, impact, and fix
```

---

## 6. Data Models

### 6.0 Overview - MongoDB Collections

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DARWIN DATABASE: darwin                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COLLECTION: signals              COLLECTION: ux_issues                     │
│  ─────────────────────            ─────────────────────                     │
│  Created by: Watcher              Created by: Analyst                       │
│  Read by: Analyst, UI             Read by: Engineer, UI                     │
│                                                                              │
│  COLLECTION: tasks                COLLECTION: pull_requests                 │
│  ─────────────────────            ─────────────────────                     │
│  Created by: NitroStack Tool      Created by: Engineer                      │
│  Read by: Engineer                Read by: UI                               │
│                                                                              │
│  COLLECTION: insights             COLLECTION: product_metrics               │
│  ─────────────────────            ─────────────────────                     │
│  Created by: Analyst              Created by: Watcher                       │
│  Read by: UI (Decision Center)    Read by: UI (Product Health)             │
│                                                                              │
│  COLLECTION: agent_logs           COLLECTION: code_fixes                    │
│  ─────────────────────            ─────────────────────                     │
│  Created by: All Agents           Created by: Engineer                      │
│  Read by: Debug/Monitoring        Read by: Engineer, UI                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 6.1 Enums & Constants

```python
# agents/models.py - Enums

from enum import Enum

class SignalType(str, Enum):
    """Types of friction signals detected by Watcher"""
    RAGE_CLICK = "RAGE_CLICK"           # User clicking repeatedly on same element
    DROP_OFF = "DROP_OFF"               # Funnel step abandonment
    ERROR_SPIKE = "ERROR_SPIKE"         # Sudden increase in errors
    DEAD_CLICK = "DEAD_CLICK"           # Clicks on non-interactive elements
    SLOW_LOAD = "SLOW_LOAD"             # Performance issue detection
    FORM_ABANDON = "FORM_ABANDON"       # User abandoning form mid-fill
    SCROLL_BOUNCE = "SCROLL_BOUNCE"     # User scrolling and leaving quickly

class Severity(str, Enum):
    """Severity levels for signals and issues"""
    LOW = "LOW"                         # Minor impact, low priority
    MEDIUM = "MEDIUM"                   # Moderate impact
    HIGH = "HIGH"                       # Significant impact
    CRITICAL = "CRITICAL"               # Severe impact, needs immediate attention

class SignalStatus(str, Enum):
    """Processing status of a signal"""
    DETECTED = "DETECTED"               # Newly detected
    INVESTIGATING = "INVESTIGATING"     # Analyst is processing
    ANALYZED = "ANALYZED"               # Analysis complete
    DISMISSED = "DISMISSED"             # False positive / ignored
    CONVERTED = "CONVERTED"             # Converted to UX Issue

class UXIssueStatus(str, Enum):
    """Status of a UX Issue through the pipeline"""
    PENDING = "PENDING"                 # Awaiting human review
    APPROVED = "APPROVED"               # Human approved for fix
    TASK_CREATED = "TASK_CREATED"       # Task created, waiting for Engineer
    IN_PROGRESS = "IN_PROGRESS"         # Engineer is generating fix
    PR_OPENED = "PR_OPENED"             # PR created on GitHub
    PR_MERGED = "PR_MERGED"             # PR merged (fix deployed)
    REJECTED = "REJECTED"               # Human rejected the fix
    FAILED = "FAILED"                   # Engineer failed to create fix

class TaskPriority(str, Enum):
    """Priority levels for tasks"""
    P0 = "P0"                           # Critical - drop everything
    P1 = "P1"                           # High - this sprint
    P2 = "P2"                           # Medium - next sprint
    P3 = "P3"                           # Low - backlog

class AgentType(str, Enum):
    """Types of Darwin agents"""
    WATCHER = "WATCHER"
    ANALYST = "ANALYST"
    ENGINEER = "ENGINEER"
```

---

### 6.2 Signal (Watcher Output)

```python
# MongoDB Collection: signals
# Created by: Watcher Agent
# Consumed by: Analyst Agent, NitroStack UI

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Signal(BaseModel):
    """
    A friction signal detected by the Watcher agent from PostHog analytics.
    Represents a potential UX issue that needs investigation.
    """
    
    # MongoDB ID
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Signal Classification
    type: SignalType                    # RAGE_CLICK, DROP_OFF, etc.
    severity: Severity                  # LOW, MEDIUM, HIGH, CRITICAL
    status: SignalStatus = SignalStatus.DETECTED
    
    # Display Fields (for UI cards)
    title: str                          # "High Rage Clicks on Add to Cart"
    description: str                    # Human-readable explanation
    
    # Metrics (shown on signal card)
    metric_name: str                    # "Rage Clicks"
    metric_value: int                   # 234
    metric_change: str                  # "+156%"
    metric_period: str = "24h"          # Time period for comparison
    
    # Confidence Score (0-100)
    confidence: int = Field(ge=0, le=100)
    
    # Location Context
    page: str                           # "/product/[id]"
    page_title: str = ""                # "Product Detail Page"
    element: Optional[str] = None       # "TouchableOpacity.addToCartButton"
    element_selector: Optional[str] = None  # CSS/XPath selector if available
    
    # Impact Metrics
    affected_users: int                 # Number of unique users affected
    session_count: int                  # Number of sessions with this issue
    total_occurrences: int = 0          # Total event count
    
    # PostHog References
    posthog_query_id: Optional[str] = None
    posthog_insight_id: Optional[str] = None
    recording_ids: List[str] = []       # Session recording IDs for review
    
    # Time Context
    first_seen: datetime                # When first detected
    last_seen: datetime                 # Most recent occurrence
    detected_ago: str = ""              # "2 hours ago" (computed)
    
    # Processing State
    processed: bool = False             # Has Analyst processed this?
    investigated: bool = False          # Has human reviewed this?
    ux_issue_id: Optional[str] = None   # Link to created UX Issue
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "watcher_agent"
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

# Example Document:
SIGNAL_EXAMPLE = {
    "_id": "signal_001",
    "type": "RAGE_CLICK",
    "severity": "CRITICAL",
    "status": "DETECTED",
    "title": "High Rage Clicks on Add to Cart Button",
    "description": "234 users rage-clicking the Add to Cart button on product pages in the last 24 hours. This indicates the button may be too small or unresponsive.",
    "metric_name": "Rage Clicks",
    "metric_value": 234,
    "metric_change": "+156%",
    "metric_period": "24h",
    "confidence": 94,
    "page": "/product/[id]",
    "page_title": "Product Detail Page",
    "element": "TouchableOpacity.addToCartButton",
    "element_selector": "[data-testid='add-to-cart-btn']",
    "affected_users": 234,
    "session_count": 312,
    "total_occurrences": 1847,
    "posthog_query_id": "query_abc123",
    "recording_ids": ["rec_001", "rec_002", "rec_003"],
    "first_seen": "2026-02-03T08:00:00Z",
    "last_seen": "2026-02-04T10:00:00Z",
    "detected_ago": "2 hours ago",
    "processed": False,
    "investigated": False,
    "ux_issue_id": None,
    "created_at": "2026-02-04T10:00:00Z",
    "updated_at": "2026-02-04T10:00:00Z",
    "created_by": "watcher_agent"
}
```

---

### 6.3 UX Issue (Analyst Output)

```python
# MongoDB Collection: ux_issues
# Created by: Analyst Agent
# Consumed by: NitroStack UI, Engineer Agent

class RecommendedFix(BaseModel):
    """Detailed code fix recommendation"""
    summary: str                        # "Increase button padding"
    file_path: str                      # "app/product/[id].tsx"
    line_start: int                     # 348
    line_end: int                       # 358
    original_code: str                  # The buggy code
    suggested_code: str                 # The fixed code
    explanation: str                    # Why this fix works

class UXIssue(BaseModel):
    """
    A diagnosed UX issue with root cause analysis and recommended fix.
    Created by Analyst agent after investigating a Signal.
    """
    
    # MongoDB ID
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Link to Source Signal
    signal_id: str                      # Reference to the source signal
    
    # Status Tracking
    status: UXIssueStatus = UXIssueStatus.PENDING
    priority: Severity                  # Inherited from signal or adjusted
    
    # Display Fields (Figma Design - UX Intelligence Card)
    title: str                          # "Add to Cart Button Touch Target Too Small"
    subtitle: str = ""                  # "Product Detail - /product/[id]"
    page_info: str                      # Page context
    
    # Impact Metrics (shown in card header)
    affected_users: int                 # 234 users
    replays_count: int                  # 87 recordings available
    conversion_impact: Optional[float] = None  # -12% cart conversion
    
    # Analysis Content (from Gemini)
    description: str                    # What is happening
    root_cause: str                     # Why it's happening (technical)
    user_impact: str                    # How it affects users
    business_impact: str = ""           # Revenue/conversion impact
    
    # Confidence (shown as badge)
    confidence: int = Field(ge=0, le=100)  # 98% confidence
    confidence_factors: List[str] = []  # ["High session count", "Clear pattern"]
    
    # Recommended Fix (shown in expandable section)
    recommended_fix: RecommendedFix
    alternative_fixes: List[RecommendedFix] = []  # Other options
    
    # Code Location
    file_path: str                      # "app/product/[id].tsx"
    line_range: List[int]               # [348, 358]
    component_name: Optional[str] = None  # "ProductDetailScreen"
    
    # Evidence
    recording_urls: List[str] = []      # PostHog recording links
    screenshot_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Workflow Tracking
    reviewed_by: Optional[str] = None   # User who reviewed
    reviewed_at: Optional[datetime] = None
    task_created_at: Optional[datetime] = None
    
    # Engineer Output
    pr_url: Optional[str] = None        # GitHub PR link
    pr_number: Optional[int] = None
    branch_name: Optional[str] = None
    
    # Metadata
    created_by: str = "analyst_agent"
    tags: List[str] = []                # ["mobile", "touch-target", "critical"]

# Example Document:
UX_ISSUE_EXAMPLE = {
    "_id": "ux_issue_001",
    "signal_id": "signal_001",
    "status": "PENDING",
    "priority": "CRITICAL",
    "title": "Add to Cart Button Touch Target Too Small",
    "subtitle": "Mobile users struggling to tap the button",
    "page_info": "Product Detail - /product/[id]",
    "affected_users": 234,
    "replays_count": 87,
    "conversion_impact": -12.3,
    "description": "Users are rage-clicking on the Add to Cart button, indicating difficulty tapping it. Analysis of 87 session recordings shows users repeatedly missing the button on mobile devices.",
    "root_cause": "The button has paddingVertical: 6 which results in an effective touch target of approximately 32px height. This is significantly below Apple's Human Interface Guidelines recommendation of 44px minimum and Google's Material Design recommendation of 48dp minimum for touch targets.",
    "user_impact": "Users must tap multiple times to add items to cart, causing frustration and potential cart abandonment.",
    "business_impact": "Estimated 12% of add-to-cart attempts are failing, potentially affecting $15K/month in revenue.",
    "confidence": 98,
    "confidence_factors": [
        "High session count (312 sessions)",
        "Clear rage-click pattern",
        "Code analysis confirms small touch target",
        "Similar issues documented in HIG guidelines"
    ],
    "recommended_fix": {
        "summary": "Increase button padding to meet touch target guidelines",
        "file_path": "app/product/[id].tsx",
        "line_start": 348,
        "line_end": 358,
        "original_code": "addToCartButton: {\n  paddingVertical: 6,\n  paddingHorizontal: 8,\n}",
        "suggested_code": "addToCartButton: {\n  paddingVertical: 16,\n  paddingHorizontal: 24,\n  minHeight: 48,\n}",
        "explanation": "Increasing paddingVertical to 16 and adding minHeight: 48 ensures the touch target meets the 48px minimum. This aligns with both Apple HIG (44pt) and Material Design (48dp) guidelines."
    },
    "alternative_fixes": [],
    "file_path": "app/product/[id].tsx",
    "line_range": [348, 358],
    "component_name": "ProductDetailScreen",
    "recording_urls": [
        "https://us.posthog.com/recordings/rec_001",
        "https://us.posthog.com/recordings/rec_002"
    ],
    "created_at": "2026-02-04T10:30:00Z",
    "updated_at": "2026-02-04T10:30:00Z",
    "reviewed_by": None,
    "reviewed_at": None,
    "task_created_at": None,
    "pr_url": None,
    "pr_number": None,
    "branch_name": None,
    "created_by": "analyst_agent",
    "tags": ["mobile", "touch-target", "critical", "add-to-cart"]
}
```

---

### 6.4 Task (NitroStack Output)

```python
# MongoDB Collection: tasks
# Created by: NitroStack createTask tool (human approval)
# Consumed by: Engineer Agent

class Task(BaseModel):
    """
    A task created when a human approves a UX Issue fix.
    This is the trigger for the Engineer agent to generate code.
    """
    
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Reference to UX Issue
    ux_issue_id: str
    signal_id: str
    
    # Task Details
    title: str                          # Copied from UX Issue
    description: str                    # Copied from UX Issue
    priority: TaskPriority              # P0, P1, P2, P3
    
    # Assignment
    assigned_to: str = "engineer_agent"
    created_by: str                     # User who approved
    
    # Status
    status: str = "PENDING"             # PENDING, IN_PROGRESS, COMPLETED, FAILED
    
    # Fix Details (copied from UX Issue)
    file_path: str
    recommended_fix: RecommendedFix
    
    # Output
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    branch_name: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Retry Logic
    attempt_count: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None

# Example Document:
TASK_EXAMPLE = {
    "_id": "task_001",
    "ux_issue_id": "ux_issue_001",
    "signal_id": "signal_001",
    "title": "Fix: Add to Cart Button Touch Target",
    "description": "Increase button padding to meet 48px touch target minimum",
    "priority": "P0",
    "assigned_to": "engineer_agent",
    "created_by": "heena@example.com",
    "status": "PENDING",
    "file_path": "app/product/[id].tsx",
    "recommended_fix": { ... },  # Same as UX Issue
    "pr_url": None,
    "created_at": "2026-02-04T11:00:00Z",
    "started_at": None,
    "completed_at": None,
    "attempt_count": 0
}
```

---

### 6.5 Pull Request (Engineer Output)

```python
# MongoDB Collection: pull_requests
# Created by: Engineer Agent
# Consumed by: NitroStack UI, Monitoring

class PullRequest(BaseModel):
    """
    Record of a GitHub PR created by the Engineer agent.
    """
    
    id: Optional[str] = Field(default=None, alias="_id")
    
    # References
    task_id: str
    ux_issue_id: str
    signal_id: str
    
    # GitHub Details
    pr_number: int
    pr_url: str                         # Full GitHub URL
    branch_name: str                    # "darwin/fix-add-to-cart-touch-target"
    base_branch: str = "main"
    
    # PR Content
    title: str                          # "🧬 Darwin Fix: Add to Cart button touch target"
    body: str                           # Full PR description with analysis
    
    # Files Changed
    files_changed: List[str]
    additions: int
    deletions: int
    
    # Status
    status: str = "OPEN"                # OPEN, MERGED, CLOSED
    mergeable: Optional[bool] = None
    
    # CI/CD
    checks_passed: Optional[bool] = None
    ci_status: Optional[str] = None     # pending, success, failure
    
    # Review
    reviewers: List[str] = []
    approved_by: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Metadata
    created_by: str = "engineer_agent"

# Example Document:
PR_EXAMPLE = {
    "_id": "pr_001",
    "task_id": "task_001",
    "ux_issue_id": "ux_issue_001",
    "signal_id": "signal_001",
    "pr_number": 42,
    "pr_url": "https://github.com/heenakousarm-cloud/Luxora_ReactNative/pull/42",
    "branch_name": "darwin/fix-add-to-cart-touch-target",
    "base_branch": "main",
    "title": "🧬 Darwin Fix: Add to Cart button touch target",
    "body": "## 🧬 Darwin Auto-Fix\n\n### Issue\nUsers rage-clicking on Add to Cart button...\n\n### Root Cause\n...\n\n### Fix\n...",
    "files_changed": ["app/product/[id].tsx"],
    "additions": 4,
    "deletions": 2,
    "status": "OPEN",
    "created_at": "2026-02-04T11:15:00Z"
}
```

---

### 6.6 Product Metric (Dashboard)

```python
# MongoDB Collection: product_metrics
# Created by: Watcher Agent (periodic)
# Consumed by: NitroStack UI (Product Health page)

class ProductMetric(BaseModel):
    """
    Product health metrics for the dashboard.
    Updated periodically by the Watcher agent.
    """
    
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Metric Identity
    name: str                           # "Active Users"
    key: str                            # "active_users"
    category: str                       # "engagement", "conversion", "performance"
    
    # Current Value
    value: float                        # 12,847
    formatted_value: str                # "12.8K"
    unit: str = ""                      # "users", "%", "ms"
    
    # Trend
    change: float                       # 12.5
    change_direction: str               # "up", "down", "stable"
    change_period: str = "7d"           # Comparison period
    is_positive_good: bool = True       # Is increase good?
    
    # Thresholds
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    status: str = "healthy"             # healthy, warning, critical
    
    # Time Context
    period_start: datetime
    period_end: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Display
    display_order: int = 0              # For sorting in UI
    icon: str = ""                      # Icon identifier
    color: str = ""                     # Color code

# Example Documents:
METRICS_EXAMPLES = [
    {
        "_id": "metric_active_users",
        "name": "Active Users",
        "key": "active_users",
        "category": "engagement",
        "value": 12847,
        "formatted_value": "12.8K",
        "unit": "users",
        "change": 12.5,
        "change_direction": "up",
        "change_period": "7d",
        "is_positive_good": True,
        "status": "healthy",
        "display_order": 1
    },
    {
        "_id": "metric_conversion_rate",
        "name": "Conversion Rate",
        "key": "conversion_rate",
        "category": "conversion",
        "value": 3.2,
        "formatted_value": "3.2%",
        "unit": "%",
        "change": -0.8,
        "change_direction": "down",
        "change_period": "7d",
        "is_positive_good": True,
        "warning_threshold": 3.0,
        "critical_threshold": 2.5,
        "status": "warning",
        "display_order": 2
    },
    {
        "_id": "metric_cart_abandonment",
        "name": "Cart Abandonment",
        "key": "cart_abandonment",
        "category": "conversion",
        "value": 68.5,
        "formatted_value": "68.5%",
        "unit": "%",
        "change": 5.2,
        "change_direction": "up",
        "is_positive_good": False,
        "warning_threshold": 65,
        "critical_threshold": 75,
        "status": "warning",
        "display_order": 3
    }
]
```

---

### 6.7 Insight / Recommendation (Decision Center)

```python
# MongoDB Collection: insights
# Created by: Analyst Agent
# Consumed by: NitroStack UI (Decision Center)

class Insight(BaseModel):
    """
    Strategic recommendations for the Decision Center.
    These are broader insights beyond individual UX issues.
    """
    
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Insight Type
    type: str                           # "optimization", "experiment", "alert"
    category: str                       # "conversion", "engagement", "retention"
    
    # Display
    title: str                          # "Optimize checkout flow"
    description: str                    # Detailed explanation
    
    # Impact Estimation
    estimated_impact: str               # "+5-10% conversion"
    confidence: int                     # 0-100
    effort: str                         # "low", "medium", "high"
    
    # Evidence
    supporting_signals: List[str] = []  # Signal IDs
    supporting_data: dict = {}          # Analytics data
    
    # Actions
    recommended_actions: List[str] = []  # Action items
    
    # Status
    status: str = "NEW"                 # NEW, REVIEWED, IN_PROGRESS, COMPLETED
    added_to_roadmap: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None

# Example Document:
INSIGHT_EXAMPLE = {
    "_id": "insight_001",
    "type": "optimization",
    "category": "conversion",
    "title": "Mobile Checkout Flow Optimization",
    "description": "Analysis shows 68% cart abandonment rate with key drop-off points at payment entry. Multiple UX issues identified.",
    "estimated_impact": "+8-12% conversion rate",
    "confidence": 85,
    "effort": "medium",
    "supporting_signals": ["signal_001", "signal_002"],
    "recommended_actions": [
        "Fix Add to Cart button touch target",
        "Simplify payment form",
        "Add Apple Pay / Google Pay"
    ],
    "status": "NEW",
    "created_at": "2026-02-04T12:00:00Z"
}
```

---

### 6.8 Agent Log (Monitoring)

```python
# MongoDB Collection: agent_logs
# Created by: All Agents
# Consumed by: Debug/Monitoring

class AgentLog(BaseModel):
    """
    Activity log for all Darwin agents.
    Used for debugging and monitoring agent behavior.
    """
    
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Agent Info
    agent: AgentType                    # WATCHER, ANALYST, ENGINEER
    session_id: str                     # Unique run session
    
    # Log Entry
    level: str = "INFO"                 # DEBUG, INFO, WARN, ERROR
    message: str
    
    # Context
    signal_id: Optional[str] = None
    ux_issue_id: Optional[str] = None
    task_id: Optional[str] = None
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None
    
    # Error Details (if applicable)
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Metadata
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None

# Example Documents:
LOG_EXAMPLES = [
    {
        "agent": "WATCHER",
        "session_id": "watch_2026020410",
        "level": "INFO",
        "message": "Started PostHog query for rage clicks",
        "timestamp": "2026-02-04T10:00:00Z"
    },
    {
        "agent": "WATCHER",
        "session_id": "watch_2026020410",
        "level": "INFO",
        "message": "Detected 1 new signal: RAGE_CLICK on /product/[id]",
        "signal_id": "signal_001",
        "timestamp": "2026-02-04T10:00:05Z"
    },
    {
        "agent": "ANALYST",
        "session_id": "analyze_2026020410",
        "level": "INFO",
        "message": "Analyzing signal with Gemini",
        "signal_id": "signal_001",
        "timestamp": "2026-02-04T10:30:00Z"
    }
]
```

---

### 6.9 Code Fix (Engineer Working Data)

```python
# MongoDB Collection: code_fixes
# Created by: Engineer Agent
# Consumed by: Engineer (retry logic), UI (PR content)

class CodeFix(BaseModel):
    """
    Generated code fix with diff and validation.
    Intermediate working data for Engineer agent.
    """
    
    id: Optional[str] = Field(default=None, alias="_id")
    
    # References
    task_id: str
    ux_issue_id: str
    
    # File Info
    file_path: str
    original_content: str               # Full original file
    fixed_content: str                  # Full fixed file
    
    # Diff
    diff: str                           # Git-style diff
    diff_lines: int                     # Number of lines changed
    
    # Validation
    syntax_valid: bool = False          # Passed syntax check?
    linter_errors: List[str] = []       # Any linting issues
    
    # Generation Metadata
    gemini_model: str = "gemini-pro"
    prompt_tokens: int = 0
    response_tokens: int = 0
    generation_time_ms: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Retry Info
    attempt_number: int = 1
    previous_attempt_ids: List[str] = []
```

---

### 6.10 MongoDB Indexes

```javascript
// Recommended indexes for performance

// signals collection
db.signals.createIndex({ "status": 1, "created_at": -1 })
db.signals.createIndex({ "type": 1, "severity": 1 })
db.signals.createIndex({ "processed": 1 })

// ux_issues collection
db.ux_issues.createIndex({ "status": 1, "created_at": -1 })
db.ux_issues.createIndex({ "signal_id": 1 })
db.ux_issues.createIndex({ "priority": 1 })

// tasks collection
db.tasks.createIndex({ "status": 1, "created_at": -1 })
db.tasks.createIndex({ "ux_issue_id": 1 })

// agent_logs collection
db.agent_logs.createIndex({ "agent": 1, "timestamp": -1 })
db.agent_logs.createIndex({ "session_id": 1 })
db.agent_logs.createIndex({ "level": 1, "timestamp": -1 })

// product_metrics collection
db.product_metrics.createIndex({ "key": 1 }, { unique: true })
db.product_metrics.createIndex({ "category": 1, "display_order": 1 })
```

---

### 6.11 TypeScript Interfaces (NitroStack)

```typescript
// src/types/models.ts - TypeScript interfaces matching Python models

export type SignalType = 
  | 'RAGE_CLICK' 
  | 'DROP_OFF' 
  | 'ERROR_SPIKE' 
  | 'DEAD_CLICK';

export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type UXIssueStatus = 
  | 'PENDING' 
  | 'APPROVED' 
  | 'TASK_CREATED' 
  | 'IN_PROGRESS' 
  | 'PR_OPENED' 
  | 'PR_MERGED';

export interface Signal {
  _id: string;
  type: SignalType;
  severity: Severity;
  title: string;
  description: string;
  metric_name: string;
  metric_value: number;
  metric_change: string;
  confidence: number;
  page: string;
  element?: string;
  affected_users: number;
  session_count: number;
  recording_ids: string[];
  detected_ago: string;
  processed: boolean;
  created_at: string;
}

export interface RecommendedFix {
  summary: string;
  file_path: string;
  line_start: number;
  line_end: number;
  original_code: string;
  suggested_code: string;
  explanation: string;
}

export interface UXIssue {
  _id: string;
  signal_id: string;
  status: UXIssueStatus;
  priority: Severity;
  title: string;
  page_info: string;
  affected_users: number;
  replays_count: number;
  description: string;
  root_cause: string;
  user_impact: string;
  confidence: number;
  recommended_fix: RecommendedFix;
  file_path: string;
  line_range: [number, number];
  recording_urls: string[];
  pr_url?: string;
  pr_number?: number;
  created_at: string;
  task_created_at?: string;
}

export interface ProductMetric {
  _id: string;
  name: string;
  key: string;
  category: string;
  value: number;
  formatted_value: string;
  change: number;
  change_direction: 'up' | 'down' | 'stable';
  status: 'healthy' | 'warning' | 'critical';
}
```

---

## 7. CrewAI Agents & Tools

### 7.1 Overview - CrewAI Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DARWIN CREWAI ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────────────┐                         │
│                         │     DARWIN CREW         │                         │
│                         │  (Process: Sequential)  │                         │
│                         └───────────┬─────────────┘                         │
│                                     │                                        │
│         ┌───────────────────────────┼───────────────────────────┐           │
│         │                           │                           │           │
│         ▼                           ▼                           ▼           │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐       │
│  │   WATCHER   │           │   ANALYST   │           │   ENGINEER  │       │
│  │   AGENT     │ ────────► │   AGENT     │ ────────► │   AGENT     │       │
│  │   🕵️ Eyes   │  Signal   │   🧠 Brain  │  UXIssue  │  👩‍💻 Hands  │       │
│  └──────┬──────┘           └──────┬──────┘           └──────┬──────┘       │
│         │                         │                         │               │
│         │ Tools:                  │ Tools:                  │ Tools:        │
│         │ • PostHogQueryTool      │ • GitHubReadTool        │ • GitHubPRTool│
│         │ • MongoDBWriteTool      │ • MongoDBReadTool       │ • MongoDBTool │
│         │                         │ • MongoDBWriteTool      │               │
│         │                         │                         │               │
│         ▼                         ▼                         ▼               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         MongoDB (darwin)                             │   │
│  │  signals → ux_issues → tasks → pull_requests                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                        │
│                                     ▼                                        │
│                         ┌─────────────────────────┐                         │
│                         │     GitHub PR Created   │                         │
│                         │   🧬 Darwin Auto-Fix    │                         │
│                         └─────────────────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.2 Custom Tools

#### 7.2.1 PostHog Tools

```python
# src/tools/posthog_tools.py

from crewai_tools import BaseTool
from pydantic import Field
import requests
from typing import Optional, List
import os

class PostHogQueryTool(BaseTool):
    """
    Query PostHog analytics for friction signals.
    Used by Watcher Agent to detect rage clicks, drop-offs, etc.
    """
    name: str = "PostHog Query Tool"
    description: str = """
    Query PostHog analytics API to find user friction signals.
    Use this to:
    - Find rage click events ($rageclick)
    - Analyze funnel drop-offs
    - Detect error spikes
    - Get session recording IDs
    
    Input: Query type (rage_clicks, drop_offs, errors) and time range
    Output: List of events with counts and user data
    """
    
    api_key: str = Field(default_factory=lambda: os.getenv("POSTHOG_PERSONAL_API_KEY"))
    project_id: str = Field(default_factory=lambda: os.getenv("POSTHOG_PROJECT_ID"))
    host: str = Field(default="https://us.posthog.com")
    
    def _run(self, query_type: str, hours: int = 24) -> str:
        """Execute PostHog query and return results."""
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        if query_type == "rage_clicks":
            # Query for rage click events
            query = {
                "kind": "HogQLQuery",
                "query": f"""
                    SELECT 
                        properties.$current_url as page,
                        properties.$el_text as element,
                        count() as count,
                        uniq(distinct_id) as unique_users
                    FROM events
                    WHERE event = '$rageclick'
                    AND timestamp > now() - interval {hours} hour
                    GROUP BY page, element
                    ORDER BY count DESC
                    LIMIT 10
                """
            }
        elif query_type == "drop_offs":
            # Query for funnel drop-offs (add_to_cart without purchase)
            query = {
                "kind": "HogQLQuery", 
                "query": f"""
                    SELECT 
                        properties.$current_url as page,
                        count() as cart_adds,
                        uniq(distinct_id) as users
                    FROM events
                    WHERE event = 'add_to_cart'
                    AND timestamp > now() - interval {hours} hour
                    AND distinct_id NOT IN (
                        SELECT distinct_id FROM events 
                        WHERE event = 'purchase'
                        AND timestamp > now() - interval {hours} hour
                    )
                    GROUP BY page
                    ORDER BY cart_adds DESC
                """
            }
        else:
            return f"Unknown query type: {query_type}"
        
        response = requests.post(
            f"{self.host}/api/projects/{self.project_id}/query",
            headers=headers,
            json=query
        )
        
        if response.status_code == 200:
            return str(response.json())
        else:
            return f"Error: {response.status_code} - {response.text}"


class PostHogRecordingsTool(BaseTool):
    """
    Fetch session recording URLs from PostHog for evidence.
    """
    name: str = "PostHog Recordings Tool"
    description: str = """
    Get session recording URLs from PostHog for a specific page or event.
    Use this to gather evidence for UX issues.
    
    Input: Page URL or event name
    Output: List of session recording URLs
    """
    
    api_key: str = Field(default_factory=lambda: os.getenv("POSTHOG_PERSONAL_API_KEY"))
    project_id: str = Field(default_factory=lambda: os.getenv("POSTHOG_PROJECT_ID"))
    host: str = Field(default="https://us.posthog.com")
    
    def _run(self, page_url: str, limit: int = 5) -> str:
        """Fetch recording URLs for a page."""
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Query recordings API
        response = requests.get(
            f"{self.host}/api/projects/{self.project_id}/session_recordings",
            headers=headers,
            params={
                "properties": f'[{{"key":"$current_url","value":"{page_url}","operator":"icontains"}}]',
                "limit": limit
            }
        )
        
        if response.status_code == 200:
            recordings = response.json().get("results", [])
            urls = [f"{self.host}/recordings/{r['id']}" for r in recordings]
            return str(urls)
        else:
            return f"Error: {response.status_code}"
```

---

#### 7.2.2 GitHub Tools

```python
# src/tools/github_tools.py

from crewai_tools import BaseTool
from pydantic import Field
from github import Github
import os
import base64

class GitHubReadTool(BaseTool):
    """
    Read file contents from GitHub repository.
    Used by Analyst to examine source code.
    """
    name: str = "GitHub Read Tool"
    description: str = """
    Read file contents from a GitHub repository.
    Use this to examine source code when analyzing UX issues.
    
    Input: File path (e.g., 'app/product/[id].tsx')
    Output: File contents as string
    """
    
    token: str = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))
    repo_owner: str = Field(default_factory=lambda: os.getenv("GITHUB_REPO_OWNER"))
    repo_name: str = Field(default_factory=lambda: os.getenv("GITHUB_REPO_NAME"))
    
    def _run(self, file_path: str, branch: str = "main") -> str:
        """Read file from GitHub."""
        
        g = Github(self.token)
        repo = g.get_repo(f"{self.repo_owner}/{self.repo_name}")
        
        try:
            content = repo.get_contents(file_path, ref=branch)
            decoded = base64.b64decode(content.content).decode('utf-8')
            return decoded
        except Exception as e:
            return f"Error reading file: {str(e)}"


class GitHubPRTool(BaseTool):
    """
    Create a Pull Request on GitHub with code changes.
    Used by Engineer to submit fixes.
    """
    name: str = "GitHub PR Tool"
    description: str = """
    Create a GitHub Pull Request with code changes.
    Use this to submit fixes for UX issues.
    
    Input: 
    - branch_name: Name for the new branch
    - file_path: Path to file being changed
    - new_content: The fixed file content
    - pr_title: Title for the PR
    - pr_body: Description of the changes
    
    Output: PR URL
    """
    
    token: str = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))
    repo_owner: str = Field(default_factory=lambda: os.getenv("GITHUB_REPO_OWNER"))
    repo_name: str = Field(default_factory=lambda: os.getenv("GITHUB_REPO_NAME"))
    
    def _run(
        self, 
        branch_name: str,
        file_path: str, 
        new_content: str,
        pr_title: str,
        pr_body: str,
        base_branch: str = "main"
    ) -> str:
        """Create branch, commit changes, and open PR."""
        
        g = Github(self.token)
        repo = g.get_repo(f"{self.repo_owner}/{self.repo_name}")
        
        try:
            # 1. Get the base branch SHA
            base_ref = repo.get_branch(base_branch)
            base_sha = base_ref.commit.sha
            
            # 2. Create new branch
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )
            
            # 3. Get current file to get its SHA
            current_file = repo.get_contents(file_path, ref=branch_name)
            
            # 4. Update the file
            repo.update_file(
                path=file_path,
                message=f"🧬 Darwin Fix: {pr_title}",
                content=new_content,
                sha=current_file.sha,
                branch=branch_name
            )
            
            # 5. Create Pull Request
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch
            )
            
            return f"✅ PR Created: {pr.html_url}"
            
        except Exception as e:
            return f"Error creating PR: {str(e)}"
```

---

#### 7.2.3 MongoDB Tools

```python
# src/tools/mongodb_tools.py

from crewai_tools import BaseTool
from pydantic import Field
from pymongo import MongoClient
from datetime import datetime
import os
import json

class MongoDBReadTool(BaseTool):
    """
    Read documents from MongoDB collections.
    """
    name: str = "MongoDB Read Tool"
    description: str = """
    Read documents from MongoDB darwin database.
    Use this to fetch signals, UX issues, or tasks.
    
    Input: 
    - collection: Collection name (signals, ux_issues, tasks)
    - query: MongoDB query dict (optional, default: {})
    - limit: Max documents to return (optional, default: 10)
    
    Output: List of documents as JSON string
    """
    
    uri: str = Field(default_factory=lambda: os.getenv("MONGODB_URI"))
    
    def _run(self, collection: str, query: dict = None, limit: int = 10) -> str:
        """Read documents from MongoDB."""
        
        client = MongoClient(self.uri)
        db = client.darwin
        
        query = query or {}
        docs = list(db[collection].find(query).limit(limit))
        
        # Convert ObjectId to string
        for doc in docs:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        client.close()
        return json.dumps(docs, default=str, indent=2)


class MongoDBWriteTool(BaseTool):
    """
    Write documents to MongoDB collections.
    """
    name: str = "MongoDB Write Tool"
    description: str = """
    Write or update documents in MongoDB darwin database.
    Use this to save signals, UX issues, tasks, or PR records.
    
    Input:
    - collection: Collection name
    - document: Document to insert/update
    - update_id: If provided, updates existing doc instead of inserting
    
    Output: Inserted/updated document ID
    """
    
    uri: str = Field(default_factory=lambda: os.getenv("MONGODB_URI"))
    
    def _run(self, collection: str, document: dict, update_id: str = None) -> str:
        """Write document to MongoDB."""
        
        client = MongoClient(self.uri)
        db = client.darwin
        
        # Add timestamps
        document['updated_at'] = datetime.utcnow()
        
        if update_id:
            # Update existing document
            result = db[collection].update_one(
                {"_id": update_id},
                {"$set": document}
            )
            client.close()
            return f"Updated document: {update_id}"
        else:
            # Insert new document
            document['created_at'] = datetime.utcnow()
            result = db[collection].insert_one(document)
            client.close()
            return f"Inserted document: {str(result.inserted_id)}"
```

---

### 7.3 Agent Definitions

#### 7.3.1 Watcher Agent (Eyes) 🕵️

```python
# src/agents/watcher.py

from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.posthog_tools import PostHogQueryTool, PostHogRecordingsTool
from src.tools.mongodb_tools import MongoDBWriteTool
from src.config.settings import settings

def create_watcher_agent() -> Agent:
    """
    Create the Watcher Agent - Darwin's Eyes.
    Responsible for detecting friction signals from PostHog analytics.
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.1  # Low temperature for consistent detection
    )
    
    return Agent(
        role="UX Friction Detector",
        
        goal="""
        Monitor PostHog analytics to detect user friction signals that indicate 
        UX problems. Focus on:
        - Rage clicks (users clicking repeatedly in frustration)
        - Funnel drop-offs (users abandoning key flows)
        - Error spikes (sudden increases in errors)
        
        When you detect a signal, calculate its severity based on affected users 
        and save it to MongoDB for the Analyst to investigate.
        """,
        
        backstory="""
        You are Darwin's vigilant eyes - a pattern recognition specialist who 
        never misses a sign of user frustration. You've analyzed millions of 
        user sessions and know exactly what friction looks like in analytics data.
        
        Your motto: "Every rage click is a user crying for help."
        
        You are methodical and thorough. You query PostHog systematically, 
        calculate confidence scores based on statistical significance, and 
        create detailed signal reports that the Analyst can act on.
        """,
        
        llm=llm,
        
        tools=[
            PostHogQueryTool(),
            PostHogRecordingsTool(),
            MongoDBWriteTool()
        ],
        
        verbose=True,
        allow_delegation=False,
        max_iter=5,
        
        # Memory settings
        memory=True
    )
```

---

#### 7.3.2 Analyst Agent (Brain) 🧠

```python
# src/agents/analyst.py

from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.github_tools import GitHubReadTool
from src.tools.mongodb_tools import MongoDBReadTool, MongoDBWriteTool
from src.config.settings import settings

def create_analyst_agent() -> Agent:
    """
    Create the Analyst Agent - Darwin's Brain.
    Responsible for diagnosing root causes and recommending fixes.
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3  # Some creativity for analysis
    )
    
    return Agent(
        role="UX Root Cause Analyst",
        
        goal="""
        For each friction signal detected by the Watcher:
        1. Understand what's happening (the symptom)
        2. Examine the source code to find WHY it's happening (root cause)
        3. Recommend a specific, actionable code fix
        4. Calculate confidence in your diagnosis
        
        Your analysis should be detailed enough that an engineer can implement 
        the fix without additional context.
        """,
        
        backstory="""
        You are Darwin's analytical brain - a senior UX engineer with deep 
        expertise in mobile development, accessibility guidelines, and user 
        behavior psychology.
        
        You've fixed thousands of UX issues and can look at a friction signal 
        and immediately start forming hypotheses about the root cause. You then 
        systematically verify your hypotheses by examining the code.
        
        You know:
        - Apple HIG recommends 44pt minimum touch targets
        - Material Design recommends 48dp touch targets
        - Common React Native styling pitfalls
        - How small changes in padding can dramatically affect usability
        
        Your analyses are thorough but actionable. You don't just say "the button 
        is too small" - you say "paddingVertical: 6 results in a 32px touch target, 
        which is 16px below the 48px minimum. Change to paddingVertical: 16."
        """,
        
        llm=llm,
        
        tools=[
            GitHubReadTool(),
            MongoDBReadTool(),
            MongoDBWriteTool()
        ],
        
        verbose=True,
        allow_delegation=False,
        max_iter=8,
        
        memory=True
    )
```

---

#### 7.3.3 Engineer Agent (Hands) 👩‍💻

```python
# src/agents/engineer.py

from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.github_tools import GitHubReadTool, GitHubPRTool
from src.tools.mongodb_tools import MongoDBReadTool, MongoDBWriteTool
from src.config.settings import settings

def create_engineer_agent() -> Agent:
    """
    Create the Engineer Agent - Darwin's Hands.
    Responsible for generating code fixes and creating PRs.
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.2  # Low temperature for precise code generation
    )
    
    return Agent(
        role="Autonomous Code Fixer",
        
        goal="""
        For each approved UX issue (status: TASK_CREATED):
        1. Fetch the current file content from GitHub
        2. Apply the recommended fix precisely
        3. Ensure the fix follows code style conventions
        4. Create a new branch with a descriptive name
        5. Commit the changes with a clear message
        6. Open a Pull Request with:
           - Clear title with 🧬 Darwin branding
           - Detailed description of the issue
           - Root cause explanation
           - Before/after code comparison
           - Impact metrics
        
        The PR should be production-ready and require minimal human review.
        """,
        
        backstory="""
        You are Darwin's skilled hands - a meticulous code craftsman who takes 
        diagnosed UX issues and turns them into perfect Pull Requests.
        
        You have strong opinions about code quality:
        - Changes should be minimal and focused
        - Style should match the existing codebase
        - Commits should be atomic and well-described
        - PRs should tell a complete story
        
        You format your PR descriptions beautifully with:
        - 🔍 Issue Summary
        - 🎯 Root Cause
        - 🛠️ The Fix
        - 📊 Impact
        - 📸 Before/After
        
        You never submit sloppy code. Every PR is your signature work.
        """,
        
        llm=llm,
        
        tools=[
            GitHubReadTool(),
            GitHubPRTool(),
            MongoDBReadTool(),
            MongoDBWriteTool()
        ],
        
        verbose=True,
        allow_delegation=False,
        max_iter=10,
        
        memory=True
    )
```

---

### 7.4 Task Definitions

```python
# src/tasks/all_tasks.py

from crewai import Task
from src.agents.watcher import create_watcher_agent
from src.agents.analyst import create_analyst_agent
from src.agents.engineer import create_engineer_agent

# ═══════════════════════════════════════════════════════════════
# TASK 1: DETECT FRICTION SIGNALS
# ═══════════════════════════════════════════════════════════════
detect_signals_task = Task(
    description="""
    ## Your Mission: Detect User Friction
    
    Query PostHog analytics for the last 24 hours to find friction signals:
    
    ### Step 1: Query for Rage Clicks
    Use the PostHog Query Tool with query_type="rage_clicks" to find:
    - Pages with high rage click counts
    - Elements being rage-clicked
    - Number of affected users
    
    ### Step 2: Analyze Results
    For each potential signal:
    - Calculate severity (CRITICAL if >100 users, HIGH if >50, etc.)
    - Calculate confidence based on session count
    - Identify the specific element causing issues
    
    ### Step 3: Get Evidence
    Use the PostHog Recordings Tool to get session recording URLs 
    that show the friction happening.
    
    ### Step 4: Save to MongoDB
    For each significant signal (confidence > 70%), save to MongoDB 
    'signals' collection with this structure:
    
    {
        "type": "RAGE_CLICK",
        "severity": "CRITICAL",
        "title": "Descriptive title",
        "description": "What's happening",
        "metric_name": "Rage Clicks",
        "metric_value": <count>,
        "metric_change": "+X%",
        "confidence": <0-100>,
        "page": "<page_url>",
        "element": "<element_identifier>",
        "affected_users": <count>,
        "session_count": <count>,
        "recording_ids": [<urls>],
        "processed": false
    }
    
    Return a summary of all signals detected.
    """,
    
    expected_output="""
    A JSON summary containing:
    - Number of signals detected
    - List of signal IDs created
    - Brief description of each signal
    
    Example:
    {
        "signals_detected": 1,
        "signals": [
            {
                "id": "signal_001",
                "type": "RAGE_CLICK",
                "title": "High Rage Clicks on Add to Cart Button",
                "severity": "CRITICAL",
                "affected_users": 234
            }
        ]
    }
    """,
    
    agent=create_watcher_agent()
)

# ═══════════════════════════════════════════════════════════════
# TASK 2: ANALYZE ROOT CAUSE
# ═══════════════════════════════════════════════════════════════
analyze_issues_task = Task(
    description="""
    ## Your Mission: Diagnose Root Causes
    
    For each unprocessed signal in MongoDB (processed: false):
    
    ### Step 1: Read the Signal
    Use MongoDB Read Tool to get signals where processed=false
    
    ### Step 2: Examine the Code
    Use GitHub Read Tool to fetch the relevant source file.
    For example, if the signal mentions "/product/[id]", read:
    - app/product/[id].tsx
    
    ### Step 3: Analyze Root Cause
    Look at the code and determine WHY users are experiencing friction.
    Consider:
    - Touch target sizes (minimum 48px)
    - Padding and margins
    - Interactive element styling
    - Accessibility issues
    
    ### Step 4: Formulate Fix
    Create a specific, actionable fix recommendation:
    - Exact file path
    - Line numbers
    - Original code snippet
    - Fixed code snippet
    - Explanation of why this fixes the issue
    
    ### Step 5: Save UX Issue
    Save to MongoDB 'ux_issues' collection:
    
    {
        "signal_id": "<from signal>",
        "status": "PENDING",
        "priority": "<from signal severity>",
        "title": "Clear issue title",
        "page_info": "Page - /path",
        "affected_users": <from signal>,
        "replays_count": <count of recordings>,
        "description": "What's happening",
        "root_cause": "Technical explanation",
        "user_impact": "How it affects users",
        "confidence": <0-100>,
        "recommended_fix": {
            "summary": "Brief fix description",
            "file_path": "path/to/file.tsx",
            "line_start": <line>,
            "line_end": <line>,
            "original_code": "...",
            "suggested_code": "...",
            "explanation": "Why this works"
        },
        "file_path": "path/to/file.tsx",
        "line_range": [start, end],
        "recording_urls": [<from signal>]
    }
    
    ### Step 6: Mark Signal as Processed
    Update the signal with processed=true and ux_issue_id
    """,
    
    expected_output="""
    A JSON summary containing:
    - Number of issues analyzed
    - List of UX issue IDs created
    - Brief root cause for each
    
    Example:
    {
        "issues_analyzed": 1,
        "issues": [
            {
                "id": "ux_issue_001",
                "signal_id": "signal_001",
                "title": "Add to Cart Button Touch Target Too Small",
                "root_cause": "paddingVertical: 6 results in 32px touch target",
                "confidence": 98
            }
        ]
    }
    """,
    
    agent=create_analyst_agent(),
    context=[detect_signals_task]  # Depends on signals being detected
)

# ═══════════════════════════════════════════════════════════════
# TASK 3: CREATE CODE FIX & PR
# ═══════════════════════════════════════════════════════════════
create_fixes_task = Task(
    description="""
    ## Your Mission: Generate Fix & Create PR
    
    For each UX issue with status="TASK_CREATED":
    
    ### Step 1: Read Approved Issue
    Use MongoDB Read Tool to get issues where status="TASK_CREATED"
    
    ### Step 2: Fetch Current Code
    Use GitHub Read Tool to get the current file content
    
    ### Step 3: Apply the Fix
    Take the recommended_fix from the issue and apply it to the file:
    - Replace the original_code with suggested_code
    - Ensure proper indentation and style
    - Don't change anything else in the file
    
    ### Step 4: Create Pull Request
    Use GitHub PR Tool with:
    
    branch_name: "darwin/fix-{slug-from-title}"
    
    pr_title: "🧬 Darwin Fix: {issue title}"
    
    pr_body: (formatted markdown)
    ```
    ## 🧬 Darwin Auto-Fix
    
    ### 🔍 Issue Summary
    {description}
    
    **Affected Users:** {affected_users}
    **Confidence:** {confidence}%
    **Priority:** {priority}
    
    ### 🎯 Root Cause
    {root_cause}
    
    ### 🛠️ The Fix
    {recommended_fix.explanation}
    
    ### 📊 Before
    ```tsx
    {original_code}
    ```
    
    ### ✅ After
    ```tsx
    {suggested_code}
    ```
    
    ### 📹 Session Recordings
    - {recording_urls}
    
    ---
    *This PR was automatically generated by Darwin 🧬*
    *Human review required before merging*
    ```
    
    ### Step 5: Update MongoDB
    - Update ux_issue: status="PR_OPENED", pr_url=<url>, pr_number=<num>
    - Create record in 'pull_requests' collection
    """,
    
    expected_output="""
    A JSON summary containing:
    - Number of PRs created
    - PR URLs
    - Status updates
    
    Example:
    {
        "prs_created": 1,
        "pull_requests": [
            {
                "issue_id": "ux_issue_001",
                "pr_number": 42,
                "pr_url": "https://github.com/owner/repo/pull/42",
                "title": "🧬 Darwin Fix: Add to Cart button touch target"
            }
        ]
    }
    """,
    
    agent=create_engineer_agent(),
    context=[analyze_issues_task]  # Depends on issues being analyzed
)
```

---

### 7.5 Darwin Crew (Main Orchestration)

```python
# src/crew/darwin_crew.py

from crewai import Crew, Process
from src.agents.watcher import create_watcher_agent
from src.agents.analyst import create_analyst_agent
from src.agents.engineer import create_engineer_agent
from src.tasks.all_tasks import (
    detect_signals_task,
    analyze_issues_task,
    create_fixes_task
)
from rich.console import Console
from rich.panel import Panel

console = Console()

def create_darwin_crew(skip_engineer: bool = False) -> Crew:
    """
    Create the Darwin Crew - the full autonomous pipeline.
    
    Args:
        skip_engineer: If True, stops after analysis (for human approval flow)
    
    Returns:
        Configured Crew ready to kickoff
    """
    
    # Define agents
    watcher = create_watcher_agent()
    analyst = create_analyst_agent()
    engineer = create_engineer_agent()
    
    # Define tasks based on mode
    if skip_engineer:
        # Human-in-the-loop: Stop after analysis
        agents = [watcher, analyst]
        tasks = [detect_signals_task, analyze_issues_task]
    else:
        # Full auto: Run all three
        agents = [watcher, analyst, engineer]
        tasks = [detect_signals_task, analyze_issues_task, create_fixes_task]
    
    # Create the crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,  # Run in order
        verbose=True,
        memory=True,
        cache=True,
        max_rpm=10,  # Rate limiting for API calls
        share_crew=False
    )
    
    return crew


def run_darwin(mode: str = "full") -> dict:
    """
    Run the Darwin pipeline.
    
    Args:
        mode: 
            - "full": Run all agents (Watcher → Analyst → Engineer)
            - "detect": Only run Watcher (detect signals)
            - "analyze": Run Watcher + Analyst (detect + analyze)
            - "engineer": Only run Engineer (for approved tasks)
    
    Returns:
        Result dict with outputs from each agent
    """
    
    console.print(Panel.fit(
        "[bold blue]🧬 DARWIN[/bold blue] - The Self-Evolving Product Engine\n"
        f"[dim]Mode: {mode}[/dim]",
        border_style="blue"
    ))
    
    if mode == "full":
        crew = create_darwin_crew(skip_engineer=False)
        console.print("\n[yellow]▶ Running full pipeline: Watcher → Analyst → Engineer[/yellow]\n")
        
    elif mode == "analyze":
        crew = create_darwin_crew(skip_engineer=True)
        console.print("\n[yellow]▶ Running analysis: Watcher → Analyst (awaiting approval)[/yellow]\n")
        
    elif mode == "engineer":
        # Special mode: Only run Engineer for approved tasks
        engineer = create_engineer_agent()
        crew = Crew(
            agents=[engineer],
            tasks=[create_fixes_task],
            process=Process.sequential,
            verbose=True
        )
        console.print("\n[yellow]▶ Running Engineer for approved tasks[/yellow]\n")
        
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    # 🚀 Kickoff!
    result = crew.kickoff()
    
    console.print(Panel.fit(
        "[bold green]✅ Darwin Complete![/bold green]",
        border_style="green"
    ))
    
    return result


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    result = run_darwin(mode=mode)
    print(result)
```

---

### 7.6 Main Entry Script

```python
# scripts/run_darwin.py

#!/usr/bin/env python3
"""
🧬 DARWIN - Main Entry Point

Usage:
    python scripts/run_darwin.py              # Run full pipeline
    python scripts/run_darwin.py analyze      # Stop before PR (await approval)
    python scripts/run_darwin.py engineer     # Only create PRs for approved tasks
    python scripts/run_darwin.py demo         # Run demo with seed data
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.crew.darwin_crew import run_darwin
from src.config.settings import settings
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def print_banner():
    """Print Darwin ASCII banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗  █████╗ ██████╗ ██╗    ██╗██╗███╗   ██╗            ║
    ║   ██╔══██╗██╔══██╗██╔══██╗██║    ██║██║████╗  ██║            ║
    ║   ██║  ██║███████║██████╔╝██║ █╗ ██║██║██╔██╗ ██║            ║
    ║   ██║  ██║██╔══██║██╔══██╗██║███╗██║██║██║╚██╗██║            ║
    ║   ██████╔╝██║  ██║██║  ██║╚███╔███╔╝██║██║ ╚████║            ║
    ║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝            ║
    ║                                                               ║
    ║   🧬 The Self-Evolving Product Engine                         ║
    ║   "Darwin doesn't just REPORT the weather. It FIXES the roof" ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")

def print_config():
    """Print current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("PostHog Project", settings.POSTHOG_PROJECT_ID)
    table.add_row("GitHub Repo", f"{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}")
    table.add_row("MongoDB", settings.MONGODB_URI.split("@")[-1] if "@" in settings.MONGODB_URI else "localhost")
    table.add_row("LLM", "Gemini Pro")
    
    console.print(table)
    console.print()

def main():
    """Main entry point."""
    print_banner()
    print_config()
    
    # Parse mode from command line
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if mode == "demo":
        console.print("[yellow]📦 Loading demo data...[/yellow]")
        from scripts.seed_data import seed_demo_data
        seed_demo_data()
        mode = "full"
    
    if mode == "help":
        console.print(__doc__)
        return
    
    # Run Darwin!
    try:
        result = run_darwin(mode=mode)
        
        console.print("\n")
        console.print(Panel.fit(
            f"[bold green]🎉 Success![/bold green]\n\n{result}",
            title="Darwin Result",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ Error:[/bold red]\n\n{str(e)}",
            title="Darwin Error",
            border_style="red"
        ))
        raise

if __name__ == "__main__":
    main()
```

---

## 8. Darwin REST API

> **NEW (Feb 7, 2026)**: A FastAPI layer between MongoDB and NitroStack for secure data access.

### 8.1 Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DARWIN REST API                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  URL: http://localhost:8000                                     │
│  Auth: Bearer Token (DARWIN_API_KEY)                            │
│  Docs: http://localhost:8000/docs                               │
│                                                                  │
│  Why?                                                            │
│  • NitroStack connects to API, not directly to MongoDB          │
│  • Single API key for authentication                            │
│  • Centralized data access control                              │
│  • Easier to add caching, rate limiting                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 API Endpoints

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Public** | `/` | GET | API info |
| **Public** | `/health` | GET | Health check |
| **Public** | `/docs` | GET | Swagger UI |
| **Signals** | `/api/signals/` | GET | Get friction signals |
| **Signals** | `/api/signals/summary/by-severity` | GET | Signals by severity |
| **UX Issues** | `/api/ux-issues/` | GET | Get UX issues |
| **UX Issues** | `/api/ux-issues/pending-review` | GET | Issues pending review |
| **UX Issues** | `/api/ux-issues/{id}/approve` | POST | Approve a fix |
| **UX Issues** | `/api/ux-issues/{id}/reject` | POST | Reject a fix |
| **PRs** | `/api/pull-requests/` | GET | Get pull requests |
| **PRs** | `/api/pull-requests/summary/stats` | GET | PR statistics |
| **Darwin** | `/api/darwin/run` | POST | Trigger pipeline |
| **Darwin** | `/api/darwin/status` | GET | Pipeline status |
| **Stats** | `/api/stats/` | GET | Dashboard stats |
| **Stats** | `/api/stats/insights` | GET | AI insights |
| **Stats** | `/api/stats/agent-logs` | GET | Agent activity |

### 8.3 Quick Start

```bash
# Start Darwin API
cd /Users/heena/Desktop/Hackathon/darwin-multi-agent
source venv/bin/activate
python scripts/run_api.py

# Test endpoints
API_KEY="darwin_sk_6hhy8503b6m96nmuv5w84pu5ey5ex8hp"

# Get signals
curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/api/signals/

# Get UX issues
curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/api/ux-issues/

# Approve a fix
curl -X POST -H "Authorization: Bearer $API_KEY" http://localhost:8000/api/ux-issues/{id}/approve
```

---

## 9. Implementation Phases

### Phase 0: Environment Setup ✅ COMPLETE

| Task | Status | Notes |
|------|--------|-------|
| MongoDB Atlas | ✅ | Cloud DB configured |
| Create database | ✅ | `darwin` database |
| Create collections | ✅ | 8 collections |
| Python venv | ✅ | 3.11+ |

### Phase 1: Project Structure & Config ✅ COMPLETE

| Task | Status | File(s) |
|------|--------|---------|
| Create folder structure | ✅ | See Section 2.2 |
| Set up Python venv | ✅ | `python -m venv venv` |
| Install dependencies | ✅ | `pip install -r requirements.txt` |
| Create settings module | ✅ | `src/config/settings.py` |
| Create .env file | ✅ | `.env` with all API keys |

### Phase 2: Data Models & MongoDB ✅ COMPLETE

| Task | Status | File(s) |
|------|--------|---------|
| Create enum definitions | ✅ | `src/models/enums.py` |
| Create Signal model | ✅ | `src/models/signal.py` |
| Create UXIssue model | ✅ | `src/models/ux_issue.py` |
| Create MongoDB client | ✅ | `src/db/mongodb.py` |

### Phase 3: CrewAI Custom Tools ✅ COMPLETE

| Task | Status | File(s) |
|------|--------|---------|
| Create PostHogQueryTool | ✅ | `src/tools/posthog_tools.py` |
| Create GitHubReadTool | ✅ | `src/tools/github_tools.py` |
| Create GitHubPRTool | ✅ | `src/tools/github_tools.py` (patch-based) |
| Create MongoDBReadTool | ✅ | `src/tools/mongodb_tools.py` |
| Create MongoDBWriteTool | ✅ | `src/tools/mongodb_tools.py` |

### Phase 4: CrewAI Agents ✅ COMPLETE

| Task | Status | File(s) |
|------|--------|---------|
| Create Watcher Agent | ✅ | `src/agents/watcher.py` |
| Create Analyst Agent | ✅ | `src/agents/analyst.py` |
| Create Engineer Agent | ✅ | `src/agents/engineer.py` |

### Phase 5: CrewAI Tasks & Crew ✅ COMPLETE

| Task | Status | File(s) |
|------|--------|---------|
| Create all tasks | ✅ | `src/tasks/all_tasks.py` |
| Create Darwin Crew | ✅ | `src/crew/darwin_crew.py` |
| Create main entry script | ✅ | `scripts/run_darwin.py` |

### Phase 5.5: Darwin REST API ✅ COMPLETE (NEW)

| Task | Status | File(s) |
|------|--------|---------|
| Create FastAPI app | ✅ | `api/main.py` |
| Add API key auth | ✅ | `api/middleware/auth.py` |
| Create routes | ✅ | `api/routes/*.py` |
| Create API runner | ✅ | `scripts/run_api.py` |
| Test all endpoints | ✅ | 15 endpoints verified |

### Phase 6: darwin-acceleration-engine / NitroStack ⬜ NEXT

| Task | Status | Description |
|------|--------|-------------|
| 6.1 | ⬜ | Initialize NitroStack project |
| 6.2 | ⬜ | Set up Darwin API connection (NOT MongoDB) |
| 6.3 | ⬜ | Create tools that call Darwin API |
| 6.4 | ⬜ | Create widgets (signals-dashboard, decision-center) |
| 6.5 | ⬜ | Test in NitroStudio |

### Phase 7: Integration Testing ⬜ PENDING

| Task | Status | Description |
|------|--------|-------------|
| 7.1 | ⬜ | Generate test data in Luxora |
| 7.2 | ⬜ | Run full Darwin pipeline |
| 7.3 | ⬜ | Test NitroStack widgets |
| 7.4 | ⬜ | Verify PR creation |

### Phase 8: Demo Polish ⬜ PENDING

| Task | Status | Description |
|------|--------|-------------|
| 8.1 | ⬜ | Create demo script |
| 8.2 | ⬜ | Set up terminal layouts |
| 8.3 | Practice full demo 3x |
| 8.4 | Record backup video |

---

### Updated Time Estimates

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0: Setup | 30 min | 30 min |
| Phase 1: Project Structure | 1.5 hours | 2 hours |
| Phase 2: Models & MongoDB | 1 hour | 3 hours |
| Phase 3: CrewAI Tools | 2 hours | 5 hours |
| Phase 4: CrewAI Agents | 2 hours | 7 hours |
| Phase 5: Tasks & Crew | 1.5 hours | 8.5 hours |
| Phase 6: NitroStack | 2 hours | 10.5 hours |
| Phase 7: Bug & Integration | 1 hour | 11.5 hours |
| Phase 8: Demo Polish | 1 hour | 12.5 hours |

**Total: ~12-13 hours of focused work**

---

## 9. Bug Injection (Luxora)

### 8.1 File to Modify

**Repository:** `Luxora_ReactNative`  
**File:** `app/product/[id].tsx`  
**Line:** ~350 (in StyleSheet)

### 8.2 Current Code (Good)

```tsx
addToCartButton: {
  flex: 1,
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 10,
  backgroundColor: '#0f172a',
  paddingVertical: 16,    // ← Good: 16px padding
  borderRadius: 14,
},
```

### 8.3 Inject Bug (Change to this)

```tsx
addToCartButton: {
  flex: 1,
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 4,                 // ← Reduced
  backgroundColor: '#0f172a',
  paddingVertical: 6,     // ← BUG: Too small!
  paddingHorizontal: 8,   // ← BUG: Too small!
  borderRadius: 14,
},
```

### 8.4 Darwin's Fix (PR will change to)

```tsx
addToCartButton: {
  flex: 1,
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 10,
  backgroundColor: '#0f172a',
  paddingVertical: 16,     // ← Fixed
  paddingHorizontal: 24,   // ← Fixed
  borderRadius: 14,
  minHeight: 48,           // ← Added: Ensures touch target
},
```

---

## 10. Demo Flow

### 10.1 Demo Script (5 minutes)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DEMO SCRIPT                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SLIDE 1: THE PROBLEM (30 sec)                                              │
│  ─────────────────────────────                                              │
│  "Every product team has analytics showing WHERE users struggle.            │
│   But it takes WEEKS to actually fix it. We call this the                  │
│   'Insight-to-Action Latency' — and it's killing your PMF."                │
│                                                                              │
│  SLIDE 2: INTRODUCING DARWIN (30 sec)                                       │
│  ────────────────────────────────────                                       │
│  "We built Darwin — an Autonomous Growth Engineer powered by CrewAI.        │
│   Three AI agents working together:                                         │
│   🕵️ Watcher (Eyes) → 🧠 Analyst (Brain) → 👩‍💻 Engineer (Hands)              │
│   Darwin doesn't just REPORT the weather. It FIXES the roof."              │
│                                                                              │
│  LIVE DEMO (3 min)                                                          │
│  ─────────────────                                                          │
│                                                                              │
│  1. SHOW LUXORA APP (20 sec)                                               │
│     → Open product page                                                      │
│     → Point to Add to Cart button                                           │
│     → "This button has a UX issue - hard to tap"                           │
│                                                                              │
│  2. SHOW POSTHOG DASHBOARD (20 sec)                                        │
│     → "PostHog detected 234 rage clicks"                                    │
│     → Show session recording briefly                                        │
│                                                                              │
│  3. RUN DARWIN - ONE COMMAND! (2 min)                                      │
│     ┌────────────────────────────────────────────────────────────────┐     │
│     │ $ python scripts/run_darwin.py                                  │     │
│     │                                                                  │     │
│     │ ╔═══════════════════════════════════════════════════════════╗  │     │
│     │ ║   ██████╗  █████╗ ██████╗ ██╗    ██╗██╗███╗   ██╗        ║  │     │
│     │ ║   ██╔══██╗██╔══██╗██╔══██╗██║    ██║██║████╗  ██║        ║  │     │
│     │ ║   ██║  ██║███████║██████╔╝██║ █╗ ██║██║██╔██╗ ██║        ║  │     │
│     │ ║   ██║  ██║██╔══██║██╔══██╗██║███╗██║██║██║╚██╗██║        ║  │     │
│     │ ║   ██████╔╝██║  ██║██║  ██║╚███╔███╔╝██║██║ ╚████║        ║  │     │
│     │ ║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝        ║  │     │
│     │ ╚═══════════════════════════════════════════════════════════╝  │     │
│     │                                                                  │     │
│     │ ▶ Running full pipeline: Watcher → Analyst → Engineer          │     │
│     │                                                                  │     │
│     │ 🕵️ [WATCHER] Querying PostHog for rage clicks...               │     │
│     │ 🕵️ [WATCHER] Found 234 rage clicks on /product/[id]            │     │
│     │ 🕵️ [WATCHER] Signal saved: signal_001                          │     │
│     │                                                                  │     │
│     │ 🧠 [ANALYST] Analyzing signal_001...                            │     │
│     │ 🧠 [ANALYST] Fetching code from GitHub...                       │     │
│     │ 🧠 [ANALYST] Root cause: paddingVertical: 6 (32px < 48px min)  │     │
│     │ 🧠 [ANALYST] UX Issue created: ux_issue_001                     │     │
│     │                                                                  │     │
│     │ 👩‍💻 [ENGINEER] Processing approved task...                      │     │
│     │ 👩‍💻 [ENGINEER] Generating code fix...                           │     │
│     │ 👩‍💻 [ENGINEER] Creating branch: darwin/fix-add-to-cart         │     │
│     │ 👩‍💻 [ENGINEER] Committing changes...                            │     │
│     │ 👩‍💻 [ENGINEER] Opening Pull Request...                          │     │
│     │                                                                  │     │
│     │ ╔═══════════════════════════════════════════════════════════╗  │     │
│     │ ║  ✅ Darwin Complete!                                       ║  │     │
│     │ ║                                                            ║  │     │
│     │ ║  PR Created: github.com/heenakousarm-cloud/Luxora/pull/42 ║  │     │
│     │ ╚═══════════════════════════════════════════════════════════╝  │     │
│     └────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  4. THE MAGICAL MOMENT 🎉 (30 sec)                                         │
│     → Switch to GitHub                                                       │
│     → Refresh Luxora repo                                                   │
│     → BOOM — PR appears!                                                    │
│     → "🧬 Darwin Fix: Add to Cart button touch target"                     │
│     → Show the diff: paddingVertical 6 → 16                                │
│     → Show the beautiful PR description                                     │
│                                                                              │
│  SLIDE 3: WHY THIS MATTERS (30 sec)                                         │
│  ──────────────────────────────────                                         │
│  "What you just saw:                                                        │
│   - PostHog detected friction (rage clicks)                                 │
│   - Darwin's Watcher found the signal                                       │
│   - Darwin's Analyst diagnosed root cause                                   │
│   - Darwin's Engineer created the fix                                       │
│   All in ONE COMMAND. Weeks → Minutes.                                     │
│   And it's safe - humans still approve the PR."                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Terminal Setup for Demo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SINGLE TERMINAL - CLEAN & SIMPLE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  # Navigate to project                                                       │
│  cd /Users/heena/Desktop/Hackathon/darwin-multi-agent                       │
│                                                                              │
│  # Activate virtual environment                                              │
│  source venv/bin/activate                                                    │
│                                                                              │
│  # 🚀 Run Darwin - THE SINGLE COMMAND                                       │
│  python scripts/run_darwin.py                                                │
│                                                                              │
│  # Optional: Run with demo data                                              │
│  python scripts/run_darwin.py demo                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.3 Alternative: Human-in-the-Loop Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 HUMAN-IN-THE-LOOP FLOW (If time permits)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 1: Run detection & analysis only                                      │
│  ─────────────────────────────────────                                      │
│  $ python scripts/run_darwin.py analyze                                      │
│                                                                              │
│  → Watcher detects signal                                                    │
│  → Analyst creates UX Issue (status: PENDING)                               │
│  → STOPS HERE - awaiting human approval                                     │
│                                                                              │
│  STEP 2: Review in NitroStack                                               │
│  ────────────────────────────────                                           │
│  → Open NitroStudio                                                          │
│  → View UX Intelligence page                                                │
│  → Review the issue card                                                    │
│  → Click "Create Task" to approve                                           │
│  → Status changes to TASK_CREATED                                           │
│                                                                              │
│  STEP 3: Run engineer only                                                  │
│  ─────────────────────────────                                              │
│  $ python scripts/run_darwin.py engineer                                     │
│                                                                              │
│  → Engineer picks up approved task                                          │
│  → Creates PR                                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Quick Start Guide

### 11.1 Prerequisites

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] MongoDB Compass installed & running
- [ ] Git installed
- [ ] API Keys ready:
  - [ ] PostHog Personal API Key (`phx_*`)
  - [ ] GitHub Personal Access Token (`ghp_*`)
  - [ ] Google Gemini API Key (`AIza*`)

### 11.2 Step-by-Step Setup

```bash
# ═══════════════════════════════════════════════════════════════
# STEP 1: Navigate to hackathon folder
# ═══════════════════════════════════════════════════════════════
cd /Users/heena/Desktop/Hackathon

# ═══════════════════════════════════════════════════════════════
# STEP 2: Start MongoDB
# ═══════════════════════════════════════════════════════════════
# Open MongoDB Compass → Connect to localhost:27017
# Create Database → Name: "darwin"
# Create Collections: signals, ux_issues, tasks, pull_requests, agent_logs

# ═══════════════════════════════════════════════════════════════
# STEP 3: Set up darwin-multi-agent (CrewAI)
# ═══════════════════════════════════════════════════════════════
cd darwin-multi-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install CrewAI and all dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your actual API keys:
#   POSTHOG_PERSONAL_API_KEY=phx_...
#   POSTHOG_PROJECT_ID=289987
#   GITHUB_TOKEN=ghp_...
#   GITHUB_REPO_OWNER=heenakousarm-cloud
#   GITHUB_REPO_NAME=Luxora_ReactNative
#   GEMINI_API_KEY=AIza...
#   MONGODB_URI=mongodb://localhost:27017/darwin

# ═══════════════════════════════════════════════════════════════
# STEP 4: Test API Connections
# ═══════════════════════════════════════════════════════════════
python scripts/test_connections.py
# Should show: ✅ MongoDB OK, ✅ PostHog OK, ✅ GitHub OK, ✅ Gemini OK

# ═══════════════════════════════════════════════════════════════
# STEP 5: Set up darwin-acceleration-engine (NitroStack)
# ═══════════════════════════════════════════════════════════════
cd ../darwin-acceleration-engine
npm install
cp .env.example .env
# Edit .env with MongoDB URI

# ═══════════════════════════════════════════════════════════════
# STEP 6: Seed Demo Data (Optional - for testing)
# ═══════════════════════════════════════════════════════════════
cd ../darwin-multi-agent
source venv/bin/activate
python scripts/seed_data.py

# ═══════════════════════════════════════════════════════════════
# STEP 7: 🚀 RUN DARWIN!
# ═══════════════════════════════════════════════════════════════
python scripts/run_darwin.py

# Or with demo data:
python scripts/run_darwin.py demo

# Or step-by-step with human approval:
python scripts/run_darwin.py analyze  # Stops before PR
# ... approve in NitroStack ...
python scripts/run_darwin.py engineer  # Creates PR
```

### 11.3 Verify Installation

```bash
# Activate venv first
cd /Users/heena/Desktop/Hackathon/darwin-multi-agent
source venv/bin/activate

# ═══════════════════════════════════════════════════════════════
# Test MongoDB
# ═══════════════════════════════════════════════════════════════
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
print('✅ MongoDB:', client.darwin.list_collection_names())
"

# ═══════════════════════════════════════════════════════════════
# Test CrewAI
# ═══════════════════════════════════════════════════════════════
python -c "
from crewai import Agent, Task, Crew
print('✅ CrewAI imported successfully')
"

# ═══════════════════════════════════════════════════════════════
# Test Gemini via LangChain
# ═══════════════════════════════════════════════════════════════
python -c "
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=os.getenv('GEMINI_API_KEY'))
print('✅ Gemini:', llm.invoke('Say hello').content[:50])
"

# ═══════════════════════════════════════════════════════════════
# Test PostHog
# ═══════════════════════════════════════════════════════════════
python -c "
import requests
import os
from dotenv import load_dotenv
load_dotenv()
r = requests.get(
    f'https://us.posthog.com/api/projects/{os.getenv(\"POSTHOG_PROJECT_ID\")}',
    headers={'Authorization': f'Bearer {os.getenv(\"POSTHOG_PERSONAL_API_KEY\")}'}
)
print('✅ PostHog:', r.status_code, r.json().get('name', 'Connected'))
"

# ═══════════════════════════════════════════════════════════════
# Test GitHub
# ═══════════════════════════════════════════════════════════════
python -c "
from github import Github
import os
from dotenv import load_dotenv
load_dotenv()
g = Github(os.getenv('GITHUB_TOKEN'))
repo = g.get_repo(f'{os.getenv(\"GITHUB_REPO_OWNER\")}/{os.getenv(\"GITHUB_REPO_NAME\")}')
print('✅ GitHub:', repo.full_name)
"
```

### 11.4 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: crewai` | Run `pip install crewai crewai-tools` |
| `MongoDB connection refused` | Start MongoDB Compass first |
| `PostHog 401 Unauthorized` | Check `phx_` key (not `phc_`) |
| `GitHub 404 Not Found` | Check repo name and owner |
| `Gemini API error` | Verify API key is enabled |
| `CrewAI rate limit` | Add `max_rpm=10` to Crew config |

---

## 🎯 Success Criteria

- [ ] Watcher detects rage clicks from PostHog
- [ ] Analyst generates root cause analysis
- [ ] NitroStack displays UX Issue card
- [ ] "Create Task" tool updates MongoDB
- [ ] Engineer creates GitHub PR
- [ ] PR shows proper Darwin branding
- [ ] Demo runs smoothly end-to-end

---

## 🚀 Let's Build Darwin!

**Ready to start? The next step is creating the project files.**

---

*Document Version: 2.0 (CrewAI Integration)*  
*Last Updated: February 5, 2026*
