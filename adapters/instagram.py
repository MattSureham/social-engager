"""
Instagram Adapter
Implementation for Instagram
"""

import asyncio
import random
from typing import List, Dict, Optional, Any
from datetime import datetime

from .base import PlatformAdapter, Platform, Post, User, EngagementResult


class InstagramAdapter(PlatformAdapter):
    """Instagram platform adapter using Playwright"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False
    
    def get_platform(self) -> Platform:
        return Platform.INSTAGRAM
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        """Login to Instagram using Playwright"""
        try:
            from playwright.async_api import async_playwright
            
            username = credentials.get("username")
            password = credentials.get("password")
            
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=False)
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                
                # Go to Instagram login
                await self.page.goto("https://www.instagram.com/accounts/login/")
                await self.page.wait_for_load_state("networkidle")
                
                # Enter username
                await self.page.fill('input[name="username"]', username)
                await self.page.fill('input[name="password"]', password)
                
                # Click login
                await self.page.click('button[type="submit"]')
                await self.page.wait_for_load_state("networkidle")
                
                # Check if logged in
                if "accounts/login" not in self.page.url:
                    self.logged_in = True
                    return True
                
                await self.browser.close()
                return False
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    async def search_posts(
        self,
        query: str = None,
        hashtags: List[str] = None,
        location: str = None,
        limit: int = 20,
        **filters
    ) -> List[Post]:
        """Search for Instagram posts"""
        posts = []
        
        if not self.logged_in and self.page is None:
            await self._init_browser()
        
        # Build search URL
        search_term = query or " ".join(hashtags) if hashtags else ""
        
        try:
            # Go to explore page with search
            search_url = f"https://www.instagram.com/explore/search/keyword/?q={search_term}"
            await self.page.goto(search_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Wait for posts to load
            await asyncio.sleep(2)
            
            # Scroll to load more posts
            for _ in range(3):
                await self.page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(1)
            
            # Extract posts (simplified - real implementation needs more robust parsing)
            post_elements = await self.page.query_selector_all('article a')
            
            for elem in post_elements[:limit]:
                try:
                    href = await elem.get_attribute("href")
                    if href and "/p/" in href:
                        post_id = href.split("/p/")[1].split("/")[0]
                        posts.append(Post(
                            platform=Platform.INSTAGRAM,
                            post_id=post_id,
                            url=f"https://www.instagram.com/p/{post_id}/",
                            author="",  # Would need to fetch
                            author_id="",
                            content=""  # Would need to fetch
                        ))
                except:
                    continue
            
        except Exception as e:
            print(f"Search failed: {e}")
        
        return posts
    
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get a specific Instagram post"""
        if not self.page:
            await self._init_browser()
        
        try:
            await self.page.goto(f"https://www.instagram.com/p/{post_id}/")
            await self.page.wait_for_load_state("networkidle")
            
            # Extract post data (simplified)
            # In real implementation, parse the page HTML
            
            return Post(
                platform=Platform.INSTAGRAM,
                post_id=post_id,
                url=f"https://www.instagram.com/p/{post_id}/",
                author="extracted_author",
                author_id="extracted_author_id",
                content="extracted_content"
            )
        except Exception as e:
            print(f"Get post failed: {e}")
            return None
    
    async def get_user(self, username: str) -> Optional[User]:
        """Get Instagram user profile"""
        if not self.page:
            await self._init_browser()
        
        try:
            await self.page.goto(f"https://www.instagram.com/{username}/")
            await self.page.wait_for_load_state("networkidle")
            
            # Extract user data (simplified)
            return User(
                platform=Platform.INSTAGRAM,
                user_id=username,
                username=username,
                display_name=username
            )
        except Exception as e:
            print(f"Get user failed: {e}")
            return None
    
    async def comment(self, post_id: str, comment: str) -> EngagementResult:
        """Post a comment on an Instagram post"""
        if not self.logged_in:
            return EngagementResult(
                success=False,
                platform=Platform.INSTAGRAM,
                action="comment",
                post_id=post_id,
                error="Not logged in"
            )
        
        try:
            await self.page.goto(f"https://www.instagram.com/p/{post_id}/")
            await self.page.wait_for_load_state("networkidle")
            
            # Random delay to appear human
            await asyncio.sleep(random.uniform(1, 3))
            
            # Find comment box
            comment_box = await self.page.query_selector('textarea[aria-label="添加评论..."]')
            if comment_box:
                await comment_box.click()
                await self.page.fill('textarea[aria-label="添加评论..."]', comment)
                
                # Submit
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(1)
                
                return EngagementResult(
                    success=True,
                    platform=Platform.INSTAGRAM,
                    action="comment",
                    post_id=post_id,
                    message=comment
                )
            else:
                return EngagementResult(
                    success=False,
                    platform=Platform.INSTAGRAM,
                    action="comment",
                    post_id=post_id,
                    error="Comment box not found"
                )
                
        except Exception as e:
            return EngagementResult(
                success=False,
                platform=Platform.INSTAGRAM,
                action="comment",
                post_id=post_id,
                error=str(e)
            )
    
    async def like(self, post_id: str) -> EngagementResult:
        """Like an Instagram post"""
        if not self.logged_in:
            return EngagementResult(
                success=False,
                platform=Platform.INSTAGRAM,
                action="like",
                post_id=post_id,
                error="Not logged in"
            )
        
        try:
            await self.page.goto(f"https://www.instagram.com/p/{post_id}/")
            await self.page.wait_for_load_state("networkidle")
            
            # Find like button and click
            like_btn = await self.page.query_selector('svg[aria-label="赞"]')
            if like_btn:
                await like_btn.click()
                
                return EngagementResult(
                    success=True,
                    platform=Platform.INSTAGRAM,
                    action="like",
                    post_id=post_id
                )
            
            return EngagementResult(
                success=False,
                platform=Platform.INSTAGRAM,
                action="like",
                post_id=post_id,
                error="Like button not found"
            )
            
        except Exception as e:
            return EngagementResult(
                success=False,
                platform=Platform.INSTAGRAM,
                action="like",
                post_id=post_id,
                error=str(e)
            )
    
    async def follow(self, user_id: str) -> EngagementResult:
        """Follow an Instagram user"""
        # Similar implementation to like
        return EngagementResult(
            success=False,
            platform=Platform.INSTAGRAM,
            action="follow",
            post_id=user_id,
            error="Not implemented"
        )
    
    async def _init_browser(self):
        """Initialize browser if not already done"""
        if self.browser is None:
            from playwright.async_api import async_playwright
            self.browser = await async_playwright()..chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
    
    async def close(self):
        """Cleanup browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
            self.logged_in = False
    
    def is_logged_in(self) -> bool:
        return self.logged_in
