"""
Base Platform Adapter
Abstract interface that all platform adapters must implement
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Platform(Enum):
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"


@dataclass
class Post:
    """Represents a social media post"""
    platform: Platform
    post_id: str
    url: str
    author: str
    author_id: str
    content: str
    image_url: Optional[str] = None
    likes: int = 0
    comments_count: int = 0
    timestamp: Optional[datetime] = None
    location: Optional[str] = None
    hashtags: List[str] = None
    
    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []


@dataclass
class User:
    """Represents a social media user"""
    platform: Platform
    user_id: str
    username: str
    display_name: str
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    is_private: bool = False
    verified: bool = False


@dataclass
class EngagementResult:
    """Result of an engagement action"""
    success: bool
    platform: Platform
    action: str  # comment, like, follow
    post_id: str
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PlatformAdapter(ABC):
    """Base class for all platform adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform = self.get_platform()
    
    @abstractmethod
    def get_platform(self) -> Platform:
        """Return the platform this adapter handles"""
        pass
    
    @abstractmethod
    async def login(self, credentials: Dict[str, str]) -> bool:
        """
        Login to the platform
        Returns True if successful
        """
        pass
    
    @abstractmethod
    async def search_posts(
        self,
        query: str = None,
        hashtags: List[str] = None,
        location: str = None,
        limit: int = 20,
        **filters
    ) -> List[Post]:
        """
        Search for posts matching criteria
        """
        pass
    
    @abstractmethod
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get a specific post by ID"""
        pass
    
    @abstractmethod
    async def get_user(self, username: str) -> Optional[User]:
        """Get user profile"""
        pass
    
    @abstractmethod
    async def comment(self, post_id: str, comment: str) -> EngagementResult:
        """Post a comment on a post"""
        pass
    
    @abstractmethod
    async def like(self, post_id: str) -> EngagementResult:
        """Like a post"""
        pass
    
    @abstractmethod
    async def follow(self, user_id: str) -> EngagementResult:
        """Follow a user"""
        pass
    
    async def close(self):
        """Cleanup resources"""
        pass
    
    def is_logged_in(self) -> bool:
        """Check if currently logged in"""
        return True  # Override in subclass
