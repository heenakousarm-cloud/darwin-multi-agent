"""
Darwin Multi-Agent System - PostHog Tools
=========================================
Custom CrewAI tools for querying PostHog analytics.
"""

from typing import Type, Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests
import json

from src.config.settings import get_settings


class PostHogQueryInput(BaseModel):
    """Input schema for PostHog query tool."""
    query_type: str = Field(
        description="Type of query: 'rage_clicks', 'drop_offs', 'events', 'funnel_analysis', 'event_counts'"
    )
    days: int = Field(
        default=30,
        description="Number of days to look back"
    )
    limit: int = Field(
        default=100,
        description="Maximum number of results"
    )
    page_filter: Optional[str] = Field(
        default=None,
        description="Filter by specific page/URL pattern"
    )


class PostHogQueryTool(BaseTool):
    """
    Query PostHog for analytics data including rage clicks, drop-offs, and events.
    
    Used by: Watcher Agent
    """
    
    name: str = "posthog_query"
    description: str = """
    Query PostHog analytics to find UX friction signals.
    Supports queries for:
    - rage_clicks: Find pages/elements with rage click events
    - drop_offs: Find funnel drop-off points  
    - events: Query specific events
    - funnel_analysis: Analyze product view → add to cart → checkout conversion
    - event_counts: Get counts of all event types
    
    Returns structured data about user friction points.
    """
    args_schema: Type[BaseModel] = PostHogQueryInput
    
    def _run(
        self,
        query_type: str,
        days: int = 30,
        limit: int = 100,
        page_filter: Optional[str] = None,
        **kwargs  # Accept and ignore extra parameters from LLM
    ) -> str:
        """Execute the PostHog query."""
        # Log if extra kwargs were passed (for debugging)
        if kwargs:
            print(f"[PostHogQueryTool] Ignoring extra parameters: {list(kwargs.keys())}")
        
        settings = get_settings()
        
        headers = {
            "Authorization": f"Bearer {settings.POSTHOG_API_KEY}",
            "Content-Type": "application/json"
        }
        
        base_url = f"{settings.POSTHOG_HOST}/api/projects/{settings.POSTHOG_PROJECT_ID}"
        
        try:
            if query_type == "rage_clicks":
                return self._query_rage_clicks(base_url, headers, days, limit, page_filter)
            elif query_type == "drop_offs" or query_type == "funnel_analysis":
                return self._query_funnel_analysis(base_url, headers, days)
            elif query_type == "events":
                return self._query_events(base_url, headers, days, limit, page_filter)
            elif query_type == "event_counts":
                return self._query_event_counts(base_url, headers, days)
            elif query_type == "persons":
                return self._query_persons(base_url, headers, limit)
            else:
                return f"Unknown query type: {query_type}. Use: rage_clicks, drop_offs, funnel_analysis, events, event_counts"
        except Exception as e:
            return f"Error querying PostHog: {str(e)}"
    
    def _query_event_counts(
        self,
        base_url: str,
        headers: dict,
        days: int
    ) -> str:
        """Query event counts using HogQL."""
        query = {
            "query": {
                "kind": "HogQLQuery",
                "query": f"""
                    SELECT event, count() as count, uniq(distinct_id) as unique_users
                    FROM events 
                    WHERE timestamp > now() - INTERVAL {days} DAY
                    GROUP BY event 
                    ORDER BY count DESC 
                    LIMIT 30
                """
            }
        }
        
        response = requests.post(
            f"{base_url}/query/",
            headers=headers,
            json=query,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return f"No events found in the last {days} days."
            
            output = f"## Event Counts (Last {days} Days)\n\n"
            output += "| Event | Count | Unique Users |\n"
            output += "|-------|-------|-------------|\n"
            
            for row in results:
                event_name = row[0] if row[0] else "unknown"
                count = row[1] if len(row) > 1 else 0
                users = row[2] if len(row) > 2 else 0
                output += f"| {event_name} | {count} | {users} |\n"
            
            return output
        else:
            return f"PostHog API error: {response.status_code} - {response.text[:200]}"
    
    def _query_rage_clicks(
        self,
        base_url: str,
        headers: dict,
        days: int,
        limit: int,
        page_filter: Optional[str]
    ) -> str:
        """Query for rage click events using HogQL."""
        # First check if $rageclick events exist
        query = {
            "query": {
                "kind": "HogQLQuery",
                "query": f"""
                    SELECT 
                        properties.$current_url as page,
                        properties.$el_text as element,
                        count() as rage_clicks,
                        uniq(distinct_id) as affected_users
                    FROM events 
                    WHERE event = '$rageclick'
                    AND timestamp > now() - INTERVAL {days} DAY
                    GROUP BY page, element
                    ORDER BY rage_clicks DESC
                    LIMIT {limit}
                """
            }
        }
        
        response = requests.post(
            f"{base_url}/query/",
            headers=headers,
            json=query,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                output = f"## Rage Click Analysis (Last {days} Days)\n\n"
                output += "| Page | Element | Rage Clicks | Affected Users |\n"
                output += "|------|---------|-------------|----------------|\n"
                
                for row in results:
                    page = row[0] if row[0] else "unknown"
                    element = row[1] if row[1] else "unknown"
                    clicks = row[2] if len(row) > 2 else 0
                    users = row[3] if len(row) > 3 else 0
                    # Truncate long URLs
                    page_short = page[:50] + "..." if len(str(page)) > 50 else page
                    output += f"| {page_short} | {element} | {clicks} | {users} |\n"
                
                return output
            else:
                # No $rageclick events, fallback to autocapture analysis
                return self._analyze_click_patterns(base_url, headers, days, limit)
        else:
            return f"PostHog API error: {response.status_code}"
    
    def _analyze_click_patterns(
        self,
        base_url: str,
        headers: dict,
        days: int,
        limit: int
    ) -> str:
        """Analyze click patterns when no rage click events exist."""
        query = {
            "query": {
                "kind": "HogQLQuery",
                "query": f"""
                    SELECT 
                        properties.$current_url as page,
                        count() as total_clicks,
                        uniq(distinct_id) as unique_users
                    FROM events 
                    WHERE event = '$autocapture'
                    AND timestamp > now() - INTERVAL {days} DAY
                    GROUP BY page
                    ORDER BY total_clicks DESC
                    LIMIT {limit}
                """
            }
        }
        
        response = requests.post(
            f"{base_url}/query/",
            headers=headers,
            json=query,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            output = f"## Click Pattern Analysis (Last {days} Days)\n\n"
            output += "*Note: No explicit $rageclick events found. Analyzing general click patterns.*\n\n"
            
            if results:
                output += "| Page | Total Clicks | Unique Users |\n"
                output += "|------|--------------|-------------|\n"
                
                for row in results:
                    page = row[0] if row[0] else "unknown"
                    clicks = row[1] if len(row) > 1 else 0
                    users = row[2] if len(row) > 2 else 0
                    page_short = page[:50] + "..." if len(str(page)) > 50 else page
                    output += f"| {page_short} | {clicks} | {users} |\n"
            else:
                output += "No click data found.\n"
            
            return output
        
        return "Could not analyze click patterns."
    
    def _query_funnel_analysis(
        self,
        base_url: str,
        headers: dict,
        days: int
    ) -> str:
        """Analyze conversion funnel: product_viewed → product_added_to_cart → checkout."""
        # Get counts for key funnel events
        query = {
            "query": {
                "kind": "HogQLQuery",
                "query": f"""
                    SELECT 
                        event,
                        count() as total,
                        uniq(distinct_id) as unique_users
                    FROM events 
                    WHERE event IN ('product_viewed', 'product_added_to_cart', 'checkout_started', 'checkout_initiated', 'payment_completed', 'order_created')
                    AND timestamp > now() - INTERVAL {days} DAY
                    GROUP BY event
                    ORDER BY total DESC
                """
            }
        }
        
        response = requests.post(
            f"{base_url}/query/",
            headers=headers,
            json=query,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return f"No funnel events found in the last {days} days."
            
            # Build a dict of event counts
            event_data = {}
            for row in results:
                event_name = row[0]
                count = row[1] if len(row) > 1 else 0
                users = row[2] if len(row) > 2 else 0
                event_data[event_name] = {"count": count, "users": users}
            
            output = f"## Conversion Funnel Analysis (Last {days} Days)\n\n"
            
            # Calculate conversion rates
            product_views = event_data.get("product_viewed", {}).get("count", 0)
            add_to_cart = event_data.get("product_added_to_cart", {}).get("count", 0)
            checkout = event_data.get("checkout_started", event_data.get("checkout_initiated", {})).get("count", 0)
            payment = event_data.get("payment_completed", {}).get("count", 0)
            
            output += "### Funnel Steps\n\n"
            output += "| Step | Events | Conversion Rate |\n"
            output += "|------|--------|----------------|\n"
            output += f"| Product Viewed | {product_views} | 100% (baseline) |\n"
            
            if product_views > 0:
                cart_rate = (add_to_cart / product_views) * 100
                output += f"| Added to Cart | {add_to_cart} | {cart_rate:.1f}% |\n"
                
                if add_to_cart > 0:
                    checkout_rate = (checkout / add_to_cart) * 100
                    output += f"| Checkout Started | {checkout} | {checkout_rate:.1f}% |\n"
                
                if checkout > 0:
                    payment_rate = (payment / checkout) * 100
                    output += f"| Payment Completed | {payment} | {payment_rate:.1f}% |\n"
            
            # Identify drop-off points
            output += "\n### 🚨 Drop-off Analysis\n\n"
            
            if product_views > 0 and add_to_cart > 0:
                view_to_cart_drop = product_views - add_to_cart
                view_to_cart_rate = (add_to_cart / product_views) * 100
                
                if view_to_cart_rate < 30:  # Less than 30% conversion is concerning
                    output += f"**CRITICAL DROP-OFF DETECTED:**\n"
                    output += f"- Product View → Add to Cart: Only {view_to_cart_rate:.1f}% conversion\n"
                    output += f"- {view_to_cart_drop} users ({100-view_to_cart_rate:.1f}%) dropped off\n"
                    output += f"- **Recommendation:** Investigate Add to Cart button usability on product pages\n\n"
                elif view_to_cart_rate < 50:
                    output += f"**MODERATE DROP-OFF:**\n"
                    output += f"- Product View → Add to Cart: {view_to_cart_rate:.1f}% conversion\n"
                    output += f"- {view_to_cart_drop} users dropped off\n\n"
            
            if add_to_cart > 0 and checkout > 0:
                cart_to_checkout_rate = (checkout / add_to_cart) * 100
                if cart_to_checkout_rate < 50:
                    output += f"**Cart to Checkout Drop-off:**\n"
                    output += f"- Add to Cart → Checkout: {cart_to_checkout_rate:.1f}% conversion\n\n"
            
            return output
        else:
            return f"PostHog API error: {response.status_code} - {response.text[:200]}"
    
    def _query_drop_offs(
        self,
        base_url: str,
        headers: dict,
        days: int,
        limit: int
    ) -> str:
        """Query for funnel drop-offs - redirects to funnel_analysis."""
        return self._query_funnel_analysis(base_url, headers, days)
    
    def _query_events(
        self,
        base_url: str,
        headers: dict,
        days: int,
        limit: int,
        page_filter: Optional[str]
    ) -> str:
        """Query general events using HogQL."""
        where_clause = f"AND properties.$current_url LIKE '%{page_filter}%'" if page_filter else ""
        
        query = {
            "query": {
                "kind": "HogQLQuery",
                "query": f"""
                    SELECT 
                        event,
                        count() as total,
                        uniq(distinct_id) as unique_users
                    FROM events 
                    WHERE timestamp > now() - INTERVAL {days} DAY
                    {where_clause}
                    GROUP BY event
                    ORDER BY total DESC
                    LIMIT {limit}
                """
            }
        }
        
        response = requests.post(
            f"{base_url}/query/",
            headers=headers,
            json=query,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return f"No events found in the last {days} days."
            
            output = f"## Event Summary (Last {days} Days)\n\n"
            output += "| Event | Count | Unique Users |\n"
            output += "|-------|-------|-------------|\n"
            
            for row in results:
                event_name = row[0] if row[0] else "unknown"
                count = row[1] if len(row) > 1 else 0
                users = row[2] if len(row) > 2 else 0
                output += f"| {event_name} | {count} | {users} |\n"
            
            return output
        
        return f"Event query failed: {response.status_code}"
    
    def _query_persons(
        self,
        base_url: str,
        headers: dict,
        limit: int
    ) -> str:
        """Query person/user data."""
        response = requests.get(
            f"{base_url}/persons/",
            headers=headers,
            params={"limit": limit},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            persons = data.get("results", [])
            return f"Found {len(persons)} users in the system."
        
        return f"Persons query failed: {response.status_code}"


class PostHogRecordingsInput(BaseModel):
    """Input schema for PostHog recordings tool."""
    limit: int = Field(
        default=10,
        description="Maximum number of recordings to fetch"
    )
    page_filter: Optional[str] = Field(
        default=None,
        description="Filter recordings by page URL"
    )


class PostHogRecordingsTool(BaseTool):
    """
    Fetch session recording URLs from PostHog.
    
    Used by: Watcher Agent, Analyst Agent
    """
    
    name: str = "posthog_recordings"
    description: str = """
    Fetch session recording URLs from PostHog.
    These recordings show actual user behavior and can be used as evidence for UX issues.
    Returns a list of recording URLs that can be reviewed.
    """
    args_schema: Type[BaseModel] = PostHogRecordingsInput
    
    def _run(self, limit: int = 10, page_filter: Optional[str] = None) -> str:
        """Fetch session recordings."""
        settings = get_settings()
        
        headers = {
            "Authorization": f"Bearer {settings.POSTHOG_API_KEY}"
        }
        
        base_url = f"{settings.POSTHOG_HOST}/api/projects/{settings.POSTHOG_PROJECT_ID}"
        
        try:
            params = {"limit": limit}
            
            response = requests.get(
                f"{base_url}/session_recordings/",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                recordings = data.get("results", [])
                
                if not recordings:
                    return "No session recordings found."
                
                output = "## Session Recordings\n\n"
                for rec in recordings[:limit]:
                    rec_id = rec.get("id", "unknown")
                    duration = rec.get("recording_duration", 0)
                    start_time = rec.get("start_time", "unknown")
                    
                    rec_url = f"{settings.POSTHOG_HOST}/replay/{rec_id}"
                    output += f"- [{rec_id[:8]}...]({rec_url}) - {duration}s - {start_time}\n"
                
                output += f"\n*Found {len(recordings)} recordings*"
                return output
            else:
                return f"Failed to fetch recordings: {response.status_code}"
                
        except Exception as e:
            return f"Error fetching recordings: {str(e)}"
