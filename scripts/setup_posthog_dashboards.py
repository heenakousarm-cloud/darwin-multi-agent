#!/usr/bin/env python3
"""
PostHog Dashboard & Insights Setup
==================================
Creates funnels, insights, and dashboards in PostHog for Darwin demo.

Run: python scripts/setup_posthog_dashboards.py
"""

import os
import sys
import requests
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import get_settings

console = Console()


class PostHogSetup:
    """Setup PostHog dashboards and insights."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = f"{self.settings.POSTHOG_HOST}/api/projects/{self.settings.POSTHOG_PROJECT_ID}"
        self.headers = {
            "Authorization": f"Bearer {self.settings.POSTHOG_API_KEY}",
            "Content-Type": "application/json"
        }
        self.created_insights = []
        self.dashboard_id = None
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make API request to PostHog."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data, timeout=30)
            else:
                return {"error": f"Unknown method: {method}"}
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {"error": f"API Error {response.status_code}: {response.text[:200]}"}
        except Exception as e:
            return {"error": str(e)}
    
    def create_conversion_funnel(self) -> dict:
        """Create e-commerce conversion funnel insight."""
        console.print("\n[bold cyan]1. Creating Conversion Funnel...[/bold cyan]")
        
        insight_data = {
            "name": "🛒 E-commerce Conversion Funnel",
            "description": "Track user journey from Add to Cart → Checkout → Purchase. Created by Darwin AI.",
            "filters": {
                "insight": "FUNNELS",
                "funnel_viz_type": "steps",
                "display": "FunnelViz",
                "interval": "day",
                "date_from": "-30d",
                "events": [
                    {
                        "id": "product_added_to_cart",
                        "name": "Product Added to Cart",
                        "type": "events",
                        "order": 0
                    },
                    {
                        "id": "checkout_initiated",
                        "name": "Checkout Initiated",
                        "type": "events",
                        "order": 1
                    },
                    {
                        "id": "payment_completed",
                        "name": "Payment Completed",
                        "type": "events",
                        "order": 2
                    }
                ],
                "funnel_window_days": 14,
                "exclusions": [],
                "breakdown_type": "event"
            },
            "query": None,
            "saved": True
        }
        
        result = self._make_request("POST", "insights/", insight_data)
        
        if "error" not in result:
            insight_id = result.get("id")
            short_id = result.get("short_id")
            console.print(f"   [green]✓ Created funnel insight (ID: {insight_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/insights/{short_id}[/dim]")
            self.created_insights.append(insight_id)
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def create_rage_click_insight(self) -> dict:
        """Create rage click detection insight."""
        console.print("\n[bold cyan]2. Creating Rage Click Detection Insight...[/bold cyan]")
        
        insight_data = {
            "name": "😤 Rage Click Detection",
            "description": "Users who clicked Add to Cart multiple times rapidly - indicates UX friction. Created by Darwin AI.",
            "filters": {
                "insight": "TRENDS",
                "display": "ActionsTable",
                "interval": "day",
                "date_from": "-7d",
                "events": [
                    {
                        "id": "product_added_to_cart",
                        "name": "Product Added to Cart",
                        "type": "events",
                        "order": 0,
                        "math": "total"
                    }
                ],
                "breakdown": "distinct_id",
                "breakdown_type": "event"
            },
            "query": None,
            "saved": True
        }
        
        result = self._make_request("POST", "insights/", insight_data)
        
        if "error" not in result:
            insight_id = result.get("id")
            short_id = result.get("short_id")
            console.print(f"   [green]✓ Created rage click insight (ID: {insight_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/insights/{short_id}[/dim]")
            self.created_insights.append(insight_id)
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def create_coupon_performance_insight(self) -> dict:
        """Create coupon success vs failure insight."""
        console.print("\n[bold cyan]3. Creating Coupon Performance Insight...[/bold cyan]")
        
        insight_data = {
            "name": "🎟️ Coupon Success vs Failure",
            "description": "Compare successful coupon applications vs failed attempts. High failure rate indicates UX issues. Created by Darwin AI.",
            "filters": {
                "insight": "TRENDS",
                "display": "ActionsLineGraph",
                "interval": "day",
                "date_from": "-30d",
                "events": [
                    {
                        "id": "coupon_applied",
                        "name": "Coupon Applied (Success)",
                        "type": "events",
                        "order": 0,
                        "math": "total"
                    },
                    {
                        "id": "coupon_failed",
                        "name": "Coupon Failed",
                        "type": "events",
                        "order": 1,
                        "math": "total"
                    }
                ]
            },
            "query": None,
            "saved": True
        }
        
        result = self._make_request("POST", "insights/", insight_data)
        
        if "error" not in result:
            insight_id = result.get("id")
            short_id = result.get("short_id")
            console.print(f"   [green]✓ Created coupon insight (ID: {insight_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/insights/{short_id}[/dim]")
            self.created_insights.append(insight_id)
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def create_cart_abandonment_insight(self) -> dict:
        """Create cart abandonment tracking insight."""
        console.print("\n[bold cyan]4. Creating Cart Abandonment Insight...[/bold cyan]")
        
        insight_data = {
            "name": "🛒 Cart Abandonment Tracking",
            "description": "Track users who add to cart but don't complete checkout. Created by Darwin AI.",
            "filters": {
                "insight": "FUNNELS",
                "funnel_viz_type": "steps",
                "display": "FunnelViz",
                "interval": "day",
                "date_from": "-14d",
                "events": [
                    {
                        "id": "product_added_to_cart",
                        "name": "Added to Cart",
                        "type": "events",
                        "order": 0
                    },
                    {
                        "id": "checkout_initiated",
                        "name": "Started Checkout",
                        "type": "events",
                        "order": 1
                    }
                ],
                "funnel_window_days": 7,
                "exclusions": [],
                "breakdown_type": "event"
            },
            "query": None,
            "saved": True
        }
        
        result = self._make_request("POST", "insights/", insight_data)
        
        if "error" not in result:
            insight_id = result.get("id")
            short_id = result.get("short_id")
            console.print(f"   [green]✓ Created cart abandonment insight (ID: {insight_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/insights/{short_id}[/dim]")
            self.created_insights.append(insight_id)
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def create_wishlist_churn_insight(self) -> dict:
        """Create wishlist add/remove churn insight."""
        console.print("\n[bold cyan]5. Creating Wishlist Churn Insight...[/bold cyan]")
        
        insight_data = {
            "name": "💕 Wishlist Add/Remove Activity",
            "description": "Track wishlist additions and removals. High churn indicates user indecision. Created by Darwin AI.",
            "filters": {
                "insight": "TRENDS",
                "display": "ActionsLineGraph",
                "interval": "day",
                "date_from": "-14d",
                "events": [
                    {
                        "id": "product_added_to_wishlist",
                        "name": "Added to Wishlist",
                        "type": "events",
                        "order": 0,
                        "math": "total"
                    },
                    {
                        "id": "product_removed_from_wishlist",
                        "name": "Removed from Wishlist",
                        "type": "events",
                        "order": 1,
                        "math": "total"
                    }
                ]
            },
            "query": None,
            "saved": True
        }
        
        result = self._make_request("POST", "insights/", insight_data)
        
        if "error" not in result:
            insight_id = result.get("id")
            short_id = result.get("short_id")
            console.print(f"   [green]✓ Created wishlist insight (ID: {insight_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/insights/{short_id}[/dim]")
            self.created_insights.append(insight_id)
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def create_quantity_spam_insight(self) -> dict:
        """Create quantity update spam insight."""
        console.print("\n[bold cyan]6. Creating Quantity Update Spam Insight...[/bold cyan]")
        
        insight_data = {
            "name": "🔢 Cart Quantity Updates by User",
            "description": "Track quantity update frequency per user. High counts indicate confusing quantity controls. Created by Darwin AI.",
            "filters": {
                "insight": "TRENDS",
                "display": "ActionsTable",
                "interval": "day",
                "date_from": "-7d",
                "events": [
                    {
                        "id": "cart_quantity_updated",
                        "name": "Cart Quantity Updated",
                        "type": "events",
                        "order": 0,
                        "math": "total"
                    }
                ],
                "breakdown": "distinct_id",
                "breakdown_type": "event"
            },
            "query": None,
            "saved": True
        }
        
        result = self._make_request("POST", "insights/", insight_data)
        
        if "error" not in result:
            insight_id = result.get("id")
            short_id = result.get("short_id")
            console.print(f"   [green]✓ Created quantity spam insight (ID: {insight_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/insights/{short_id}[/dim]")
            self.created_insights.append(insight_id)
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def create_event_overview_insight(self) -> dict:
        """Create overall event overview insight."""
        console.print("\n[bold cyan]7. Creating Event Overview Insight...[/bold cyan]")
        
        insight_data = {
            "name": "📊 All Events Overview",
            "description": "Overview of all tracked events in the app. Created by Darwin AI.",
            "filters": {
                "insight": "TRENDS",
                "display": "ActionsLineGraph",
                "interval": "day",
                "date_from": "-30d",
                "events": [
                    {
                        "id": "product_added_to_cart",
                        "name": "Add to Cart",
                        "type": "events",
                        "order": 0,
                        "math": "total"
                    },
                    {
                        "id": "checkout_initiated",
                        "name": "Checkout",
                        "type": "events",
                        "order": 1,
                        "math": "total"
                    },
                    {
                        "id": "payment_completed",
                        "name": "Payment",
                        "type": "events",
                        "order": 2,
                        "math": "total"
                    },
                    {
                        "id": "cart_cleared",
                        "name": "Cart Cleared",
                        "type": "events",
                        "order": 3,
                        "math": "total"
                    }
                ]
            },
            "query": None,
            "saved": True
        }
        
        result = self._make_request("POST", "insights/", insight_data)
        
        if "error" not in result:
            insight_id = result.get("id")
            short_id = result.get("short_id")
            console.print(f"   [green]✓ Created event overview insight (ID: {insight_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/insights/{short_id}[/dim]")
            self.created_insights.append(insight_id)
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def create_dashboard(self) -> dict:
        """Create main Darwin dashboard."""
        console.print("\n[bold cyan]8. Creating Darwin UX Friction Dashboard...[/bold cyan]")
        
        dashboard_data = {
            "name": "🧬 Darwin UX Friction Dashboard",
            "description": "Dashboard for monitoring UX friction signals detected by Darwin AI. Includes conversion funnels, rage click detection, coupon failures, and cart abandonment tracking.",
            "pinned": True,
            "tags": ["darwin", "ux", "friction", "analytics"]
        }
        
        result = self._make_request("POST", "dashboards/", dashboard_data)
        
        if "error" not in result:
            self.dashboard_id = result.get("id")
            console.print(f"   [green]✓ Created dashboard (ID: {self.dashboard_id})[/green]")
            console.print(f"   [dim]View at: {self.settings.POSTHOG_HOST}/dashboard/{self.dashboard_id}[/dim]")
            return result
        else:
            console.print(f"   [red]✗ Failed: {result['error']}[/red]")
            return result
    
    def add_insights_to_dashboard(self):
        """Add all created insights to the dashboard."""
        if not self.dashboard_id or not self.created_insights:
            console.print("\n[yellow]⚠️ No dashboard or insights to link[/yellow]")
            return
        
        console.print("\n[bold cyan]9. Adding Insights to Dashboard...[/bold cyan]")
        
        for insight_id in self.created_insights:
            # Update insight to add to dashboard
            update_data = {
                "dashboards": [self.dashboard_id]
            }
            
            result = self._make_request("PATCH", f"insights/{insight_id}/", update_data)
            
            if "error" not in result:
                console.print(f"   [green]✓ Added insight {insight_id} to dashboard[/green]")
            else:
                console.print(f"   [yellow]⚠️ Could not add insight {insight_id}: {result.get('error', 'Unknown error')}[/yellow]")
    
    def run_setup(self):
        """Run the complete setup."""
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🧬 Darwin PostHog Setup[/bold cyan]\n"
            "Creating insights and dashboard for UX friction monitoring",
            border_style="cyan"
        ))
        
        console.print(f"\n[bold]📋 Configuration:[/bold]")
        console.print(f"   Host: {self.settings.POSTHOG_HOST}")
        console.print(f"   Project ID: {self.settings.POSTHOG_PROJECT_ID}")
        
        # Create all insights
        self.create_conversion_funnel()
        self.create_rage_click_insight()
        self.create_coupon_performance_insight()
        self.create_cart_abandonment_insight()
        self.create_wishlist_churn_insight()
        self.create_quantity_spam_insight()
        self.create_event_overview_insight()
        
        # Create dashboard
        self.create_dashboard()
        
        # Add insights to dashboard
        self.add_insights_to_dashboard()
        
        # Summary
        console.print()
        console.print(Panel(
            f"[bold green]✅ Setup Complete![/bold green]\n\n"
            f"Created {len(self.created_insights)} insights and 1 dashboard\n\n"
            f"[bold]Dashboard URL:[/bold]\n"
            f"[cyan]{self.settings.POSTHOG_HOST}/dashboard/{self.dashboard_id}[/cyan]\n\n"
            f"[bold]What's Included:[/bold]\n"
            f"• 🛒 E-commerce Conversion Funnel\n"
            f"• 😤 Rage Click Detection\n"
            f"• 🎟️ Coupon Success vs Failure\n"
            f"• 🛒 Cart Abandonment Tracking\n"
            f"• 💕 Wishlist Churn Analysis\n"
            f"• 🔢 Quantity Update Spam\n"
            f"• 📊 Event Overview",
            title="Summary",
            border_style="green"
        ))
        
        return {
            "dashboard_id": self.dashboard_id,
            "dashboard_url": f"{self.settings.POSTHOG_HOST}/dashboard/{self.dashboard_id}",
            "insights_created": len(self.created_insights),
            "insight_ids": self.created_insights
        }


def main():
    """Main function."""
    try:
        setup = PostHogSetup()
        result = setup.run_setup()
        
        console.print("\n[bold]🔗 Quick Links:[/bold]")
        console.print(f"   Dashboard: {result['dashboard_url']}")
        console.print(f"   Insights: {setup.settings.POSTHOG_HOST}/insights")
        console.print()
        
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
