"""
Darwin Multi-Agent System - Task Definitions
============================================
CrewAI tasks for the Darwin pipeline.
"""

from crewai import Task, Agent
from typing import Optional


def create_detect_signals_task(watcher_agent: Agent) -> Task:
    """
    Create the signal detection task for the Watcher Agent.
    
    This task queries PostHog for friction signals and saves them to MongoDB.
    """
    return Task(
        description="""
        Detect UX friction signals from PostHog analytics.
        
        Steps:
        1. Query PostHog for rage click events in the last 7 days
        2. Query PostHog for any significant drop-offs or errors
        3. For each friction point found:
           - Classify the signal type (rage_click, drop_off, error_spike, etc.)
           - Determine severity based on affected user count
           - Identify the page/element where friction occurs
        4. Save each signal to MongoDB 'signals' collection with:
           - type: The signal type
           - severity: critical/high/medium/low
           - title: Human-readable description
           - description: Detailed explanation
           - metric_name: The metric that triggered this
           - metric_value: Current value
           - page: Page URL/path
           - element: Specific element if known
           - affected_users: Number of users impacted
           - processed: false (to be picked up by Analyst)
        5. Report how many signals were detected
        
        Focus on the product pages, especially /product/* routes where 
        users interact with Add to Cart functionality.
        """,
        expected_output="""
        A summary report containing:
        - Total number of friction signals detected
        - Breakdown by signal type
        - List of the most critical signals with:
          - Signal ID (from MongoDB)
          - Type and severity
          - Page/element affected
          - Number of users impacted
        - Confirmation that signals were saved to MongoDB
        """,
        agent=watcher_agent,
    )


def create_analyze_issues_task(
    analyst_agent: Agent,
    context_tasks: Optional[list] = None
) -> Task:
    """
    Create the issue analysis task for the Analyst Agent.
    
    This task analyzes signals and creates UX issues with fix recommendations.
    """
    return Task(
        description="""
        Analyze unprocessed signals and diagnose root causes.
        
        Steps:
        1. Get unprocessed signals from MongoDB using get_unprocessed_signals tool
        2. For each high-severity signal:
           a. Read the relevant source code from GitHub
              - For product page issues, check 'app/product/[id].tsx'
              - Use github_list_files to explore if needed
           b. Analyze the code to find the root cause:
              - Small touch targets (padding < 16)
              - Missing press feedback (no activeOpacity)
              - Slow operations without loading states
              - Confusing UI patterns
           c. Formulate a SIMPLE, SINGLE-CHANGE fix recommendation
        
        3. Create a UX Issue in MongoDB 'ux_issues' collection with:
           - signal_id: Link to original signal
           - status: "diagnosed"
           - priority: Based on severity and impact
           - title: Clear issue title
           - description: Full issue description
           - page: Affected page
           - root_cause: Technical root cause
           - user_impact: How users are affected
           - business_impact: Business consequences
           - confidence: Your confidence in the diagnosis (0-1)
           - file_path: The exact file to modify (e.g., "app/product/[id].tsx")
           - recommended_fix: Object with these EXACT fields:
             * title: Short fix title
             * description: What the fix does
             * file_path: Same as above
             * line_start: Starting line number
             * line_end: Ending line number
             * original_code: EXACT code to find (copy from file, keep formatting!)
             * suggested_code: The replacement code (SAME scope as original!)
        
        4. Update the original signal's status to "analyzed" and processed=true
        
        CRITICAL RULES FOR recommended_fix:
        =====================================
        1. original_code MUST be copied EXACTLY from the file (same indentation!)
        2. suggested_code MUST replace ONLY what's in original_code
        3. Do NOT include imports in suggested_code if original_code doesn't have them
        4. Keep fixes SMALL and FOCUSED - one change at a time!
        5. If multiple changes needed, create MULTIPLE issues, one per change
        
        GOOD EXAMPLE (simple activeOpacity fix):
        - original_code: "<TouchableOpacity style={styles.btn} onPress={handleClick}>"
        - suggested_code: "<TouchableOpacity style={styles.btn} onPress={handleClick} activeOpacity={0.7}>"
        
        BAD EXAMPLE (too complex):
        - original_code: "<TouchableOpacity...>"
        - suggested_code: "import Haptics...\n<TouchableOpacity...with haptics...>"
        (This fails because imports aren't in original_code!)
        """,
        expected_output="""
        A detailed analysis report containing:
        - Number of signals analyzed
        - For each UX issue created:
          - Issue ID (from MongoDB)
          - Root cause diagnosis
          - Specific fix recommendation with code
          - Confidence level
        - Summary of files that need modification
        - Confirmation that issues were saved and signals updated
        """,
        agent=analyst_agent,
        context=context_tasks or [],
    )


