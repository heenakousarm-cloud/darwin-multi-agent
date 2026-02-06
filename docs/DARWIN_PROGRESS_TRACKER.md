# 🧬 Darwin - Implementation Progress Tracker

> **Track your progress through each implementation phase**  
> Mark items with `[x]` as you complete them

**Started:** February 5, 2026  
**Target Completion:** February 8, 2026  
**Team:** heenakousarm-cloud, anands@wekancode.com

---

## 📊 Overall Progress

| Phase | Status | Progress | Time Spent |
|-------|--------|----------|------------|
| Phase 0: Environment Setup | ✅ Complete | 100% | ~20 min |
| Phase 1: Project Structure | ✅ Complete | 100% | ~25 min |
| Phase 2: Data Models | ✅ Complete | 100% | ~15 min |
| Phase 3: CrewAI Tools | ✅ Complete | 100% | ~20 min |
| Phase 4: CrewAI Agents | ✅ Complete | 100% | ~10 min |
| Phase 5: Tasks & Crew | ✅ Complete | 100% | ~15 min |
| Phase 5.5: Darwin REST API | ✅ Complete | 100% | ~3 hrs |
| Phase 6: NitroStack MCP Server | ⬜ Not Started | 0% | - |
| Phase 7: Integration Testing | ⬜ Not Started | 0% | - |
| Phase 8: Demo Polish | ⬜ Not Started | 0% | - |

**Status Legend:**
- ⬜ Not Started
- 🟡 In Progress
- ✅ Complete
- ⏸️ Blocked
- ❌ Skipped

---

## Phase 0: Environment Setup
**Estimated Time:** 30 minutes  
**Actual Time:** ~20 minutes  
**Status:** ✅ Complete

### Prerequisites Check
- [x] Python 3.11+ installed → Version: 3.11.14
- [x] Node.js 18+ installed → Version: v24.10.0
- [x] MongoDB Compass installed
- [x] Git installed → Version: 2.51.1

### MongoDB Setup
- [x] MongoDB Compass opened
- [x] Connected to `localhost:27017` (later migrated to Atlas)
- [x] Created database: `darwin`
- [x] Created collection: `signals`
- [x] Created collection: `ux_issues`
- [x] Created collection: `tasks`
- [x] Created collection: `pull_requests`
- [x] Created collection: `agent_logs`
- [x] Created collection: `code_fixes`
- [x] Created collection: `product_metrics`
- [x] Created collection: `insights`
- [x] **Migrated to MongoDB Atlas** (cloud) for team collaboration

### API Keys Verification
- [x] PostHog Personal API Key (`phx_*`) - ✅ Connected to "Luxora" project
- [x] GitHub Personal Access Token (`ghp_*`) - ✅ Authenticated as heenakousarm-cloud
- [x] Gemini API Key (`AIza*`) - ✅ Working
- [x] Darwin API Key (`darwin_sk_*`) - ✅ Generated for NitroStack

**Phase 0 Notes:**
```
- Installed Python 3.11.14 via Homebrew
- Created 8 MongoDB collections in darwin database
- PostHog: Connected to Luxora project (ID: 289987)
- GitHub: Authenticated as heenakousarm-cloud
- Gemini: Key working after quota reset
- MongoDB: Migrated from local to Atlas for team access
- Darwin API Key: Generated for secure NitroStack integration
```

---

## Phase 1: Project Structure & Config
**Estimated Time:** 1.5 hours  
**Actual Time:** ~25 minutes  
**Status:** ✅ Complete

### 1.1 Create GitHub Repositories
- [x] Created `darwin-multi-agent` repository → https://github.com/heenakousarm-cloud/darwin-multi-agent
- [x] Created `darwin-acceleration-engine` repository → https://github.com/heenakousarm-cloud/darwin-acceleration-engine
- [x] Added collaborator: anand-shirahatti (anands@wekancode.com) - Invitation sent

### 1.2 darwin-multi-agent Folder Structure
- [x] Created `darwin-multi-agent/` folder
- [x] Created `src/` directory
- [x] Created `src/__init__.py`
- [x] Created `src/config/` directory
- [x] Created `src/config/__init__.py`
- [x] Created `src/models/` directory
- [x] Created `src/models/__init__.py`
- [x] Created `src/db/` directory
- [x] Created `src/db/__init__.py`
- [x] Created `src/tools/` directory
- [x] Created `src/tools/__init__.py`
- [x] Created `src/agents/` directory
- [x] Created `src/agents/__init__.py`
- [x] Created `src/tasks/` directory
- [x] Created `src/tasks/__init__.py`
- [x] Created `src/crew/` directory
- [x] Created `src/crew/__init__.py`
- [x] Created `scripts/` directory
- [x] Created `data/mock/` directory
- [x] Created `api/` directory (for Darwin REST API)
- [x] Created `docs/` directory (for documentation)

