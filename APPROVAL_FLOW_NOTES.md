# 🔐 Darwin Approval Flow - Implementation Notes

## Current State (Phase 7 - Integration Testing)

**Current Approach:** Terminal-based human-in-the-loop
- User runs `--mode review` in terminal
- Script displays issues and prompts for approval
- User types Y/N to approve/reject
- Approved issues get status updated to "approved"

**Why this for now:** Quick to test, ensures agents work correctly before adding UI layer.

---

## 🎯 Planned Change (Phase 6 - NitroStack)

### Target: MongoDB Status-Based Approval Flow

This approach is better for NitroStack because:
1. ✅ NitroStack widget can update MongoDB directly
2. ✅ No terminal interaction needed
3. ✅ Beautiful UI for reviewing code diffs
4. ✅ Multiple users can review simultaneously
5. ✅ Audit trail in MongoDB

---

## 📋 Implementation Plan

### Step 1: Update Analyst Agent Output

**File:** `src/agents/analyst.py` and `src/tasks/all_tasks.py`

**Change:** Analyst saves UX issues with status `"pending_approval"` instead of `"diagnosed"`

```python
# In analyze task, ensure issues are saved with:
{
    "status": "pending_approval",  # Changed from "diagnosed"
    "awaiting_human_review": True,
    "created_at": datetime.now().isoformat(),
    # ... other fields
}
```

### Step 2: Update Engineer Agent Filter

**File:** `src/tools/mongodb_tools.py` → `GetPendingTasksTool`

**Change:** Engineer only processes issues with status `"approved"`

```python
# Current:
query = {"status": "diagnosed"}  # or similar

# Change to:
query = {"status": "approved"}  # Only human-approved issues
```

### Step 3: NitroStack Widget Integration

**File:** `darwin-acceleration-engine/src/tools/approve-fix.ts`

**The `approve_fix` tool will:**
1. Find issue by ID in MongoDB
2. Validate status is `"pending_approval"`
3. Update status to `"approved"`
4. Optionally trigger Engineer agent

```typescript
// NitroStack approve_fix tool
@Tool({
  name: 'approve_fix',
  description: 'Approve a UX issue for PR creation',
})
export async function approveFix(input: { issue_id: string }) {
  // Update MongoDB status
  await mongodb.updateOne('ux_issues', 
    { _id: input.issue_id, status: 'pending_approval' },
    { $set: { 
      status: 'approved',
      approved_at: new Date().toISOString(),
      approved_by: 'human_via_nitrostack'
    }}
  );
  
  return { success: true, message: 'Issue approved for PR creation' };
}
```

### Step 4: DecisionCenter Widget

**File:** `darwin-acceleration-engine/src/widgets/decision-center/DecisionCenter.tsx`

**Features:**
- Shows issues with status `"pending_approval"`
- Displays code diff (before/after)
- "Approve" button calls `approve_fix` tool
- "Reject" button updates status to `"rejected"`
- "Approve & Create PR" triggers Engineer immediately

---

## 🔄 Status Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     DARWIN APPROVAL FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PostHog ──► Watcher ──► Signal (status: "new")                │
│                              │                                  │
│                              ▼                                  │
│              Analyst ──► UX Issue (status: "pending_approval") │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────┐         │
│  │         🧑‍💻 HUMAN REVIEW (NitroStack)              │         │
│  │                                                   │         │
│  │   DecisionCenter Widget shows:                    │         │
│  │   - Issue title & priority                        │         │
│  │   - Root cause analysis                           │         │
│  │   - Code diff (before/after)                      │         │
│  │   - [✅ Approve] [❌ Reject] [🚀 Approve & PR]    │         │
│  │                                                   │         │
│  └───────────────────────────────────────────────────┘         │
│                              │                                  │
│              ┌───────────────┼───────────────┐                 │
│              ▼               ▼               ▼                 │
│         "approved"      "rejected"    "needs_revision"         │
│              │                                                  │
│              ▼                                                  │
│  Engineer ──► PR Created (status: "pr_created")                │
│              │                                                  │
│              ▼                                                  │
│         GitHub PR #N opened                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 MongoDB Status Values

### Signal Statuses
| Status | Description |
|--------|-------------|
| `new` | Just detected by Watcher |
| `processing` | Being analyzed by Analyst |
| `analyzed` | Analysis complete, UX Issue created |
| `ignored` | Marked as false positive |

### UX Issue Statuses
| Status | Description |
|--------|-------------|
| `pending_approval` | ⏳ Waiting for human review |
| `approved` | ✅ Human approved, ready for Engineer |
| `rejected` | ❌ Human rejected, won't create PR |
| `needs_revision` | 🔄 Needs more analysis |
| `pr_created` | 🔀 PR created on GitHub |
| `merged` | ✅ PR merged into main |
| `closed` | 🔒 PR closed without merge |

---

## 🚀 When to Implement

**Timeline:**
1. ✅ Phase 7 (Now): Use terminal-based approval for testing
2. ⬜ Phase 6 (NitroStack): Implement MongoDB status-based flow
3. ⬜ Phase 8 (Demo): Use NitroStack widget for approval

**Files to Modify:**
- `src/tasks/all_tasks.py` - Change Analyst output status
- `src/tools/mongodb_tools.py` - Update GetPendingTasksTool query
- `src/crew/darwin_crew.py` - Update engineer mode to check for approved status
- `darwin-acceleration-engine/src/tools/approve-fix.ts` - NitroStack tool

---

## 💡 Benefits of This Approach

1. **Decoupled:** Agents don't need to wait for human input
2. **Scalable:** Multiple reviewers can work in parallel
3. **Auditable:** All approvals tracked in MongoDB
4. **Beautiful:** NitroStack widgets provide great UX
5. **Flexible:** Can add approval rules, auto-approve for low severity, etc.

---

*Last Updated: February 6, 2026*
*Status: PLANNED - Will implement during Phase 6 (NitroStack)*