def create_fix_and_pr_task(
    engineer_agent: Agent,
    context_tasks: Optional[list] = None
) -> Task:
    """
    Create the fix implementation task for the Engineer Agent.
    
    This task implements fixes and creates GitHub Pull Requests using PATCH approach.
    """
    return Task(
        description="""
        Implement ONE code fix and create a GitHub Pull Request.
        
        IMPORTANT: Only process ONE issue. Use the PATCH-BASED approach!
        
        Steps:
        1. Query MongoDB for ONE approved issue:
           - Use: mongodb_read with collection='ux_issues', query='{"status": "approved"}', limit=1
           - Pick the FIRST issue only
        
        2. Determine the file_path (IMPORTANT - check in this order):
           a. If recommended_fix is a LIST: use recommended_fix[0].file_path
           b. If recommended_fix is a DICT: use recommended_fix.file_path
           c. FALLBACK: use issue.file_path (top-level)
           - If ALL are "N/A", "unknown", or missing → skip this issue
        
        3. Extract the fix details:
           - Get recommended_fix (if list, use FIRST item)
           - Get original_code from recommended_fix.original_code OR recommended_fix.code_changes[0].original_code
           - Get suggested_code from recommended_fix.suggested_code OR recommended_fix.code_changes[0].suggested_code
        
        4. Create the PR using github_create_pr with PATCH approach:
           - title: "🧬 Darwin Fix: [Issue Title]"
           - body: Markdown description with:
             * Issue summary
             * Root cause
             * Fix description
           - file_path: Use the file_path determined in step 2
           - original_code: Copy EXACTLY from the fix
           - suggested_code: Copy EXACTLY from the fix
           
           NOTE: You do NOT need to provide the full file content!
           The tool will read the file, find original_code, and replace it.
        
        4. After PR is created:
           - Save PR details to MongoDB 'pull_requests' collection with:
             * issue_id, pr_number, pr_url, branch_name, status="open"
           - Update the UX issue status to "pr_created" using mongodb_update
        
        5. Return the PR URL
        
        CRITICAL: 
        - Do NOT read the file yourself - the PR tool handles it!
        - Just pass original_code and suggested_code from the issue's recommended_fix
        - Process exactly ONE issue
        """,
        expected_output="""
        A PR creation report containing:
        - PR URL (clickable link)
        - PR number
        - Branch name
        - File modified
        - Summary of the patch applied (original → suggested)
        - Confirmation that MongoDB was updated
        - Next steps for human review
        """,
        agent=engineer_agent,
        context=context_tasks or [],
    )


# Task metadata for logging
TASK_METADATA = {
    "detect_signals": {
        "name": "Detect Signals",
        "agent": "Watcher",
        "description": "Query PostHog and save friction signals to MongoDB",
    },
    "analyze_issues": {
        "name": "Analyze Issues",
        "agent": "Analyst", 
        "description": "Diagnose root causes and recommend fixes",
    },
    "fix_and_pr": {
        "name": "Fix & Create PR",
        "agent": "Engineer",
        "description": "Implement fixes and create GitHub PRs",
    },
}