### 1.3 Python Environment
- [x] Created virtual environment: `python3.11 -m venv venv`
- [x] Activated venv: `source venv/bin/activate`
- [x] Created `requirements.txt`
- [x] Installed dependencies: `pip install -r requirements.txt`
- [x] Verified CrewAI: v1.9.3 ✅
- [x] Added FastAPI and Uvicorn for REST API

### 1.4 Configuration Files
- [x] Created `src/config/settings.py`
- [x] Created `.env.example`
- [x] Created `.env` (with actual keys)
- [x] Created `.gitignore`
- [x] Created `README.md`

### 1.5 Test Connections Script
- [x] Created `scripts/test_connections.py`
- [x] Tested MongoDB connection ✅ (8 collections)
- [x] Tested PostHog connection ✅ (Luxora project)
- [x] Tested GitHub connection ✅ (heenakousarm-cloud)
- [x] Tested Gemini connection ✅

**Phase 1 Notes:**
```
- Created GitHub repos: darwin-multi-agent, darwin-acceleration-engine
- Collaborator anand-shirahatti invited to both repos
- Python 3.11 venv with CrewAI 1.9.3 installed
- All configurations verified via test_connections.py
- MongoDB: 8 collections ready (now on Atlas)
- PostHog: Connected to Luxora (ID: 289987)
- GitHub: Access to Luxora_ReactNative repo
- Added api/ folder for Darwin REST API
- Added docs/ folder for all documentation
```

---

## Phase 2: Data Models & MongoDB
**Estimated Time:** 1 hour  
**Actual Time:** ~15 minutes  
**Status:** ✅ Complete

### 2.1 Enums
- [x] Created `src/models/enums.py`
- [x] Defined `SignalType` enum (7 types)
- [x] Defined `Severity` enum (4 levels)
- [x] Defined `SignalStatus` enum (5 states)
- [x] Defined `UXIssueStatus` enum (10 states)
- [x] Defined `TaskPriority` enum (4 levels)
- [x] Defined `AgentType` enum (3 agents)
- [x] Added `TaskStatus`, `PRStatus`, `LogLevel` enums
- [x] Added severity thresholds constants

### 2.2 Pydantic Models
- [x] Created `src/models/signal.py` (Signal model)
- [x] Created `src/models/ux_issue.py` (UXIssue + RecommendedFix models)
- [x] Created `src/models/task.py` (Task model)
- [x] Created `src/models/pull_request.py` (PullRequest + FileChange models)
- [x] Updated `src/models/__init__.py` with all exports

### 2.3 MongoDB Client
- [x] Created `src/db/mongodb.py`
- [x] Implemented `get_database()` function
- [x] Implemented `get_collection()` function
- [x] Implemented CRUD helpers (insert_one, find_one, update_one, etc.)
- [x] Implemented specialized queries (get_unprocessed_signals, etc.)
- [x] Tested connection with models ✅
- [x] Added logging functions (log_agent_action, log_insight, etc.)

**Phase 2 Notes:**
```
- Created 9 enums for type safety
- Created 6 Pydantic models (Signal, UXIssue, Task, PullRequest, etc.)
- MongoDB client with full CRUD operations
- Specialized queries for agent pipeline
- All models tested with MongoDB serialization
- Added logging functions for comprehensive data tracking
```

---

## Phase 3: CrewAI Custom Tools
**Estimated Time:** 2 hours  
**Actual Time:** ~20 minutes  
**Status:** ✅ Complete

### 3.1 PostHog Tools
- [x] Created `src/tools/posthog_tools.py`
- [x] Implemented `PostHogQueryTool`
  - [x] Rage clicks query (with fallback to rapid clicks)
  - [x] Drop-offs query (funnel analysis)
  - [x] Events query
  - [x] Persons query
- [x] Implemented `PostHogRecordingsTool`
  - [x] Session recordings fetch
- [x] Tested PostHog tools instantiation ✅

### 3.2 GitHub Tools
- [x] Created `src/tools/github_tools.py`
- [x] Implemented `GitHubReadTool`
  - [x] File read with line numbers
- [x] Implemented `GitHubPRTool`
  - [x] Branch creation
  - [x] File update/create
  - [x] PR creation with labels
  - [x] **Patch-based approach** (original_code + suggested_code)
- [x] Implemented `GitHubCheckBranchTool`
- [x] Implemented `GitHubListFilesTool`
- [x] Tested GitHub tools ✅ (listed Luxora app directory)

