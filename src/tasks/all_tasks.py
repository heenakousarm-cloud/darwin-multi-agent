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
              - Missing press feedback
              - Slow operations without loading states
              - Confusing UI patterns
           c. Formulate a specific fix recommendation with:
              - Exact file path
              - Line numbers to modify
              - Current code snippet
              - Recommended code change
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
           - recommended_fix: Object with title, description, file_path, 
             line_start, line_end, original_code, suggested_code
           - file_path: Primary file to modify
        4. Update the original signal's status to "analyzed" and processed=true
        
        Be specific in your recommendations - the Engineer needs exact code changes.
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
    
    This task implements fixes and creates GitHub Pull Requests.
    """
    return Task(
        description="""
        Implement code fixes and create GitHub Pull Requests.
        
        Steps:
        1. Get pending tasks from MongoDB OR read diagnosed UX issues
           - Look for issues with status "diagnosed" or "fix_proposed"
           - Or use get_pending_tasks if tasks exist
        2. For the highest priority issue:
           a. Read the current file content from GitHub
           b. Apply the recommended fix:
              - Make the exact changes specified
              - Preserve existing code style
              - Don't change anything else
           c. Create a GitHub Pull Request using github_create_pr:
              - title: "🧬 Darwin Fix: [Issue Title]"
              - body: Markdown description with:
                * Issue summary
                * Root cause
                * Changes made
                * User impact
                * Affected users count
              - file_path: Path to the file
              - new_content: Complete file with fix applied
        3. Save PR details to MongoDB 'pull_requests' collection:
           - pr_number
           - pr_url
           - branch_name
           - task_id or ux_issue_id
           - status: "open"
        4. Update the UX issue status to "pr_created"
        5. Report the PR URL
        
        Important: Read the ENTIRE current file first, then apply changes.
        The new_content must be the complete file, not just the changed lines.
        """,
        expected_output="""
        A PR creation report containing:
        - PR URL (clickable link)
        - PR number
        - Branch name
        - Files changed
        - Summary of code changes made
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
