"""
Main Engine
Orchestrates discovery, engagement, and analytics
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime

from adapters.base import Platform, PlatformAdapter
from adapters.instagram import InstagramAdapter
from core.discovery import Discovery, DiscoveryConfig, DiscoveredPost
from core.engagement import Engagement, EngagementConfig, TargetAudience
from core.analytics import Analytics


class SocialEngagementEngine:
    """
    Main engine that orchestrates all components
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.adapters: Dict[Platform, PlatformAdapter] = {}
        self.discovery = None
        self.engagement = None
        self.analytics = Analytics()
    
    async def initialize(self):
        """Initialize adapters and components"""
        # Initialize adapters based on config
        platform_config = self.config.get("platforms", {})
        
        if "instagram" in platform_config:
            self.adapters[Platform.INSTAGRAM] = InstagramAdapter(
                platform_config["instagram"]
            )
        
        # Initialize discovery
        self.discovery = Discovery(self.adapters)
        
        # Initialize engagement (will need LLM)
        self.engagement = Engagement()
    
    async def login(self, platform: Platform, credentials: Dict) -> bool:
        """Login to a platform"""
        adapter = self.adapters.get(platform)
        if not adapter:
            raise ValueError(f"No adapter for {platform}")
        
        return await adapter.login(credentials)
    
    async def discover_and_engage(
        self,
        target_audience: TargetAudience,
        discovery_config: DiscoveryConfig,
        engagement_config: EngagementConfig
    ) -> Dict:
        """
        Run full discovery + engagement workflow
        """
        results = {
            "discovered": [],
            "engaged": [],
            "failed": []
        }
        
        # Phase 1: Discovery
        print("🔍 Discovering posts...")
        discovered = await self.discovery.discover(discovery_config)
        results["discovered"] = discovered
        
        print(f"Found {len(discovered)} posts to potentially engage with")
        
        # Phase 2: Filter already engaged
        if engagement_config.skip_already_engaged:
            to_engage = [
                d for d in discovered
                if not self.analytics.is_engaged(d.post.post_id)
            ]
            print(f"After filtering already engaged: {len(to_engage)} posts")
        else:
            to_engage = discovered
        
        # Phase 3: Engage
        for platform in discovery_config.platforms:
            adapter = self.adapters.get(platform)
            if not adapter:
                continue
            
            posts_to_engage = [d.post for d in to_engage if d.post.platform == platform]
            
            print(f"💬 Engaging on {len(posts_to_engage)} {platform.value} posts...")
            
            engagement_results = await self.engagement.engage(
                posts_to_engage,
                adapter,
                engagement_config,
                engagement_callback=self._on_engagement
            )
            
            results["engaged"].extend([r for r in engagement_results if r.success])
            results["failed"].extend([r for r in engagement_results if not r.success])
        
        return results
    
    def _on_engagement(self, post, result):
        """Callback when engagement completes"""
        self.analytics.record(
            result,
            post_author=post.author,
            comment=result.message or ""
        )
    
    async def close(self):
        """Cleanup resources"""
        for adapter in self.adapters.values():
            await adapter.close()
    
    def get_stats(self) -> Dict:
        """Get engagement statistics"""
        return self.analytics.get_total_stats()
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get daily statistics"""
        return self.analytics.get_daily_stats(days)


async def create_engine(config: Dict) -> SocialEngagementEngine:
    """Factory function to create engine"""
    engine = SocialEngagementEngine(config)
    await engine.initialize()
    return engine