### 3.3 MongoDB Tools
- [x] Created `src/tools/mongodb_tools.py`
- [x] Implemented `MongoDBReadTool` (query with JSON)
- [x] Implemented `MongoDBWriteTool` (insert with robust JSON parsing)
- [x] Implemented `MongoDBUpdateTool` (update by ID)
- [x] Implemented `MongoDBFindByIdTool`
- [x] Implemented `MongoDBCountTool`
- [x] Implemented `GetUnprocessedSignalsTool` (Watcher→Analyst)
- [x] Implemented `GetPendingTasksTool` (Engineer)
- [x] Tested MongoDB tools ✅ (write/read cycle working)

### 3.4 Tools Index
- [x] Updated `src/tools/__init__.py` with all exports
- [x] Created WATCHER_TOOLS, ANALYST_TOOLS, ENGINEER_TOOLS groups

**Phase 3 Notes:**
```
- Created 13 custom CrewAI tools total
- PostHog: 2 tools (query + recordings)
- GitHub: 4 tools (read, PR, check branch, list files)
- MongoDB: 7 tools (read, write, update, find, count + 2 convenience)
- All tools use Pydantic schemas for input validation
- Created tool groups for each agent type
- GitHub PR tool uses patch-based approach for LLM token efficiency
- MongoDB write tool has robust JSON parsing for LLM output
```

---

## Phase 4: CrewAI Agents
**Estimated Time:** 2 hours  
**Actual Time:** ~10 minutes  
**Status:** ✅ Complete

### 4.1 Watcher Agent (🕵️ Eyes)
- [x] Created `src/agents/watcher.py`
- [x] Defined role: "UX Friction Detector"
- [x] Defined goal (detect rage clicks, drop-offs, errors)
- [x] Defined backstory
- [x] Attached tools: PostHogQueryTool, PostHogRecordingsTool, MongoDBWriteTool, MongoDBReadTool
- [x] Set LLM: Gemini 2.0 Flash
- [x] Tested agent standalone ✅

### 4.2 Analyst Agent (🧠 Brain)
- [x] Created `src/agents/analyst.py`
- [x] Defined role: "UX Root Cause Analyst"
- [x] Defined goal (diagnose root cause, recommend fixes)
- [x] Defined backstory (React Native/UX expert)
- [x] Attached tools: GitHubReadTool, GitHubListFilesTool, MongoDBReadTool, MongoDBWriteTool, MongoDBUpdateTool, GetUnprocessedSignalsTool
- [x] Set LLM: Gemini 2.0 Flash
- [x] Tested agent standalone ✅
- [x] Added stricter guidelines for smaller, focused patches

### 4.3 Engineer Agent (👩‍💻 Hands)
- [x] Created `src/agents/engineer.py`
- [x] Defined role: "Autonomous Code Fixer"
- [x] Defined goal (implement fixes, create PRs)
- [x] Defined backstory (senior React Native engineer)
- [x] Attached tools: GitHubReadTool, GitHubPRTool, GitHubListFilesTool, MongoDBReadTool, MongoDBWriteTool, MongoDBUpdateTool, GetPendingTasksTool
- [x] Set LLM: Gemini 2.0 Flash
- [x] Tested agent standalone ✅
- [x] Uses patch-based PR creation approach

### 4.4 Agents Index
- [x] Updated `src/agents/__init__.py` with all exports
- [x] Created ALL_AGENTS_METADATA for easy access

**Phase 4 Notes:**
```
- Created 3 specialized agents with Gemini 2.0 Flash LLM
- Watcher: 4 tools for PostHog monitoring
- Analyst: 6 tools for root cause analysis (with stricter patch guidelines)
- Engineer: 7 tools for code fixes and PRs (patch-based approach)
- All agents have detailed goals and backstories
- Agents index created with metadata for logging
```

---

## Phase 5: CrewAI Tasks & Crew
**Estimated Time:** 1.5 hours  
**Actual Time:** ~15 minutes  
**Status:** ✅ Complete

### 5.1 Task Definitions
- [x] Created `src/tasks/all_tasks.py`
- [x] Defined `detect_signals_task`
  - [x] Description complete (7 detailed steps)
  - [x] Expected output defined
  - [x] Assigned to Watcher
- [x] Defined `analyze_issues_task`
  - [x] Description complete (4 detailed steps)
  - [x] Expected output defined
  - [x] Assigned to Analyst
  - [x] Context linked to detect_signals_task
  - [x] Stricter guidelines for patch generation
