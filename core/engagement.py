"""
Engagement Module
Comment generation using LLM
"""

import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from adapters.base import Post, EngagementResult, Platform


@dataclass
class TargetAudience:
    """Definition of target audience"""
    interests: List[str]  # e.g., ["rock climbing", "outdoor fitness"]
    demographics: Dict[str, str]  # e.g., {"age": "18-35", "location": "New York"}
    pain_points: List[str]  # What they struggle with
    desires: List[str]  # What they want


@dataclass
class EngagementConfig:
    """Configuration for engagement actions"""
    audience: TargetAudience
    tone: str = "friendly"  # friendly, professional, casual, humorous
    max_daily: int = 20
    min_delay_seconds: int = 30
    max_delay_seconds: int = 120
    skip_already_engaged: bool = True


class Engagement:
    """Handles comment generation and posting"""
    
    def __init__(self, llm_wrapper=None):
        self.llm = llm_wrapper
    
    async def generate_comment(
        self,
        post: Post,
        config: EngagementConfig
    ) -> List[str]:
        """Generate multiple comment options for a post"""
        
        if not self.llm:
            # Fallback to template comments
            return self._generate_template_comments(post, config)
        
        # Build prompt for LLM
        prompt = self._build_comment_prompt(post, config)
        
        try:
            # Use LLM to generate comments
            response = self.llm.complete(prompt, temperature=0.8)
            
            # Parse response into list
            comments = self._parse_comments(response)
            return comments
        
        except Exception as e:
            print(f"LLM comment generation failed: {e}")
            return self._generate_template_comments(post, config)
    
    def _build_comment_prompt(self, post: Post, config: EngagementConfig) -> str:
        """Build prompt for comment generation"""
        
        audience_info = f"""
Target Audience:
- Interests: {', '.join(config.audience.interests)}
- Demographics: {json.dumps(config.audience.demographics)}
- Pain points: {', '.join(config.audience.pain_points)}
- Desires: {', '.join(config.audience.desires)}
"""
        
        post_info = f"""
Post Details:
- Author: {post.author}
- Content: {post.content}
- Hashtags: {', '.join(post.hashtags) if post.hashtags else 'None'}
- Likes: {post.likes}
"""
        
        prompt = f"""You are a social media engagement specialist. Generate 3-5 genuine, contextual comments for the following Instagram post.

{audience_info}

{post_info}

Requirements:
- Tone: {config.tone}
- Length: 1-3 sentences max
- Genuine and conversational
- NO generic spam like "great post!", "🔥🔥🔥", "nicee"
- Ask questions to start conversation
- Show you actually read/understood the post

Return ONLY a JSON array of strings, nothing else. Example:
["Comment 1", "Comment 2", "Comment 3"]
"""
        return prompt
    
    def _parse_comments(self, response: str) -> List[str]:
        """Parse LLM response into comment list"""
        try:
            # Try to find JSON array
            import re
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                comments = json.loads(match.group())
                if isinstance(comments, list):
                    return comments
            
            # Fallback: split by newlines
            lines = [l.strip() for l in response.split('\n') if l.strip()]
            return [l for l in lines if len(l) > 10]
        
        except:
            return []
    
    def _generate_template_comments(
        self,
        post: Post,
        config: EngagementConfig
    ) -> List[str]:
        """Generate template-based comments as fallback"""
        
        templates = [
            "This is exactly what I've been looking for! 👏",
            "Love this! What made you get into {interest}?",
            "This is inspiring! Any tips for beginners?",
            "Where is this? Looks amazing! 🧗",
            "This is goals! 🔥 How long have you been doing this?",
            "Just started getting into {interest} - this gives me motivation!",
            "The community around here is so supportive 💪",
            "Absolutely incredible shot! What camera/filter did you use?",
        ]
        
        # Personalize based on hashtags
        interest = post.hashtags[0] if post.hashtags else "this"
        
        comments = []
        for template in templates:
            comment = template.format(interest=interest)
            comments.append(comment)
        
        return comments[:5]
    
    async def engage(
        self,
        posts: List[Post],
        adapter: any,
        config: EngagementConfig,
        engagement_callback=None
    ) -> List[EngagementResult]:
        """Execute engagement on a list of posts"""
        results = []
        
        for i, post in enumerate(posts):
            # Check daily limit
            if i >= config.max_daily:
                print(f"Reached daily limit: {config.max_daily}")
                break
            
            # Random delay between actions (human-like)
            delay = random.randint(config.min_delay_seconds, config.max_delay_seconds)
            print(f"Waiting {delay}s before next engagement...")
            await asyncio.sleep(delay)
            
            # Generate comment
            comments = await self.generate_comment(post, config)
            
            if not comments:
                print(f"Skipping post {post.post_id} - no comments generated")
                continue
            
            # Use first comment
            comment = comments[0]
            
            # Post comment
            result = await adapter.comment(post.post_id, comment)
            results.append(result)
            
            if result.success:
                print(f"✅ Commented on {post.post_id}: {comment[:50]}...")
            else:
                print(f"❌ Failed: {result.error}")
            
            # Callback for tracking
            if engagement_callback:
                engagement_callback(post, result)
        
        return results


# Helper function for async import
import asyncio
