"""
Discovery Module
Platform-agnostic post/user discovery
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from adapters.base import Platform, Post


@dataclass
class DiscoveryConfig:
    """Configuration for discovery"""
    platforms: List[Platform] = field(default_factory=lambda: [Platform.INSTAGRAM])
    hashtags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    location: Optional[str] = None
    min_likes: int = 0
    max_likes: int = 1000000
    posts_age_hours: int = 24  # Only posts from last X hours
    limit: int = 20
    exclude_users: List[str] = field(default_factory=list)
    exclude_hashtags: List[str] = field(default_factory=list)


@dataclass
class DiscoveredPost:
    """A discovered post ready for engagement"""
    post: Post
    engagement_score: float = 0.0
    reason: str = ""
    filters_passed: List[str] = field(default_factory=list)


class Discovery:
    """Cross-platform discovery engine"""
    
    def __init__(self, adapters: Dict[Platform, any]):
        self.adapters = adapters
    
    async def discover(
        self,
        config: DiscoveryConfig
    ) -> List[DiscoveredPost]:
        """Discover posts across platforms"""
        results = []
        
        for platform in config.platforms:
            adapter = self.adapters.get(platform)
            if not adapter:
                print(f"No adapter for {platform}")
                continue
            
            # Build search query
            query = " ".join(config.keywords) if config.keywords else None
            
            try:
                posts = await adapter.search_posts(
                    query=query,
                    hashtags=config.hashtags,
                    location=config.location,
                    limit=config.limit
                )
                
                for post in posts:
                    discovered = self._evaluate_post(post, config)
                    if discovered:
                        results.append(discovered)
            
            except Exception as e:
                print(f"Discovery failed for {platform}: {e}")
        
        # Sort by engagement score
        results.sort(key=lambda x: x.engagement_score, reverse=True)
        
        return results[:config.limit]
    
    def _evaluate_post(
        self,
        post: Post,
        config: DiscoveryConfig
    ) -> Optional[DiscoveredPost]:
        """Evaluate if a post should be engaged with"""
        filters_passed = []
        
        # Check user exclusions
        if post.author in config.exclude_users:
            return None
        
        # Check hashtag exclusions
        for hashtag in post.hashtags:
            if hashtag in config.exclude_hashtags:
                return None
        
        # Check likes range
        if post.likes < config.min_likes or post.likes > config.max_likes:
            return None
        
        # Calculate engagement score
        score = self._calculate_score(post, config)
        
        return DiscoveredPost(
            post=post,
            engagement_score=score,
            reason=self._get_reason(post, config),
            filters_passed=filters_passed
        )
    
    def _calculate_score(self, post: Post, config: DiscoveryConfig) -> float:
        """Calculate engagement score for a post"""
        score = 0.0
        
        # Like count scoring (normalize to 0-10)
        like_score = min(post.likes / 100, 10)
        score += like_score
        
        # Recency bonus
        if post.timestamp:
            hours_old = (datetime.now() - post.timestamp).total_seconds() / 3600
            if hours_old < 1:
                score += 5
            elif hours_old < 6:
                score += 3
            elif hours_old < 24:
                score += 1
        
        # Hashtag relevance
        for hashtag in post.hashtags:
            if hashtag.lower() in [h.lower() for h in config.hashtags]:
                score += 2
        
        # Keyword relevance
        for keyword in config.keywords:
            if keyword.lower() in post.content.lower():
                score += 3
        
        return score
    
    def _get_reason(self, post: Post, config: DiscoveryConfig) -> str:
        """Get human-readable reason for discovery"""
        reasons = []
        
        if post.hashtags:
            matching = [h for h in post.hashtags 
                       if h.lower() in [t.lower() for t in config.hashtags]]
            if matching:
                reasons.append(f"Matching hashtags: {', '.join(matching)}")
        
        if post.likes > 100:
            reasons.append(f"Good engagement: {post.likes} likes")
        
        if post.timestamp:
            hours_old = (datetime.now() - post.timestamp).total_seconds() / 3600
            if hours_old < 6:
                reasons.append("Recent post")
        
        return "; ".join(reasons) if reasons else "Matches criteria"