- [x] Defined `fix_and_pr_task`
  - [x] Description complete (5 detailed steps)
  - [x] Expected output defined
  - [x] Assigned to Engineer
  - [x] Context linked to analyze_issues_task
  - [x] Uses patch-based PR creation
- [x] Created TASK_METADATA for logging
- [x] Tested task creation ✅

### 5.2 Darwin Crew
- [x] Created `src/crew/darwin_crew.py`
- [x] Implemented `create_darwin_crew()` function
- [x] Implemented `run_darwin()` function
- [x] Supported modes: full, analyze, engineer, review
- [x] Added convenience functions (run_full_pipeline, run_analysis_only, run_engineer_only)
- [x] Tested all modes ✅

### 5.3 Main Entry Script
- [x] Created `scripts/run_darwin.py`
- [x] Added ASCII banner (beautiful Darwin logo)
- [x] Added config display (table format)
- [x] Added mode parsing (full, analyze, engineer, review)
- [x] Added error handling
- [x] Added --seed flag for demo data
- [x] Added --quiet flag for reduced output
- [x] Added human-in-the-loop approval for review mode
- [x] Added MongoDB logging functions
- [x] Tested help, config, and seed modes ✅

### 5.4 Full Pipeline Test
- [x] Script runs without errors
- [x] Config display works
- [x] Seed data works
- [x] Full pipeline tested ✅
- [x] PRs created successfully on GitHub

**Phase 5 Notes:**
```
- Created 3 detailed task definitions with clear descriptions
- Darwin Crew supports 4 modes: full, analyze, engineer, review
- Main entry script with beautiful ASCII banner
- Config display in table format
- Review mode has human-in-the-loop approval
- Full pipeline tested and working
- PRs successfully created on Luxora_ReactNative repo
```

---

## Phase 5.5: Darwin REST API (NEW)
**Estimated Time:** 3 hours  
**Actual Time:** ~3 hours  
**Status:** ✅ Complete

### 5.5.1 API Setup
- [x] Created `api/` directory structure
- [x] Created `api/__init__.py`
- [x] Created `api/main.py` (FastAPI app)
- [x] Added CORS middleware
- [x] Created `scripts/run_api.py` (API runner)

### 5.5.2 Authentication Middleware
- [x] Created `api/middleware/__init__.py`
- [x] Created `api/middleware/auth.py`
- [x] Implemented Bearer token authentication
- [x] Added `DARWIN_API_KEY` to settings
- [x] Protected all `/api/*` endpoints

### 5.5.3 API Routes
- [x] Created `api/routes/__init__.py`
- [x] Created `api/routes/signals.py`
  - [x] `GET /api/signals/` - List signals
  - [x] `GET /api/signals/{id}` - Get signal by ID
  - [x] `GET /api/signals/summary/by-severity` - Severity breakdown
- [x] Created `api/routes/ux_issues.py`
  - [x] `GET /api/ux-issues/` - List UX issues
  - [x] `GET /api/ux-issues/pending-review` - Pending issues
  - [x] `GET /api/ux-issues/{id}` - Get issue by ID
  - [x] `POST /api/ux-issues/{id}/approve` - Approve fix
  - [x] `POST /api/ux-issues/{id}/reject` - Reject fix
  - [x] `GET /api/ux-issues/summary/by-status` - Status breakdown
- [x] Created `api/routes/pull_requests.py`
  - [x] `GET /api/pull-requests/` - List PRs
  - [x] `GET /api/pull-requests/{id}` - Get PR by ID
  - [x] `GET /api/pull-requests/summary/stats` - PR statistics
- [x] Created `api/routes/darwin.py`
  - [x] `POST /api/darwin/run` - Trigger pipeline
  - [x] `GET /api/darwin/status` - Pipeline status
- [x] Created `api/routes/stats.py`
  - [x] `GET /api/stats/` - Dashboard statistics
  - [x] `GET /api/stats/insights` - AI insights
  - [x] `GET /api/stats/agent-logs` - Agent activity
  - [x] `GET /api/stats/product-metrics` - Product metrics

### 5.5.4 Testing
- [x] API starts correctly on http://localhost:8000
- [x] Swagger docs available at http://localhost:8000/docs
- [x] Health check works: `GET /health`
- [x] All public endpoints work without auth
- [x] All protected endpoints require Bearer token
- [x] All 15+ endpoints verified working ✅

**Phase 5.5 Notes:**
```
- Created FastAPI REST API for NitroStack integration
- API runs on http://localhost:8000
- Bearer token authentication with DARWIN_API_KEY
- 15+ endpoints covering signals, issues, PRs, stats
- Swagger UI at /docs for easy testing
- NitroStack will connect to this API (not direct MongoDB)
- This provides secure, centralized data access
```

