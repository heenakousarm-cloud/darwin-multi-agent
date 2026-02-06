#!/usr/bin/env python3
"""
PostHog Data Checker
====================
Check what data exists in PostHog and analyze what Darwin can detect.

Run: python scripts/check_posthog_data.py
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import get_settings

console = Console()


def check_posthog_connection():
    """Verify PostHog connection."""
    settings = get_settings()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🔍 PostHog Data Checker[/bold cyan]\n"
        "Analyzing what data exists for Darwin to detect",
        border_style="cyan"
    ))
    console.print()
    
    # Check settings
    console.print("[bold]📋 Configuration:[/bold]")
    console.print(f"  • Host: {settings.POSTHOG_HOST}")
    console.print(f"  • Project ID: {settings.POSTHOG_PROJECT_ID}")
    console.print(f"  • API Key: {settings.POSTHOG_API_KEY[:15]}...")
    console.print()
    
    return settings


def query_posthog(settings, query: str) -> dict:
    """Execute a HogQL query."""
    headers = {
        "Authorization": f"Bearer {settings.POSTHOG_API_KEY}",
        "Content-Type": "application/json"
    }
    
    base_url = f"{settings.POSTHOG_HOST}/api/projects/{settings.POSTHOG_PROJECT_ID}"
    
    response = requests.post(
        f"{base_url}/query/",
        headers=headers,
        json={"query": {"kind": "HogQLQuery", "query": query}},
        timeout=30
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        console.print(f"[red]API Error: {response.status_code}[/red]")
        console.print(f"[dim]{response.text[:500]}[/dim]")
        return {"results": []}


def check_event_counts(settings):
    """Check all event types and counts."""
    console.print("[bold yellow]📊 Event Summary (Last 30 Days)[/bold yellow]")
    console.print()
    
    query = """
        SELECT 
            event,
            count() as count,
            uniq(distinct_id) as unique_users,
            max(timestamp) as last_seen
        FROM events 
        WHERE timestamp > now() - INTERVAL 30 DAY
        GROUP BY event 
        ORDER BY count DESC 
        LIMIT 50
    """
    
    data = query_posthog(settings, query)
    results = data.get("results", [])
    
    if not results:
        console.print("[red]❌ No events found in the last 30 days![/red]")
        console.print("[dim]Run the Test Data Generator in Luxora app first.[/dim]")
        return []
    
    table = Table(title="All Events", show_header=True, header_style="bold magenta")
    table.add_column("Event Name", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Unique Users", justify="right")
    table.add_column("Last Seen", style="dim")
    
    darwin_relevant = []
    
    for row in results:
        event_name = row[0] or "unknown"
        count = row[1] or 0
        users = row[2] or 0
        last_seen = str(row[3])[:19] if row[3] else "unknown"
        
        # Highlight Darwin-relevant events
        is_relevant = event_name in [
            'product_added_to_cart', 'product_removed_from_cart',
            'cart_quantity_updated', 'cart_cleared',
            'product_added_to_wishlist', 'product_removed_from_wishlist',
            'checkout_initiated', 'purchase_completed',
            'coupon_applied', 'coupon_failed',
            '$screen', '$identify', 'session_started', 'session_ended'
        ]
        
        if is_relevant:
            darwin_relevant.append((event_name, count, users))
            table.add_row(f"[green]✓[/green] {event_name}", str(count), str(users), last_seen)
        else:
            table.add_row(f"  {event_name}", str(count), str(users), last_seen)
    
    console.print(table)
    console.print()
    
    return darwin_relevant


def check_friction_signals(settings):
    """Check for specific friction patterns Darwin looks for."""
    console.print("[bold yellow]🚨 Friction Signal Detection[/bold yellow]")
    console.print()
    
    friction_checks = []
    
    # 1. Check for rage clicks (rapid add-to-cart)
    console.print("[bold]1. Rage Clicks (Rapid Add to Cart):[/bold]")
    query = """
        SELECT 
            distinct_id,
            properties.product_id as product,
            count() as click_count,
            min(timestamp) as first_click,
            max(timestamp) as last_click,
            dateDiff('second', min(timestamp), max(timestamp)) as duration_seconds
        FROM events 
        WHERE event = 'product_added_to_cart'
        AND timestamp > now() - INTERVAL 7 DAY
        GROUP BY distinct_id, product
        HAVING count() >= 3
        ORDER BY click_count DESC
        LIMIT 20
    """
    
    data = query_posthog(settings, query)
    results = data.get("results", [])
    
    if results:
        rage_count = len([r for r in results if r[2] >= 5])  # 5+ clicks
        console.print(f"  [green]✓ Found {len(results)} users with multiple add-to-cart clicks[/green]")
        console.print(f"  [yellow]  → {rage_count} potential rage click incidents (5+ clicks)[/yellow]")
        friction_checks.append(("Rage Clicks", rage_count, "High" if rage_count > 0 else "None"))
    else:
        console.print("  [dim]No rapid click patterns detected[/dim]")
        friction_checks.append(("Rage Clicks", 0, "None"))
    console.print()
    
    # 2. Check for cart abandonment
    console.print("[bold]2. Cart Abandonment:[/bold]")
    query = """
        SELECT 
            count(DISTINCT case when event = 'product_added_to_cart' then distinct_id end) as added_to_cart,
            count(DISTINCT case when event = 'checkout_initiated' then distinct_id end) as started_checkout
        FROM events 
        WHERE timestamp > now() - INTERVAL 7 DAY
    """
    
    data = query_posthog(settings, query)
    results = data.get("results", [])
    
    if results and results[0][0]:
        cart_users = results[0][0]
        checkout_users = results[0][1] or 0
        abandoned = cart_users - checkout_users
        abandon_rate = (abandoned / cart_users * 100) if cart_users > 0 else 0
        
        console.print(f"  [cyan]Users who added to cart: {cart_users}[/cyan]")
        console.print(f"  [cyan]Users who started checkout: {checkout_users}[/cyan]")
        console.print(f"  [{'red' if abandon_rate > 50 else 'yellow'}]Cart abandonment rate: {abandon_rate:.1f}%[/{'red' if abandon_rate > 50 else 'yellow'}]")
        friction_checks.append(("Cart Abandonment", f"{abandon_rate:.1f}%", "High" if abandon_rate > 70 else "Medium" if abandon_rate > 50 else "Low"))
    else:
        console.print("  [dim]No cart data found[/dim]")
        friction_checks.append(("Cart Abandonment", "N/A", "Unknown"))
    console.print()
    
    # 3. Check for coupon failures
    console.print("[bold]3. Coupon Failures:[/bold]")
    query = """
        SELECT 
            count(case when event = 'coupon_failed' then 1 end) as failed,
            count(case when event = 'coupon_applied' then 1 end) as success,
            uniq(case when event = 'coupon_failed' then distinct_id end) as users_failed
        FROM events 
        WHERE event IN ('coupon_failed', 'coupon_applied')
        AND timestamp > now() - INTERVAL 7 DAY
    """
    
    data = query_posthog(settings, query)
    results = data.get("results", [])
    
    if results and (results[0][0] or results[0][1]):
        failed = results[0][0] or 0
        success = results[0][1] or 0
        users_failed = results[0][2] or 0
        total = failed + success
        fail_rate = (failed / total * 100) if total > 0 else 0
        
        console.print(f"  [cyan]Coupon attempts: {total} (Success: {success}, Failed: {failed})[/cyan]")
        console.print(f"  [{'red' if fail_rate > 50 else 'yellow'}]Failure rate: {fail_rate:.1f}% ({users_failed} users)[/{'red' if fail_rate > 50 else 'yellow'}]")
        friction_checks.append(("Coupon Failures", f"{fail_rate:.1f}%", "High" if fail_rate > 60 else "Medium" if fail_rate > 30 else "Low"))
    else:
        console.print("  [dim]No coupon data found[/dim]")
        friction_checks.append(("Coupon Failures", "N/A", "Unknown"))
    console.print()
    
    # 4. Check for wishlist churn
    console.print("[bold]4. Wishlist Churn:[/bold]")
    query = """
        SELECT 
            distinct_id,
            count(case when event = 'product_added_to_wishlist' then 1 end) as adds,
            count(case when event = 'product_removed_from_wishlist' then 1 end) as removes
        FROM events 
        WHERE event IN ('product_added_to_wishlist', 'product_removed_from_wishlist')
        AND timestamp > now() - INTERVAL 7 DAY
        GROUP BY distinct_id
        HAVING adds >= 2 AND removes >= 2
    """
    
    data = query_posthog(settings, query)
    results = data.get("results", [])
    
    if results:
        console.print(f"  [green]✓ Found {len(results)} users with wishlist add/remove cycles[/green]")
        friction_checks.append(("Wishlist Churn", len(results), "Medium" if len(results) > 0 else "None"))
    else:
        console.print("  [dim]No wishlist churn detected[/dim]")
        friction_checks.append(("Wishlist Churn", 0, "None"))
    console.print()
    
    # 5. Check for quantity update spam
    console.print("[bold]5. Quantity Update Spam:[/bold]")
    query = """
        SELECT 
            distinct_id,
            count() as updates
        FROM events 
        WHERE event = 'cart_quantity_updated'
        AND timestamp > now() - INTERVAL 7 DAY
        GROUP BY distinct_id
        HAVING updates >= 5
    """
    
    data = query_posthog(settings, query)
    results = data.get("results", [])
    
    if results:
        console.print(f"  [green]✓ Found {len(results)} users with 5+ quantity updates[/green]")
        friction_checks.append(("Quantity Spam", len(results), "Medium" if len(results) > 0 else "None"))
    else:
        console.print("  [dim]No quantity spam detected[/dim]")
        friction_checks.append(("Quantity Spam", 0, "None"))
    console.print()
    
    return friction_checks


def check_users(settings):
    """Check user/person data."""
    console.print("[bold yellow]👥 User Data[/bold yellow]")
    console.print()
    
    query = """
        SELECT 
            distinct_id,
            count() as event_count,
            min(timestamp) as first_seen,
            max(timestamp) as last_seen
        FROM events 
        WHERE timestamp > now() - INTERVAL 30 DAY
        GROUP BY distinct_id
        ORDER BY event_count DESC
        LIMIT 15
    """
    
    data = query_posthog(settings, query)
    results = data.get("results", [])
    
    if results:
        table = Table(title="Active Users", show_header=True, header_style="bold magenta")
        table.add_column("User ID", style="cyan", max_width=30)
        table.add_column("Events", justify="right")
        table.add_column("First Seen", style="dim")
        table.add_column("Last Seen", style="dim")
        
        for row in results:
            user_id = str(row[0])[:30] if row[0] else "anonymous"
            events = row[1] or 0
            first = str(row[2])[:10] if row[2] else "unknown"
            last = str(row[3])[:10] if row[3] else "unknown"
            table.add_row(user_id, str(events), first, last)
        
        console.print(table)
        console.print(f"\n[dim]Showing top 15 of {len(results)} users[/dim]")
    else:
        console.print("[red]No users found[/red]")
    
    console.print()
    return len(results)


def generate_recommendations(friction_checks, event_count):
    """Generate recommendations for PostHog setup."""
    console.print("[bold yellow]💡 Recommendations for Darwin[/bold yellow]")
    console.print()
    
    # Check if we have enough data
    if event_count == 0:
        console.print(Panel(
            "[red bold]⚠️ NO DATA FOUND![/red bold]\n\n"
            "You need to generate test data first:\n"
            "1. Run Luxora app: cd ~/Desktop/Projects/ReactNative/ecommerce-app && npx expo start\n"
            "2. Open app in simulator/device\n"
            "3. Tap the 🧪 button (bottom-right)\n"
            "4. Tap 'Generate All Test Data'\n"
            "5. Wait for completion, then run this script again",
            title="Action Required",
            border_style="red"
        ))
        return
    
    console.print("[bold green]✅ Data Found! Here's what Darwin can detect:[/bold green]")
    console.print()
    
    # Summary table
    table = Table(title="Friction Signal Summary", show_header=True, header_style="bold magenta")
    table.add_column("Signal Type", style="cyan")
    table.add_column("Value")
    table.add_column("Severity", justify="center")
    
    for signal, value, severity in friction_checks:
        severity_color = {"High": "red", "Medium": "yellow", "Low": "green", "None": "dim", "Unknown": "dim"}.get(severity, "white")
        table.add_row(signal, str(value), f"[{severity_color}]{severity}[/{severity_color}]")
    
    console.print(table)
    console.print()
    
    # PostHog setup recommendations
    console.print("[bold]📊 Optional PostHog Enhancements:[/bold]")
    console.print()
    
    console.print("These are OPTIONAL - Darwin works with raw events, but these help visualization:\n")
    
    console.print("[cyan]1. Conversion Funnel (Insight)[/cyan]")
    console.print("   Create in PostHog → Insights → New Insight → Funnel")
    console.print("   Steps: product_added_to_cart → checkout_initiated → purchase_completed")
    console.print()
    
    console.print("[cyan]2. Rage Click Dashboard[/cyan]")
    console.print("   Create in PostHog → Dashboards → New Dashboard")
    console.print("   Add trends for: product_added_to_cart grouped by user")
    console.print()
    
    console.print("[cyan]3. Coupon Analysis[/cyan]")
    console.print("   Create insight comparing coupon_applied vs coupon_failed")
    console.print()
    
    console.print(Panel(
        "[bold green]✓ Darwin is ready to analyze this data![/bold green]\n\n"
        "Run Darwin:\n"
        "  cd ~/Desktop/Hackathon/darwin-multi-agent\n"
        "  source venv/bin/activate\n"
        "  python scripts/run_darwin.py --mode analyze",
        title="Next Steps",
        border_style="green"
    ))


def main():
    """Main function."""
    try:
        settings = check_posthog_connection()
        
        # Check events
        darwin_events = check_event_counts(settings)
        
        # Check friction signals
        friction_checks = check_friction_signals(settings)
        
        # Check users
        user_count = check_users(settings)
        
        # Generate recommendations
        generate_recommendations(friction_checks, len(darwin_events))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
