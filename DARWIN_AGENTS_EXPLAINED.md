# 🧬 Darwin Multi-Agent System - Deep Dive

Darwin uses **3 specialized AI agents** that work together in a sequential pipeline. Think of them as a **team of experts**, each with a specific role.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Agent 1: Watcher (The Eyes)](#-agent-1-watcher-the-eyes)
3. [Agent 2: Analyst (The Brain)](#-agent-2-analyst-the-brain)
4. [Agent 3: Engineer (The Hands)](#-agent-3-engineer-the-hands)
5. [The Complete Pipeline](#-the-complete-pipeline)
6. [Summary Table](#-summary-table)

---

## Overview

Darwin is an **AI Growth Engineer** that automatically:
1. **Detects** user friction from analytics (PostHog)
2. **Diagnoses** root causes by reading source code
3. **Fixes** issues by creating GitHub Pull Requests

All with **human-in-the-loop** approval before any changes go live.

---

## 🕵️ Agent 1: WATCHER (The Eyes)

### Role
**UX Friction Detector**

### What It Does
The Watcher is like a **24/7 security camera** monitoring user behavior. It:

1. **Queries PostHog** for friction signals:
   - 😤 **Rage clicks** - Users clicking the same element repeatedly (frustration!)
   - 📉 **Drop-offs** - Users abandoning pages/flows
   - ❌ **Error spikes** - Increased error rates
   - 🐌 **Slow loads** - Pages taking too long
   - 💀 **Dead clicks** - Clicks on non-interactive elements

2. **Classifies each signal** by:
   - Type (rage_click, drop_off, error_spike, etc.)
   - Severity (critical/high/medium/low)
   - Affected users count

3. **Saves signals to MongoDB** `signals` collection

### Tools It Uses

| Tool | Purpose |
|------|---------|
| `PostHogQueryTool` | Query rage clicks, events, drop-offs |
| `PostHogRecordingsTool` | Fetch session recordings |
| `MongoDBWriteTool` | Save detected signals |
| `MongoDBReadTool` | Check for existing signals |

### Code Location
```
src/agents/watcher.py
```

### Agent Configuration

```python
Agent(
    role="UX Friction Detector",
    goal="""
    Monitor PostHog analytics to detect UX friction signals that indicate 
    users are struggling. Look for:
    - Rage clicks (users clicking repeatedly in frustration)
    - High drop-off rates on key pages
    - Error spikes
    - Slow page loads
    - Dead clicks on non-interactive elements
    """,
    backstory="""
    You are Darwin's eyes - a vigilant UX analyst who never sleeps.
    You've analyzed millions of user sessions and can spot patterns 
    that indicate frustration instantly.
    """,
    tools=[PostHogQueryTool(), PostHogRecordingsTool(), MongoDBWriteTool(), MongoDBReadTool()],
    max_iter=10,
)
```

### Example Output

```
📊 Detected 3 friction signals:

┌────────────┬─────────────────────────────────┬──────────────────┐
│ Severity   │ Signal                          │ Affected Users   │
├────────────┼─────────────────────────────────┼──────────────────┤
│ CRITICAL   │ Rage clicks on Add to Cart      │ 47 users         │
│ HIGH       │ 65% drop-off on product page    │ 120 users        │
│ MEDIUM     │ Error spike in checkout flow    │ 12 users         │
└────────────┴─────────────────────────────────┴──────────────────┘

✅ Signals saved to MongoDB 'signals' collection
```

---

## 🧠 Agent 2: ANALYST (The Brain)

### Role
**UX Root Cause Analyst**

### What It Does
The Analyst is like a **detective** who investigates the crime scene. It:

1. **Reads unprocessed signals** from MongoDB
2. **Explores the codebase** via GitHub to find the problematic code
3. **Diagnoses the root cause**:
   - Small touch targets (`padding < 16` → hard to tap)
   - Missing press feedback (button doesn't respond visually)
   - No loading states (user doesn't know if action worked)
   - Confusing UI patterns

4. **Recommends specific fixes** with:
   - Exact file path (`app/product/[id].tsx`)
   - Line numbers to modify
   - Before/after code snippets

5. **Creates UX Issues** in MongoDB `ux_issues` collection

### Tools It Uses

| Tool | Purpose |
|------|---------|
| `GitHubReadTool` | Read source code files |
| `GitHubListFilesTool` | Explore codebase structure |
| `GetUnprocessedSignalsTool` | Get signals needing analysis |
| `MongoDBWriteTool` | Create UX issues |
| `MongoDBUpdateTool` | Mark signals as processed |

### Code Location
```
src/agents/analyst.py
```

### Domain Knowledge (Backstory)

The Analyst knows UX best practices:

| Guideline | Requirement |
|-----------|-------------|
| Touch targets | Min 44×44 pt (iOS) / 48×48 dp (Android) |
| Button feedback | Visual feedback on press required |
| Loading states | Must be clear and visible |
| Error messages | Should be helpful and actionable |

### Agent Configuration

```python
Agent(
    role="UX Root Cause Analyst",
    goal="""
    Analyze UX friction signals to identify root causes and recommend 
    specific code fixes. For each signal:
    1. Read the signal details from MongoDB
    2. Identify which file/component is likely causing the issue
    3. Read the relevant source code from GitHub
    4. Diagnose the root cause
    5. Recommend a specific code fix with exact changes needed
    """,
    backstory="""
    You are Darwin's brain - a senior UX engineer with deep expertise 
    in React Native, mobile UX patterns, and accessibility guidelines.
    You follow these principles:
    - Touch targets should be at least 44x44 points (iOS) / 48x48 dp (Android)
    - Buttons need visual feedback on press
    - Loading states should be communicated clearly
    """,
    tools=[GitHubReadTool(), GitHubListFilesTool(), MongoDBReadTool(), ...],
    max_iter=15,
)
```

### Example Output

```
🔍 Root Cause Analysis Report
═══════════════════════════════════════════════════════════════

Signal: CRITICAL - Rage clicks on "Add to Cart" button
File: app/product/[id].tsx (lines 480-495)

┌─────────────────────────────────────────────────────────────┐
│ ROOT CAUSE                                                   │
├─────────────────────────────────────────────────────────────┤
│ Button padding is only 16px vertical, making the touch      │
│ target approximately 48px. On edge taps, users miss the     │
│ button and rage click out of frustration.                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ RECOMMENDED FIX                                              │
├─────────────────────────────────────────────────────────────┤
│ File: app/product/[id].tsx                                  │
│ Line: 485                                                    │
│                                                              │
│ BEFORE:                                                      │
│   addToCartButton: {                                         │
│     paddingVertical: 16,                                     │
│   }                                                          │
│                                                              │
│ AFTER:                                                       │
│   addToCartButton: {                                         │
│     paddingVertical: 20,                                     │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘

Confidence: 92%
User Impact: 47 users currently affected
Business Impact: Potential lost sales from frustrated users

✅ UX Issue created in MongoDB 'ux_issues' collection
✅ Original signal marked as processed
```

---

## 👩‍💻 Agent 3: ENGINEER (The Hands)

### Role
**Autonomous Code Fixer**

### What It Does
The Engineer is like a **skilled developer** who implements the fix. It:

1. **Reads diagnosed UX issues** from MongoDB
2. **Fetches the current file** from GitHub
3. **Applies the recommended fix** to the code:
   - Makes exact changes specified
   - Preserves existing code style
   - Doesn't break anything else

4. **Creates a GitHub Pull Request** with:
   - Title: `🧬 Darwin Fix: [Issue Title]`
   - Detailed description (issue, root cause, changes, impact)
   - Proper branch: `darwin/fix-add-to-cart-button-1738XXX`

5. **Updates MongoDB** with PR details

### Tools It Uses

| Tool | Purpose |
|------|---------|
| `GitHubReadTool` | Read current file content |
| `GitHubPRTool` | Create branches and PRs |
| `GetPendingTasksTool` | Get tasks to work on |
| `MongoDBWriteTool` | Save PR records |
| `MongoDBUpdateTool` | Update task status |

### Code Location
```
src/agents/engineer.py
```

### Coding Principles (Backstory)

The Engineer follows strict coding standards:

- ✅ Match existing code style exactly
- ✅ Make minimal changes to fix the issue
- ✅ Preserve all existing functionality
- ✅ Add comments only when necessary
- ✅ Follow React Native best practices
- ✅ Write clear PR descriptions for reviewers

### Agent Configuration

```python
Agent(
    role="Autonomous Code Fixer",
    goal="""
    Implement code fixes and create GitHub Pull Requests. For each task:
    1. Read the pending task from MongoDB
    2. Read the current file content from GitHub
    3. Apply the recommended fix to the code
    4. Create a GitHub Pull Request with clear title and description
    5. Save the PR details to MongoDB
    """,
    backstory="""
    You are Darwin's hands - a senior React Native engineer who writes 
    clean, production-ready code. You've shipped code to millions of users.
    When creating PRs, you write clear descriptions that help reviewers 
    understand what changed and why.
    """,
    tools=[GitHubReadTool(), GitHubPRTool(), MongoDBWriteTool(), ...],
    max_iter=15,
)
```

### Example Output

```
✅ Pull Request Created!
═══════════════════════════════════════════════════════════════

PR #23: 🧬 Darwin Fix: Increase Add to Cart button touch target
URL: https://github.com/heenakousarm-cloud/Luxora_ReactNative/pull/23
Branch: darwin/fix-add-to-cart-1738780000

┌─────────────────────────────────────────────────────────────┐
│ CHANGES MADE                                                 │
├─────────────────────────────────────────────────────────────┤
│ File: app/product/[id].tsx                                  │
│                                                              │
│ - paddingVertical: 16,                                       │
│ + paddingVertical: 20,                                       │
│                                                              │
│ Touch target increased from 48px to 56px                    │
│ (Above 48dp Android minimum ✓)                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PR DESCRIPTION                                               │
├─────────────────────────────────────────────────────────────┤
│ ## 🐛 Issue                                                  │
│ Users experiencing rage clicks on Add to Cart button        │
│                                                              │
│ ## 🔍 Root Cause                                             │
│ Touch target too small (48px < 48dp minimum)                │
│                                                              │
│ ## ✨ Fix                                                    │
│ Increased paddingVertical from 16 to 20                     │
│                                                              │
│ ## 📊 Impact                                                 │
│ 47 users affected → Expected 0 after fix                    │
└─────────────────────────────────────────────────────────────┘

✅ PR record saved to MongoDB 'pull_requests' collection
✅ UX Issue status updated to 'pr_created'

🎉 Ready for human review!
```

---

## 🔄 The Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DARWIN PIPELINE                              │
│                                                                      │
│  "From friction detected → to PR ready for review"                  │
└─────────────────────────────────────────────────────────────────────┘

     📊 PostHog                                              📂 GitHub
     (Analytics)                                             (Code Repo)
          │                                                       │
          │ Rage clicks                                          │
          │ Drop-offs                                            │
          │ Errors                                               │
          ▼                                                       │
    ┌───────────────┐                                            │
    │  🕵️ WATCHER   │                                            │
    │               │                                            │
    │  "I found 47  │                                            │
    │   rage clicks │                                            │
    │   on Add to   │                                            │
    │   Cart!"      │                                            │
    └───────┬───────┘                                            │
            │                                                     │
            │ Saves signals                                       │
            ▼                                                     │
    ┌───────────────┐     Reads code                             │
    │  🧠 ANALYST   │◄────────────────────────────────────────────┤
    │               │                                            │
    │  "Root cause  │                                            │
    │   is small    │                                            │
    │   padding -   │                                            │
    │   16px only"  │                                            │
    └───────┬───────┘                                            │
            │                                                     │
            │ Creates UX issues                                   │
            ▼                                                     │
    ┌───────────────┐     Creates PR                             │
    │ 👩‍💻 ENGINEER  │─────────────────────────────────────────────►
    │               │                                            │
    │  "Here's the  │                                            │
    │   fix + PR    │                                            │
    │   #23"        │                                            │
    └───────┬───────┘                                            │
            │                                                     │
            │ All data flows through                              │
            ▼                                                     │
┌─────────────────────────────────────────────────────────────────────┐
│                           MongoDB                                    │
│                                                                      │
│   signals ──────► ux_issues ──────► tasks ──────► pull_requests     │
│                                                                      │
│   (detected)      (diagnosed)      (approved)     (created)         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
                    ┌─────────────────┐
                    │                 │
                    │   👤 HUMAN      │
                    │                 │
                    │   Reviews PR    │
                    │   ✅ Approves   │
                    │   🚀 Merges     │
                    │                 │
                    └─────────────────┘
```

---

## 📊 Summary Table

| Agent | Emoji | Role | Input | Output | Max Iterations |
|-------|-------|------|-------|--------|----------------|
| **Watcher** | 🕵️ | UX Friction Detector | PostHog analytics | Signals in MongoDB | 10 |
| **Analyst** | 🧠 | Root Cause Analyst | Signals + Source Code | UX Issues with fixes | 15 |
| **Engineer** | 👩‍💻 | Autonomous Code Fixer | UX Issues + Code | GitHub Pull Request | 15 |

---

## 🛠️ Tools Summary

### PostHog Tools (Watcher)
| Tool | Description |
|------|-------------|
| `PostHogQueryTool` | Query events, rage clicks, funnels using HogQL |
| `PostHogRecordingsTool` | Fetch session recording URLs |

### GitHub Tools (Analyst & Engineer)
| Tool | Description |
|------|-------------|
| `GitHubReadTool` | Read file contents from repository |
| `GitHubListFilesTool` | List files in a directory |
| `GitHubPRTool` | Create branches and pull requests |
| `GitHubCheckBranchTool` | Check if branch exists |

### MongoDB Tools (All Agents)
| Tool | Description |
|------|-------------|
| `MongoDBReadTool` | Query documents from collections |
| `MongoDBWriteTool` | Insert new documents |
| `MongoDBUpdateTool` | Update existing documents |
| `MongoDBFindByIdTool` | Find document by ID |
| `GetUnprocessedSignalsTool` | Get signals with `processed=false` |
| `GetPendingTasksTool` | Get tasks with `status=pending` |

---

## 🚀 Running the Pipeline

### Full Pipeline (All 3 Agents)
```bash
cd darwin-multi-agent
source venv/bin/activate
python scripts/run_darwin.py --mode full
```

### Individual Modes
```bash
# Only Watcher (detect signals)
python scripts/run_darwin.py --mode watch

# Watcher + Analyst (detect + analyze)
python scripts/run_darwin.py --mode analyze

# Full pipeline with seeded data
python scripts/run_darwin.py --mode seed
```

---

## 📁 File Structure

```
darwin-multi-agent/
├── src/
│   ├── agents/
│   │   ├── watcher.py      # 🕵️ Watcher Agent
│   │   ├── analyst.py      # 🧠 Analyst Agent
│   │   └── engineer.py     # 👩‍💻 Engineer Agent
│   ├── tools/
│   │   ├── posthog_tools.py   # PostHog API tools
│   │   ├── github_tools.py    # GitHub API tools
│   │   └── mongodb_tools.py   # MongoDB tools
│   ├── tasks/
│   │   └── all_tasks.py    # Task definitions
│   ├── crew/
│   │   └── darwin_crew.py  # Crew orchestration
│   └── models/
│       ├── signal.py       # Signal data model
│       ├── ux_issue.py     # UX Issue data model
│       ├── task.py         # Task data model
│       └── pull_request.py # PR data model
└── scripts/
    └── run_darwin.py       # CLI entry point
```

---

## 🎯 Key Takeaways

1. **Specialized Agents**: Each agent has a focused role with specific tools
2. **Sequential Pipeline**: Watcher → Analyst → Engineer (data flows through MongoDB)
3. **Human-in-the-Loop**: PRs require human approval before merging
4. **Full Automation**: From friction detection to PR creation is fully automated
5. **Transparency**: Clear logging and MongoDB records for audit trail

---

*Darwin: Your AI Growth Engineer* 🧬