---

## Phase 6: NitroStack MCP Server (darwin-acceleration-engine)
**Estimated Time:** 12-15 hours  
**Actual Time:** _______________  
**Status:** ⬜ Not Started

> **Reference:** See `docs/NITROSTACK_IMPLEMENTATION_PLAN.md` for detailed code examples

### 6.1 Project Setup (30 min)
- [ ] Navigate to Hackathon folder: `cd /Users/heena/Desktop/Hackathon`
- [ ] Initialize NitroStack: `npx nitrostack init darwin-acceleration-engine`
- [ ] Review generated template structure
- [ ] Create `.env` file with:
  - [ ] `DARWIN_API_URL=http://localhost:8000`
  - [ ] `DARWIN_API_KEY=darwin_sk_...`
  - [ ] `NITROSTACK_PORT=3000`
- [ ] Install additional dependencies:
  - [ ] `npm install zod`
  - [ ] `npm install framer-motion`
  - [ ] `npm install recharts`
  - [ ] `npm install -D @types/react`
- [ ] Update `nitrostack.config.ts` with Darwin theme

### 6.2 Darwin API Client (15 min)
- [ ] Create `src/lib/darwin-api.ts`
- [ ] Implement `DarwinApiClient` class
  - [ ] `get(path)` method
  - [ ] `post(path, body)` method
  - [ ] Bearer token authentication
- [ ] Export `darwinApi` instance
- [ ] Test API connection

### 6.3 Tools - Core MCP Feature #1 (2 hours)
- [ ] Create `src/tools/get-signals.ts`
  - [ ] `@Tool` decorator with description
  - [ ] Input schema with Zod
  - [ ] Calls `GET /api/signals/`
  - [ ] `@Widget('signals-dashboard')` attached
- [ ] Create `src/tools/get-ux-issues.ts`
  - [ ] `@Tool` decorator with description
  - [ ] Input schema with Zod
  - [ ] Calls `GET /api/ux-issues/`
  - [ ] `@Widget('decision-center')` attached
- [ ] Create `src/tools/approve-fix.ts`
  - [ ] `@Tool` decorator with description
  - [ ] Input schema (issue_id, create_pr_immediately)
  - [ ] Calls `POST /api/ux-issues/{id}/approve`
- [ ] Create `src/tools/reject-fix.ts`
  - [ ] `@Tool` decorator with description
  - [ ] Calls `POST /api/ux-issues/{id}/reject`
- [ ] Create `src/tools/get-pull-requests.ts`
  - [ ] `@Tool` decorator with description
  - [ ] Calls `GET /api/pull-requests/`
  - [ ] `@Widget('pr-viewer')` attached
- [ ] Create `src/tools/trigger-darwin.ts`
  - [ ] `@Tool` decorator with description
  - [ ] Input schema (mode: analyze/engineer/full)
  - [ ] Calls `POST /api/darwin/run`
- [ ] Create `src/tools/get-stats.ts`
  - [ ] Calls `GET /api/stats/`

### 6.4 Resources - Core MCP Feature #2 (1 hour)
- [ ] Create `src/resources/signals-resource.ts`
  - [ ] `@Resource` decorator for `darwin://signals`
  - [ ] `@Resource` decorator for `darwin://signals/critical`
- [ ] Create `src/resources/issues-resource.ts`
  - [ ] `@Resource` decorator for `darwin://issues`
  - [ ] `@Resource` decorator for `darwin://issues/pending`
- [ ] Create `src/resources/prs-resource.ts`
  - [ ] `@Resource` decorator for `darwin://pull-requests`

### 6.5 Prompts - Core MCP Feature #3 (30 min)
- [ ] Create `src/prompts/analyze-friction.ts`
  - [ ] `@Prompt` decorator
  - [ ] Template with {{signal}} placeholder
- [ ] Create `src/prompts/diagnose-issue.ts`
  - [ ] `@Prompt` decorator
  - [ ] Template with {{signal}}, {{file_path}}, {{code}} placeholders
- [ ] Create `src/prompts/generate-fix.ts`
  - [ ] `@Prompt` decorator
  - [ ] Template with {{issue_title}}, {{original_code}} placeholders

### 6.6 Middleware - Core MCP Features #4-7 (1 hour)
- [ ] Create `src/middleware/auth.ts`
  - [ ] `@Middleware` decorator
  - [ ] API key validation
  - [ ] Skip auth for health checks
- [ ] Create `src/middleware/logging.ts`
  - [ ] `@Middleware` decorator
  - [ ] Request/response logging
  - [ ] Duration tracking
