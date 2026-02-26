#!/usr/bin/env python3
"""
Social Engagement Tool CLI
"""

import asyncio
import argparse
import yaml
from pathlib import Path

from core.engine import create_engine, SocialEngagementEngine
from core.discovery import DiscoveryConfig
from core.engagement import EngagementConfig, TargetAudience
from adapters.base import Platform


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


async def cmd_discover(args, engine: SocialEngagementEngine):
    """Discover posts"""
    print(f"🔍 Discovering {args.platform} posts...")
    
    config = DiscoveryConfig(
        platforms=[Platform.INSTAGRAM],
        hashtags=args.hashtags.split(',') if args.hashtags else [],
        keywords=args.keywords.split(',') if args.keywords else [],
        location=args.location,
        limit=args.limit
    )
    
    discovered = await engine.discovery.discover(config)
    
    print(f"\n📊 Found {len(discovered)} posts:\n")
    for d in discovered[:10]:
        print(f"  {d.post.url}")
        print(f"    Score: {d.engagement_score:.1f} | {d.reason}")
        print()


async def cmd_engage(args, engine: SocialEngagementEngine):
    """Run engagement campaign"""
    
    # Load audience from config
    audience = TargetAudience(
        interests=args.interests.split(',') if args.interests else ["rock climbing"],
        demographics={"location": args.location or "Unknown"},
        pain_points=[],
        desires=[]
    )
    
    discovery_config = DiscoveryConfig(
        platforms=[Platform.INSTAGRAM],
        hashtags=args.hashtags.split(',') if args.hashtags else [],
        keywords=args.keywords.split(',') if args.keywords else [],
        location=args.location,
        limit=args.limit
    )
    
    engagement_config = EngagementConfig(
        audience=audience,
        tone=args.tone,
        max_daily=args.daily_limit,
        min_delay_seconds=args.min_delay,
        max_delay_seconds=args.max_delay
    )
    
    print(f"🚀 Starting engagement campaign...")
    print(f"   Hashtags: {args.hashtags}")
    print(f"   Location: {args.location}")
    print(f"   Daily limit: {args.daily_limit}")
    
    results = await engine.discover_and_engage(audience, discovery_config, engagement_config)
    
    print(f"\n📊 Results:")
    print(f"   Discovered: {len(results['discovered'])}")
    print(f"   Engaged: {len(results['engaged'])}")
    print(f"   Failed: {len(results['failed'])}")


async def cmd_stats(args, engine: SocialEngagementEngine):
    """Show statistics"""
    stats = engine.get_stats()
    
    print("📊 Statistics")
    print("-" * 30)
    print(f"Today: {stats['today']} engagements")
    print(f"This week: {stats['this_week']} engagements")
    print()
    print("By action:")
    for action, data in stats['by_action'].items():
        rate = (data['success'] / data['total'] * 100) if data['total'] > 0 else 0
        print(f"  {action}: {data['success']}/{data['total']} ({rate:.1f}%)")


async def cmd_login(args, engine: SocialEngagementEngine):
    """Login to platform"""
    import getpass
    
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    platform = Platform.INSTAGRAM if args.platform == "instagram" else Platform.TWITTER
    
    success = await engine.login(platform, {"username": username, "password": password})
    
    if success:
        print("✅ Logged in successfully!")
    else:
        print("❌ Login failed")


def main():
    parser = argparse.ArgumentParser(description="Social Engagement Tool")
    parser.add_argument("--config", default="config/platforms.yaml", help="Config file path")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Discover posts")
    discover_parser.add_argument("--platform", default="instagram")
    discover_parser.add_argument("--hashtags", help="Comma-separated hashtags")
    discover_parser.add_argument("--keywords", help="Comma-separated keywords")
    discover_parser.add_argument("--location", help="Location filter")
    discover_parser.add_argument("--limit", type=int, default=20)
    
    # Engage command
    engage_parser = subparsers.add_parser("engage", help="Run engagement campaign")
    engage_parser.add_argument("--platform", default="instagram")
    engage_parser.add_argument("--hashtags", required=True, help="Comma-separated hashtags")
    engage_parser.add_argument("--keywords", help="Comma-separated keywords")
    engage_parser.add_argument("--location", help="Location filter")
    engage_parser.add_argument("--interests", default="rock climbing", help="Target interests")
    engage_parser.add_argument("--tone", default="friendly", help="Comment tone")
    engage_parser.add_argument("--limit", type=int, default=50, help="Max posts to process")
    engage_parser.add_argument("--daily-limit", type=int, default=20, help="Max comments per day")
    engage_parser.add_argument("--min-delay", type=int, default=30, help="Min delay between actions (seconds)")
    engage_parser.add_argument("--max-delay", type=int, default=120, help="Max delay between actions (seconds)")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to platform")
    login_parser.add_argument("--platform", default="instagram")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # Load config
    config_path = Path(args.config)
    if config_path.exists():
        config = load_config(args.config)
    else:
        config = {"platforms": {}}
        print(f"⚠️  Config not found at {args.config}, using defaults")
    
    # Run command
    asyncio.run(run_command(args, config))


async def run_command(args, config):
    """Run the specified command"""
    engine = await create_engine(config)
    
    try:
        if args.command == "discover":
            await cmd_discover(args, engine)
        elif args.command == "engage":
            await cmd_engage(args, engine)
        elif args.command == "stats":
            await cmd_stats(args, engine)
        elif args.command == "login":
            await cmd_login(args, engine)
    finally:
        await engine.close()


if __name__ == "__main__":
    main()