- [ ] Create `src/middleware/rate-limit.ts`
  - [ ] `@Middleware` decorator
  - [ ] Rate limit headers
  - [ ] 100 requests per minute
- [ ] Create `src/lib/cache.ts`
  - [ ] Cache class with TTL
  - [ ] `cachedFind` helper
  - [ ] `invalidateCache` helper

### 6.7 Widgets - Core MCP Feature #8 (4 hours)

#### 6.7.1 Signals Dashboard Widget (1.5 hours)
- [ ] Create `src/widgets/signals-dashboard/SignalsDashboard.tsx`
- [ ] Implement Widget SDK features:
  - [ ] `useTheme` - Light/dark mode
  - [ ] `useWidgetState` - Persist selected signal
  - [ ] `callTool` - Chain to get_ux_issues
  - [ ] `sendFollowUpMessage` - Send analysis results
  - [ ] `openExternal` - Link to PostHog
  - [ ] `setDisplayMode` - Fullscreen support
- [ ] Implement UI components:
  - [ ] Header with signal count
  - [ ] View mode toggle (list/chart)
  - [ ] Severity badges (critical/high/medium/low)
  - [ ] Pie chart for severity distribution (Recharts)
  - [ ] Area chart for signals over time
  - [ ] Signal list with expand/collapse
  - [ ] Analyze and PostHog buttons
- [ ] Add animations with Framer Motion
- [ ] Add loading and error states
- [ ] Create `src/widgets/signals-dashboard/styles.css`

#### 6.7.2 Decision Center Widget - MOST IMPORTANT (2 hours)
- [ ] Create `src/widgets/decision-center/DecisionCenter.tsx`
- [ ] Implement Widget SDK features:
  - [ ] `useTheme` - Light/dark mode
  - [ ] `useWidgetState` - Current index, approved IDs
  - [ ] `callTool` - approve_fix, trigger_darwin
  - [ ] `sendFollowUpMessage` - Approval confirmation
  - [ ] `openExternal` - Link to GitHub
  - [ ] `setDisplayMode` - Fullscreen for code review
  - [ ] `showToast` - Success/error notifications
- [ ] Implement UI components:
  - [ ] Progress bar (current/total issues)
  - [ ] Issue header with priority badge
  - [ ] Confidence score display
  - [ ] Root cause panel
  - [ ] User impact panel
  - [ ] Code diff view (BEFORE/AFTER)
  - [ ] Approve Fix button
  - [ ] Approve & Create PR button
  - [ ] Skip button
  - [ ] Previous/Next navigation
- [ ] Create `src/widgets/decision-center/CodeDiff.tsx`
  - [ ] Split view mode
  - [ ] Unified view mode
  - [ ] Syntax highlighting
  - [ ] File name header
- [ ] Add animations with Framer Motion
- [ ] Add loading and error states
- [ ] Create `src/widgets/decision-center/styles.css`

#### 6.7.3 PR Viewer Widget (1 hour)
- [ ] Create `src/widgets/pr-viewer/PRViewer.tsx`
- [ ] Implement Widget SDK features:
  - [ ] `useTheme` - Light/dark mode
  - [ ] `useWidgetState` - Expanded PR
  - [ ] `openExternal` - Link to GitHub PR
  - [ ] `sendFollowUpMessage` - PR opened notification
- [ ] Implement UI components:
  - [ ] Stats cards (open/merged/closed)
  - [ ] PR list with status icons
  - [ ] Expandable PR details
  - [ ] Files changed list
  - [ ] Open in GitHub button
- [ ] Add animations with Framer Motion
- [ ] Create `src/widgets/pr-viewer/styles.css`

### 6.8 Main Entry Point (30 min)
- [ ] Update `src/index.ts`
- [ ] Import all tools (7)
- [ ] Import all resources (5)
- [ ] Import all prompts (3)
- [ ] Import all middleware (3)
- [ ] Import all widgets (3)
- [ ] Register tools with `server.registerTool()`
- [ ] Register resources with `server.registerResource()`
- [ ] Register prompts with `server.registerPrompt()`
- [ ] Register middleware with `server.use()`
- [ ] Register widgets with `server.registerWidget()`
- [ ] Add startup banner with counts

### 6.9 Testing in NitroStudio (1 hour)
- [ ] Start Darwin API: `python scripts/run_api.py`
- [ ] Start NitroStack: `npm run dev`
- [ ] Open NitroStudio: http://localhost:3000/studio
- [ ] Test `get_signals` tool
- [ ] Test `get_ux_issues` tool
- [ ] Test `approve_fix` tool
- [ ] Test `trigger_darwin` tool
- [ ] Test `get_pull_requests` tool
- [ ] Test signals-dashboard widget renders
- [ ] Test decision-center widget renders
- [ ] Test pr-viewer widget renders
- [ ] Test `callTool` from widget
- [ ] Test `openExternal` from widget
- [ ] Test light/dark theme toggle
- [ ] Test fullscreen mode

### 6.10 NitroStack Feature Coverage Checklist (22 Features)

#### Core MCP Features (8)
- [ ] #1: @Tool Decorators (7 tools)
- [ ] #2: @Widget Decorators (3 widgets)
- [ ] #3: Resources (5 resources)
- [ ] #4: Prompts (3 prompts)
- [ ] #5: Authentication (middleware)
- [ ] #6: Middleware (logging)
- [ ] #7: Caching (cache.ts)
- [ ] #8: Rate Limiting (middleware)

#### Widget SDK Features (8)
- [ ] #9: useTheme
- [ ] #10: callTool
- [ ] #11: sendFollowUpMessage
- [ ] #12: openExternal
- [ ] #13: useWidgetState
- [ ] #14: Display Modes (fullscreen)
- [ ] #15: Error Handling
- [ ] #16: Loading States

#### Visual/UX Features (6)
- [ ] #17: Code Diff View
- [ ] #18: Severity Badges
- [ ] #19: Interactive Buttons
- [ ] #20: Charts/Graphs (Recharts)
- [ ] #21: Animations (Framer Motion)
- [ ] #22: Toast Notifications

**Phase 6 Notes:**
```
(Add notes as you implement)


```

---

## Phase 7: Integration Testing
**Estimated Time:** 1 hour  
**Actual Time:** _______________  
**Status:** ⬜ Not Started

### 7.1 End-to-End Flow Test
- [ ] Clear MongoDB collections for fresh test
- [ ] Generate test data in Luxora app
- [ ] Start Darwin API: `python scripts/run_api.py`
- [ ] Start NitroStack: `npm run dev`
- [ ] Run Darwin analyze: `python scripts/run_darwin.py --mode analyze`
- [ ] Verify signals in MongoDB
- [ ] Verify UX issues in MongoDB
- [ ] Open NitroStudio
- [ ] View signals in signals-dashboard widget
- [ ] Review issue in decision-center widget
- [ ] Click "Approve & Create PR"
- [ ] Verify PR created on GitHub
- [ ] Check PR in pr-viewer widget

### 7.2 API Integration Test
- [ ] Test all Darwin API endpoints from NitroStack
- [ ] Verify authentication works
- [ ] Verify data flows correctly
- [ ] Test error handling

### 7.3 Widget Integration Test
- [ ] Test callTool from signals-dashboard
- [ ] Test callTool from decision-center
- [ ] Test openExternal links
- [ ] Test sendFollowUpMessage
- [ ] Test showToast notifications

**Phase 7 Notes:**
```
(Add notes as you test)


```

---

## Phase 8: Demo Polish
**Estimated Time:** 1 hour  
**Actual Time:** _______________  
**Status:** ⬜ Not Started

### 8.1 Demo Preparation
- [ ] Reviewed demo script (see HACKATHON_STATUS.md)
- [ ] Prepared slides (if needed)
- [ ] Set up terminal with correct directory
- [ ] Cleared old data from MongoDB
- [ ] Generated fresh test data

### 8.2 Demo Script (5 minutes)

**0:00 - 0:30 INTRO**
- [ ] Explain Darwin concept
- [ ] "AI Growth Engineer that detects UX friction and creates PRs"

**0:30 - 1:30 SHOW THE PROBLEM**
- [ ] Open Luxora app in simulator
- [ ] Show the "Add to Cart" button
- [ ] Demonstrate rage clicking (no feedback)
- [ ] Show PostHog dashboard with rage click data

**1:30 - 3:00 DARWIN IN ACTION**
- [ ] Open NitroStudio with Darwin MCP
- [ ] Say: "Show me UX issues in Luxora"
- [ ] Decision-center widget renders
- [ ] Show the diagnosed issue and recommended fix
- [ ] Click "Approve" button in widget

**3:00 - 4:00 PR CREATED**
- [ ] Show GitHub PR created by Darwin
- [ ] Review the code changes
- [ ] Merge the PR (optional)

**4:00 - 5:00 RESULT**
- [ ] Show the fixed app (button now has loading state)
- [ ] Recap: "From friction detected to PR merged in minutes"

### 8.3 Demo Run-Through
- [ ] Practice Run 1 completed
  - [ ] Timing: _____ minutes
  - [ ] Issues found: _______________
- [ ] Practice Run 2 completed
  - [ ] Timing: _____ minutes
  - [ ] Issues found: _______________
- [ ] Practice Run 3 completed
  - [ ] Timing: _____ minutes
  - [ ] All smooth ✅

### 8.4 Backup Plan
- [ ] Recorded backup video (optional)
- [ ] Screenshots of key moments saved
- [ ] Fallback demo data prepared

### 8.5 Final Checklist
- [ ] MongoDB Atlas connected
- [ ] All API keys working
- [ ] Darwin API running (port 8000)
- [ ] NitroStack running (port 3000)
- [ ] Terminal ready
- [ ] GitHub logged in
- [ ] NitroStudio open
- [ ] Luxora app ready to show

**Phase 8 Notes:**
```
(Add notes as you prepare)


```

---

## 🎯 Success Criteria Checklist

### Core Functionality
- [x] Watcher detects rage clicks from PostHog
- [x] Analyst generates root cause analysis with Gemini
- [x] Analyst produces specific code fix recommendation
- [x] Engineer creates GitHub PR automatically
- [x] PR has proper Darwin branding (🧬)
- [x] MongoDB stores all data correctly
- [x] Darwin REST API provides secure data access

### NitroStack Integration
- [ ] NitroStack connects to Darwin API
- [ ] All 7 tools working
- [ ] All 3 widgets rendering
- [ ] Human-in-the-loop approval via widget
- [ ] 22/22 NitroStack features demonstrated

### Demo Quality
- [ ] Single command runs full pipeline
- [ ] Terminal output is beautiful (rich library)
- [ ] Demo completes in under 5 minutes
- [ ] No errors during demo
- [ ] PR appears on GitHub as expected
- [ ] NitroStack widgets look professional

---

## 🐛 Issues & Blockers Log

| # | Issue | Status | Resolution |
|---|-------|--------|------------|
| 1 | Gemini rate limits | ✅ Resolved | Wait for quota reset / use new key |
| 2 | Engineer LLM token limit | ✅ Resolved | Implemented patch-based PR approach |
| 3 | Analyst generating large patches | ✅ Resolved | Added stricter guidelines |
| 4 | MongoDB local access for team | ✅ Resolved | Migrated to MongoDB Atlas |
| 5 | | | |

---

## 📝 Daily Notes

### Day 1 - February 5, 2026
**Hours Worked:** ~2 hours  
**Phases Completed:** 0-5  
**Notes:**
```
- Set up Python environment and CrewAI
- Created all agents, tools, and tasks
- Tested basic pipeline
- Hit Gemini rate limits
```

### Day 2 - February 6, 2026
**Hours Worked:** ~4 hours  
**Phases Completed:** 5 (refinements)  
**Notes:**
```
- Fixed Engineer agent token limit issue
- Implemented patch-based PR approach
- Added human-in-the-loop review mode
- Migrated MongoDB to Atlas
- Created comprehensive documentation
```

### Day 3 - February 7, 2026
**Hours Worked:** ~3 hours  
**Phases Completed:** 5.5 (Darwin REST API)  
**Notes:**
```
- Created Darwin REST API with FastAPI
- Implemented API key authentication
- Created 15+ endpoints
- Updated all documentation
- Ready for NitroStack implementation
```

### Day 4 - February 8, 2026
**Hours Worked:** _______________  
**Phases Completed:** _______________  
**Notes:**
```
(Add notes here)


```

---

## 🏁 Final Summary

**Total Time Spent:** ~9 hours (so far)  
**Phases Completed:** 6 / 9 (including 5.5)  
**Demo Ready:** ⬜ Not Yet (need NitroStack)  

**What Worked Well:**
```
- CrewAI agents work smoothly
- Patch-based PR approach solved token limit
- MongoDB Atlas enables team collaboration
- Darwin REST API provides clean interface for NitroStack
```

**What Could Be Improved:**
```
- Start NitroStack earlier
- Better error handling in agents
- More comprehensive test data
```

**Key Learnings:**
```
- LLM token limits require creative solutions
- API layer between systems improves security
- Documentation is crucial for team work
```

---

## 📚 Related Documentation

- [NITROSTACK_IMPLEMENTATION_PLAN.md](./NITROSTACK_IMPLEMENTATION_PLAN.md) - Detailed NitroStack code
- [HACKATHON_STATUS.md](./HACKATHON_STATUS.md) - Overall hackathon status
- [API_KEY_AUTHENTICATION.md](./API_KEY_AUTHENTICATION.md) - API security docs
- [DARWIN_AGENTS_EXPLAINED.md](./DARWIN_AGENTS_EXPLAINED.md) - Agent documentation

---

*Last Updated: February 7, 2026*
