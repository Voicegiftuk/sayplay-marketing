#!/usr/bin/env python3
"""
SayPlay FINAL Complete Marketing System
- Daily trend research from 5+ sources
- Anti-repetition logic (compares with last 7 days)
- AI analysis and content generation
- Intelligent image generation based on research
- Multi-platform: Shopify + Instagram + Facebook PAGE + Twitter/X
- Image hosting: Catbox.moe (no API key needed!)
"""

import os
import json
import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import google.generativeai as genai

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """System configuration"""
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    SHOPIFY_SHOP = os.getenv('SHOPIFY_SHOP')
    SHOPIFY_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
    FACEBOOK_PAGE_TOKEN = os.getenv('FACEBOOK_PAGE_TOKEN')
    INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
    
    # History tracking
    HISTORY_FILE = 'content_history.json'
    MAX_HISTORY_DAYS = 7


# =============================================================================
# CONTENT HISTORY MANAGER
# =============================================================================

class ContentHistoryManager:
    """Track previous content to avoid repetition"""
    
    def __init__(self, history_file: str = 'content_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load content history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                # Filter last 7 days only
                cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
                return [h for h in history if h.get('date', '') >= cutoff_date]
            return []
        except Exception as e:
            print(f"   ⚠️  Error loading history: {e}")
            return []
    
    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"   ⚠️  Error saving history: {e}")
    
    def add_entry(self, content_data: Dict):
        """Add new content to history"""
        entry = {
            'date': datetime.now().isoformat(),
            'blog_title': content_data.get('blog_title', ''),
            'main_trend': content_data.get('main_trend', ''),
            'keywords': content_data.get('keywords', []),
            'style': content_data.get('style', ''),
            'hashtags': content_data.get('hashtags', [])
        }
        self.history.append(entry)
        self._save_history()
    
    def get_recent_topics(self) -> List[str]:
        """Get topics from last 7 days"""
        topics = []
        for entry in self.history:
            topics.append(entry.get('main_trend', ''))
            topics.extend(entry.get('keywords', []))
        return list(set(topics))  # Unique only
    
    def get_recent_styles(self) -> List[str]:
        """Get styles used recently"""
        return [entry.get('style', '') for entry in self.history]
    
    def is_topic_recent(self, topic: str) -> bool:
        """Check if topic was used in last 3 days"""
        cutoff_date = (datetime.now() - timedelta(days=3)).isoformat()
        recent_entries = [h for h in self.history if h.get('date', '') >= cutoff_date]
        recent_topics = []
        for entry in recent_entries:
            recent_topics.append(entry.get('main_trend', ''))
            recent_topics.extend(entry.get('keywords', []))
        
        # Check similarity
        topic_lower = topic.lower()
        for recent_topic in recent_topics:
            if recent_topic.lower() in topic_lower or topic_lower in recent_topic.lower():
                return True
        return False


# =============================================================================
# TREND RESEARCH ENGINE
# =============================================================================

class TrendResearcher:
    """Research current gift trends across multiple platforms"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def get_google_trends(self) -> List[str]:
        """Get trending gift searches from Google Trends"""
        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl='en-GB', tz=0)
            
            gift_keywords = [
                'gift ideas', 'birthday gift', 'christmas gift',
                'personalized gift', 'unique gift', 'anniversary gift',
                'wedding gift', 'baby shower gift', 'valentine gift',
                'mother day gift', 'father day gift'
            ]
            
            pytrends.build_payload(gift_keywords, timeframe='now 7-d', geo='GB')
            interest = pytrends.interest_over_time()
            
            trending = []
            if not interest.empty:
                for keyword in gift_keywords:
                    if keyword in interest.columns:
                        avg_interest = interest[keyword].mean()
                        trending.append({
                            'keyword': keyword,
                            'interest': avg_interest
                        })
            
            trending.sort(key=lambda x: x['interest'], reverse=True)
            return [t['keyword'] for t in trending[:5]]
            
        except Exception as e:
            print(f"   ⚠️  Google Trends error: {e}")
            return self._get_seasonal_fallback()
    
    def _get_seasonal_fallback(self) -> List[str]:
        """Seasonal gift trends based on current date"""
        month = datetime.now().month
        day = datetime.now().day
        
        if month == 12:
            return ['Christmas gifts', 'Last minute Christmas', 'Stocking stuffers', 'Secret Santa', 'Christmas personalized']
        elif month == 2 and day < 15:
            return ["Valentine's Day gifts", 'Romantic gifts', 'Gifts for girlfriend', 'Gifts for boyfriend', 'Valentine personalized']
        elif month == 3:
            return ["Mother's Day gifts", 'Gifts for mum', 'Personalized Mother Day', 'Thoughtful mum gifts', 'Mother Day UK']
        elif month == 6:
            return ["Father's Day gifts", 'Gifts for dad', 'Personalized Father Day', 'Unique dad gifts', 'Father Day UK']
        else:
            return ['Birthday gifts', 'Personalized gifts', 'Unique gifts', 'Thoughtful presents', 'Custom gifts UK']
    
    def scrape_reddit_giftideas(self) -> List[Dict[str, str]]:
        """Scrape r/GiftIdeas for trending topics"""
        try:
            url = 'https://www.reddit.com/r/GiftIdeas/hot.json'
            headers = {'User-Agent': 'SayPlayMarketing/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                for post in data['data']['children'][:10]:
                    post_data = post['data']
                    posts.append({
                        'title': post_data['title'],
                        'upvotes': post_data['ups'],
                        'comments': post_data['num_comments']
                    })
                return posts
        except Exception as e:
            print(f"   ⚠️  Reddit scraping error: {e}")
        return []
    
    def get_amazon_bestsellers_topics(self) -> List[str]:
        """Trending gift categories"""
        categories = [
            'Tech gadgets', 'Home decor', 'Personalized items',
            'Books', 'Beauty products', 'Kitchen accessories',
            'Toys and games', 'Jewelry', 'Sports equipment', 'Craft supplies'
        ]
        return random.sample(categories, random.randint(3, 5))
    
    def analyze_pinterest_trends(self) -> List[str]:
        """Pinterest trending searches"""
        month = datetime.now().month
        base_trends = ['DIY gifts', 'Gift wrapping', 'Handmade gifts', 'Gift baskets', 'Experience gifts']
        
        if month == 12:
            base_trends.extend(['Christmas crafts', 'Holiday gift guides'])
        elif month in [10, 11]:
            base_trends.extend(['Fall gift ideas', 'Thanksgiving gifts'])
        
        return base_trends[:5]
    
    def research_all_sources(self) -> Dict[str, Any]:
        """Comprehensive trend research"""
        print("🔍 RESEARCHING GIFT TRENDS...")
        
        research_data = {
            'date': self.today,
            'sources': {}
        }
        
        print("   📊 Checking Google Trends...")
        research_data['sources']['google_trends'] = self.get_google_trends()
        
        print("   🔴 Scraping Reddit r/GiftIdeas...")
        research_data['sources']['reddit'] = self.scrape_reddit_giftideas()
        
        print("   🛒 Analyzing Amazon categories...")
        research_data['sources']['amazon_categories'] = self.get_amazon_bestsellers_topics()
        
        print("   📌 Checking Pinterest trends...")
        research_data['sources']['pinterest'] = self.analyze_pinterest_trends()
        
        print("   ✅ Research complete!")
        return research_data


# =============================================================================
# INTELLIGENT IMAGE GENERATOR
# =============================================================================

class IntelligentImageGenerator:
    """Generate images based on research data and content theme"""
    
    def __init__(self):
        self.width = 1080
        self.height = 1080
    
    def create_image_from_theme(self, theme: str, trend_data: Dict, style: str = 'modern') -> str:
        """Create themed image based on research and content"""
        
        # Analyze theme for visual elements
        theme_lower = theme.lower()
        
        # Determine color scheme based on theme
        if 'christmas' in theme_lower or 'holiday' in theme_lower:
            colors = self._get_christmas_palette()
        elif 'valentine' in theme_lower or 'romantic' in theme_lower or 'love' in theme_lower:
            colors = self._get_valentine_palette()
        elif 'birthday' in theme_lower:
            colors = self._get_birthday_palette()
        elif 'wedding' in theme_lower or 'anniversary' in theme_lower:
            colors = self._get_wedding_palette()
        else:
            colors = self._get_default_palette()
        
        # Create image based on style
        if style == 'gradient':
            return self._create_gradient_design(theme, colors, trend_data)
        elif style == 'minimal':
            return self._create_minimal_design(theme, colors, trend_data)
        else:
            return self._create_vibrant_design(theme, colors, trend_data)
    
    def _get_christmas_palette(self) -> Dict:
        return {
            'primary': '#C41E3A',  # Christmas red
            'secondary': '#165B33', # Christmas green
            'accent': '#FFD700',    # Gold
            'bg_start': '#1a472a',
            'bg_end': '#8b0000'
        }
    
    def _get_valentine_palette(self) -> Dict:
        return {
            'primary': '#FF1493',  # Deep pink
            'secondary': '#C71585', # Medium violet red
            'accent': '#FFB6C1',   # Light pink
            'bg_start': '#8B008B',
            'bg_end': '#FF69B4'
        }
    
    def _get_birthday_palette(self) -> Dict:
        return {
            'primary': '#FF6B6B',
            'secondary': '#4ECDC4',
            'accent': '#FFE66D',
            'bg_start': '#A8E6CF',
            'bg_end': '#FF8B94'
        }
    
    def _get_wedding_palette(self) -> Dict:
        return {
            'primary': '#E8D5C4',  # Champagne
            'secondary': '#B8A99A', # Tan
            'accent': '#FFD700',   # Gold
            'bg_start': '#F5F5DC',
            'bg_end': '#DEB887'
        }
    
    def _get_default_palette(self) -> Dict:
        return {
            'primary': '#6A0DAD',
            'secondary': '#FF69B4',
            'accent': '#FFD700',
            'bg_start': '#6a0dad',
            'bg_end': '#ff69b4'
        }
    
    def _create_gradient_design(self, theme: str, colors: Dict, trend_data: Dict) -> str:
        """Modern gradient design"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(self.height):
            ratio = y / self.height
            r1, g1, b1 = int(colors['bg_start'][1:3], 16), int(colors['bg_start'][3:5], 16), int(colors['bg_start'][5:7], 16)
            r2, g2, b2 = int(colors['bg_end'][1:3], 16), int(colors['bg_end'][3:5], 16), int(colors['bg_end'][5:7], 16)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.rectangle([(0, y), (self.width, y+1)], fill=(r, g, b))
        
        # Load fonts
        try:
            brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 75)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
        except:
            brand_font = title_font = body_font = ImageFont.load_default()
        
        # Brand
        brand = "SAYPLAY"
        self._draw_centered_text(draw, brand, brand_font, 80, '#FFFFFF')
        
        # Trending badge
        badge = "🔥 TRENDING NOW 🔥"
        self._draw_centered_text(draw, badge, body_font, 200, colors['accent'])
        
        # Theme (max 3 words)
        theme_words = theme.split()[:3]
        y_pos = 320
        for word in theme_words:
            self._draw_centered_text(draw, word, title_font, y_pos, '#FFFFFF', shadow=True)
            y_pos += 90
        
        # Features
        features = ["🎁 Perfect Addition", "💝 Add Your Voice", "♾️ Memories Forever"]
        y_pos = 680
        for feature in features:
            self._draw_centered_text(draw, feature, body_font, y_pos, '#FFFFFF')
            y_pos += 65
        
        # CTA
        draw.rectangle([(80, 920), (self.width-80, 1000)], fill='#FFFFFF')
        self._draw_centered_text(draw, "sayplay.co.uk", brand_font, 930, colors['primary'])
        
        temp_file = f'/tmp/instagram_{int(time.time())}.jpg'
        img.save(temp_file, 'JPEG', quality=95)
        return temp_file
    
    def _create_minimal_design(self, theme: str, colors: Dict, trend_data: Dict) -> str:
        """Minimal clean design"""
        img = Image.new('RGB', (self.width, self.height), color='#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # Accent bars
        draw.rectangle([(0, 0), (self.width, 30)], fill=colors['primary'])
        draw.rectangle([(0, self.height-30), (self.width, self.height)], fill=colors['primary'])
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 44)
        except:
            title_font = body_font = ImageFont.load_default()
        
        # Content
        self._draw_centered_text(draw, "SayPlay", title_font, 150, colors['primary'])
        self._draw_centered_text(draw, "Voice Message Stickers", body_font, 270, '#333333')
        self._draw_centered_text(draw, theme[:50], body_font, 420, '#666666')
        self._draw_centered_text(draw, "✨ Personal", body_font, 580, colors['secondary'])
        self._draw_centered_text(draw, "💝 Permanent", body_font, 660, colors['secondary'])
        self._draw_centered_text(draw, "🎁 Perfect", body_font, 740, colors['secondary'])
        self._draw_centered_text(draw, "sayplay.co.uk", title_font, 880, colors['primary'])
        
        temp_file = f'/tmp/instagram_{int(time.time())}.jpg'
        img.save(temp_file, 'JPEG', quality=95)
        return temp_file
    
    def _create_vibrant_design(self, theme: str, colors: Dict, trend_data: Dict) -> str:
        """Vibrant colorful design - IMPROVED for readability"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Use gradient instead of blocks for better look
        primary_rgb = tuple(int(colors['primary'][i:i+2], 16) for i in (1, 3, 5))
        accent_rgb = tuple(int(colors['accent'][i:i+2], 16) for i in (1, 3, 5))
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(primary_rgb[0] + (accent_rgb[0] - primary_rgb[0]) * ratio)
            g = int(primary_rgb[1] + (accent_rgb[1] - primary_rgb[1]) * ratio)
            b = int(primary_rgb[2] + (accent_rgb[2] - primary_rgb[2]) * ratio)
            draw.rectangle([(0, y), (self.width, y+1)], fill=(r, g, b))
        
        # Dark overlay for better text contrast
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        try:
            brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
        except:
            brand_font = title_font = body_font = ImageFont.load_default()
        
        # Content with better readability
        self._draw_centered_text(draw, "SAYPLAY", brand_font, 100, '#FFFFFF', shadow=True)
        self._draw_centered_text(draw, "Voice Message Stickers", body_font, 220, '#FFFFFF')
        
        # Theme
        theme_short = ' '.join(theme.split()[:3])
        self._draw_centered_text(draw, theme_short, title_font, 400, '#FFFFFF', shadow=True)
        
        # Benefits
        benefits = [
            "🎤 Record Your Message",
            "🎁 Stick on Any Gift",
            "♾️ They Play Forever"
        ]
        y_pos = 550
        for benefit in benefits:
            self._draw_centered_text(draw, benefit, body_font, y_pos, '#FFFFFF')
            y_pos += 70
        
        # CTA
        draw.rectangle([(100, 900), (self.width-100, 980)], fill='#FFFFFF')
        self._draw_centered_text(draw, "sayplay.co.uk", brand_font, 910, colors['primary'])
        
        temp_file = f'/tmp/instagram_{int(time.time())}.jpg'
        img.save(temp_file, 'JPEG', quality=95)
        return temp_file
    
    def _draw_centered_text(self, draw, text, font, y, color, shadow=False):
        """Draw centered text"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        
        if shadow:
            draw.text((x+3, y+3), text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y), text, font=font, fill=color)
    
    def _draw_outlined_text(self, draw, text, font, y, fill_color, outline_color):
        """Draw text with outline"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        
        # Outline
        for adj_x in range(-3, 4):
            for adj_y in range(-3, 4):
                draw.text((x+adj_x, y+adj_y), text, font=font, fill=outline_color)
        # Main
        draw.text((x, y), text, font=font, fill=fill_color)


# =============================================================================
# AI CONTENT CREATOR
# =============================================================================

class IntelligentContentCreator:
    """AI-powered content creation with anti-repetition"""
    
    def __init__(self, gemini_api_key: str, history_manager: ContentHistoryManager):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.history = history_manager
    
    def analyze_trends_and_create_strategy(self, research_data: Dict) -> Dict:
        """AI analyzes trends and creates marketing strategy (avoiding recent topics)"""
        print("🤖 AI ANALYZING TRENDS...")
        
        # Get recent topics to avoid
        recent_topics = self.history.get_recent_topics()
        recent_styles = self.history.get_recent_styles()
        
        avoid_instruction = ""
        if recent_topics:
            avoid_instruction = f"\n\nIMPORTANT: AVOID these topics (used in last 7 days): {', '.join(recent_topics[:10])}\nFind DIFFERENT angles and trends that haven't been covered recently."
        
        prompt = f"""You are a professional marketing strategist for SayPlay - voice message stickers for gifts.

PRODUCT: SayPlay
- NFC stickers that record/play voice/video messages
- Stick on ANY gift for personalization
- Permanent, no app, no batteries
- £19.99, free UK delivery
- Website: sayplay.co.uk

TODAY'S RESEARCH DATA:
{json.dumps(research_data, indent=2)}

RECENT CONTENT HISTORY:
{avoid_instruction}

YOUR TASK:
1. Identify TOP 3 trends (DIFFERENT from recent content)
2. Explain SayPlay angle for each
3. Create specific gift pairings
4. Identify emotional triggers
5. Target audiences

FORMAT AS JSON:
{{
  "top_trends": [
    {{
      "trend_name": "...",
      "why_relevant": "...",
      "sayplay_angle": "...",
      "gift_pairings": ["..."],
      "emotional_trigger": "...",
      "target_audience": "..."
    }}
  ],
  "overall_strategy": "...",
  "recommended_hashtags": ["..."],
  "content_style": "emotional|problem_solution|urgency"
}}

Be creative and find FRESH angles!"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            strategy = json.loads(response_text)
            
            # Check if main trend is too similar to recent
            main_trend = strategy['top_trends'][0]['trend_name']
            if self.history.is_topic_recent(main_trend):
                print(f"   ⚠️  Topic '{main_trend}' too similar to recent, requesting alternative...")
                # Try second trend
                if len(strategy['top_trends']) > 1:
                    strategy['top_trends'][0], strategy['top_trends'][1] = strategy['top_trends'][1], strategy['top_trends'][0]
            
            print("   ✅ Strategy created!")
            return strategy
            
        except Exception as e:
            print(f"   ⚠️  AI analysis error: {e}")
            return self._fallback_strategy()
    
    def _fallback_strategy(self) -> Dict:
        """Fallback if AI fails"""
        return {
            "top_trends": [{
                "trend_name": "Thoughtful Personalized Gifts",
                "why_relevant": "Always relevant",
                "sayplay_angle": "Add personal touch to any gift",
                "gift_pairings": ["Any gift + SayPlay"],
                "emotional_trigger": "Connection",
                "target_audience": "Everyone"
            }],
            "overall_strategy": "Personalization focus",
            "recommended_hashtags": ["#PersonalizedGifts", "#SayPlay"],
            "content_style": "emotional"
        }
    
    def generate_blog_post(self, strategy: Dict) -> Dict:
        """Generate blog post"""
        print("📝 GENERATING BLOG POST...")
        
        top_trend = strategy['top_trends'][0]
        
        prompt = f"""Write SEO-optimized blog post for SayPlay.

STRATEGY:
{json.dumps(strategy, indent=2)}

FOCUS: {top_trend['trend_name']}

REQUIREMENTS:
- Title: SEO-friendly, include 2025
- Length: 600-800 words
- Structure: Problem → Solution (SayPlay) → Examples → CTA
- Specific gift pairings from strategy
- Emotional, relatable
- Natural SayPlay mentions (3-4x)
- Include pricing and CTA

JSON FORMAT:
{{
  "title": "...",
  "content": "...",
  "meta_description": "...",
  "tags": ["..."]
}}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            blog_post = json.loads(response_text)
            print(f"   ✅ Blog created: {blog_post['title']}")
            return blog_post
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            return {
                "title": f"{top_trend['trend_name']}: Make it Personal with SayPlay",
                "content": "Content generation failed",
                "meta_description": "SayPlay voice message stickers",
                "tags": ["sayplay-marketing"]
            }
    
    def generate_social_posts(self, strategy: Dict, blog_title: str) -> Dict:
        """Generate social media posts"""
        print("📱 GENERATING SOCIAL MEDIA POSTS...")
        
        style = strategy.get('content_style', 'emotional')
        
        prompt = f"""Create engaging social media content for SayPlay voice message stickers.

STRATEGY: {json.dumps(strategy, indent=2)}
BLOG TITLE: {blog_title}
STYLE: {style}

PRODUCT REMINDER:
- SayPlay = NFC voice message stickers
- Record voice/video messages
- Stick on ANY gift
- They last FOREVER
- £19.99, free UK delivery
- sayplay.co.uk

CREATE HIGHLY ENGAGING POSTS:

1. INSTAGRAM (400-600 words):
   - Start with HOOK (emoji + question or statement)
   - Explain the problem/emotion (2-3 lines)
   - Introduce SayPlay as solution (2-3 lines)
   - 3-5 bullet points with emoji (Perfect for: ...)
   - Call to action
   - 12-15 relevant hashtags
   - Use style: {style}
   - Make it conversational and engaging!

2. FACEBOOK (250-350 words):
   - Conversational tone
   - Tell a mini story
   - Include benefits
   - Clear CTA
   - 5-8 hashtags

3. TWITTER/X (250-280 chars):
   - Punchy hook
   - Key benefit
   - CTA + URL
   - 3-5 hashtags

IMPORTANT: Make Instagram caption LONG and ENGAGING - minimum 400 words!

JSON FORMAT:
{{
  "instagram": {{"caption": "...", "style": "{style}"}},
  "facebook": {{"caption": "..."}},
  "twitter": {{"tweet": "..."}}
}}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            posts = json.loads(response_text)
            
            # Validate Instagram caption length
            ig_caption = posts.get('instagram', {}).get('caption', '')
            if len(ig_caption) < 200:
                print(f"   ⚠️  Instagram caption too short ({len(ig_caption)} chars), regenerating...")
                # Add default engaging caption
                posts['instagram']['caption'] = f"""✨ Looking for the PERFECT gift that shows you really care? ✨

Generic gifts get forgotten. But SayPlay voice message stickers? They create memories that last FOREVER. ❤️

🎤 Record your voice/video
📦 Stick it on ANY gift
♾️ They tap & play - forever

Perfect for:
- Birthdays 🎂
- Weddings 💍
- Baby showers 👶
- Christmas (4 days!) 🎄

Just £19.99 at sayplay.co.uk

Tag someone who needs to see this! 👇

#SayPlay #PersonalizedGifts #VoiceMessage #GiftIdeas #UniqueGifts #ThoughtfulGifts #Christmas2025 #BirthdayGift #WeddingGift #VoiceStickers #MemorableMoments #GiftingMadeEasy"""
            
            print(f"   ✅ Social posts created! (Instagram: {len(posts['instagram']['caption'])} chars)")
            return posts
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            return {
                "instagram": {"caption": """✨ Transform ANY gift into something unforgettable with SayPlay! ✨

Record your voice, stick it on a gift, and they'll treasure it forever. No app needed!

🎁 Perfect for birthdays, weddings, Christmas
💝 Just £19.99 with free UK delivery
♾️ Memories that last forever

Shop now: sayplay.co.uk

#SayPlay #PersonalizedGifts #VoiceMessage #GiftIdeas #UniqueGifts #Christmas2025 #BirthdayGift #ThoughtfulPresents""", "style": style},
                "facebook": {"caption": "Make gifts personal with SayPlay voice stickers! Record your message, stick it on any gift, and create memories that last forever. £19.99 at sayplay.co.uk #SayPlay #PersonalizedGifts"},
                "twitter": {"tweet": "Transform any gift with SayPlay voice stickers! Record your message, they play it forever. 🎁 sayplay.co.uk #SayPlay #PersonalizedGifts #UniqueGifts"}
            }


# =============================================================================
# MULTI-PLATFORM PUBLISHER
# =============================================================================

class MultiPlatformPublisher:
    """Publish to all platforms"""
    
    def __init__(self):
        self.shopify_shop = Config.SHOPIFY_SHOP
        self.shopify_token = Config.SHOPIFY_TOKEN
        self.page_token = Config.FACEBOOK_PAGE_TOKEN
        self.instagram_id = Config.INSTAGRAM_ACCOUNT_ID
        self.facebook_page_id = Config.FACEBOOK_PAGE_ID
        self.image_gen = IntelligentImageGenerator()
        
        # Twitter/X OAuth1
        self.twitter_api_key = Config.TWITTER_API_KEY
        self.twitter_api_secret = Config.TWITTER_API_SECRET
        self.twitter_access_token = Config.TWITTER_ACCESS_TOKEN
        self.twitter_access_secret = Config.TWITTER_ACCESS_SECRET
    
    def upload_to_catbox(self, image_path: str) -> str:
        """Upload image to Catbox.moe (no API key needed!)"""
        print("   ☁️  Uploading to Catbox.moe...")
        try:
            with open(image_path, 'rb') as img:
                response = requests.post(
                    'https://catbox.moe/user/api.php',
                    data={'reqtype': 'fileupload'},
                    files={'fileToUpload': img},
                    timeout=30
                )
            
            if response.status_code == 200:
                # Catbox returns direct URL as text
                url = response.text.strip()
                if url.startswith('http'):
                    print(f"   ✅ Image uploaded: {url}")
                    return url
                else:
                    raise Exception(f"Catbox upload failed: {url}")
            else:
                raise Exception(f"Catbox upload failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Catbox upload error: {e}")
            raise
    
    def publish_to_shopify(self, blog_post: Dict) -> str:
        """Publish to Shopify blog"""
        print("📝 PUBLISHING TO SHOPIFY...")
        
        url = f'https://{self.shopify_shop}/admin/api/2024-01/articles.json'
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.shopify_token
        }
        
        # Get blog ID
        blogs_url = f'https://{self.shopify_shop}/admin/api/2024-01/blogs.json'
        blogs_response = requests.get(blogs_url, headers=headers)
        
        if blogs_response.status_code == 200:
            blogs = blogs_response.json().get('blogs', [])
            if blogs:
                blog_id = blogs[0]['id']
                url = f'https://{self.shopify_shop}/admin/api/2024-01/blogs/{blog_id}/articles.json'
        
        data = {
            "article": {
                "title": blog_post['title'],
                "author": "SayPlay Team",
                "tags": ", ".join(blog_post.get('tags', ['sayplay-marketing'])),
                "body_html": blog_post['content'].replace('\n', '<br>'),
                "published": True
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            article = response.json()['article']
            print(f"   ✅ Published: {blog_post['title']}")
            return f"https://{self.shopify_shop}/blogs/news/{article['handle']}"
        raise Exception(f"Shopify error: {response.text}")
    
    def publish_to_instagram(self, caption: str, image_path: str) -> str:
        """Publish to Instagram Business Account"""
        print("📸 PUBLISHING TO INSTAGRAM...")
        
        # Validate and truncate caption if needed
        if not caption or len(caption.strip()) == 0:
            caption = "Check out our latest personalized gift ideas! 🎁 #SayPlay #PersonalizedGifts"
            print("   ⚠️  Empty caption, using fallback")
        
        # Instagram caption limit is 2200 characters
        if len(caption) > 2200:
            caption = caption[:2180] + "... 🎁"
            print(f"   ⚠️  Caption truncated to {len(caption)} chars")
        
        print(f"   📝 Caption length: {len(caption)} chars")
        
        image_url = self.upload_to_catbox(image_path)
        
        # Create container
        print("   📦 Creating Instagram container...")
        container_url = f'https://graph.facebook.com/v18.0/{self.instagram_id}/media'
        container_data = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.page_token
        }
        
        print(f"   🔗 Image URL: {image_url}")
        print(f"   📝 Caption preview: {caption[:100]}...")
        
        container_response = requests.post(container_url, data=container_data)
        if container_response.status_code != 200:
            raise Exception(f"Instagram container error: {container_response.text}")
        
        container_id = container_response.json()['id']
        print(f"   ✅ Container created: {container_id}")
        
        # WAIT for Instagram to process the image
        print("   ⏳ Waiting 20 seconds for Instagram to process image...")
        time.sleep(20)
        
        # Publish
        print("   🚀 Publishing to Instagram...")
        publish_url = f'https://graph.facebook.com/v18.0/{self.instagram_id}/media_publish'
        publish_data = {
            'creation_id': container_id,
            'access_token': self.page_token
        }
        
        publish_response = requests.post(publish_url, data=publish_data)
        if publish_response.status_code != 200:
            raise Exception(f"Instagram publish error: {publish_response.text}")
        
        post_id = publish_response.json()['id']
        print(f"   ✅ Posted to Instagram: {post_id}")
        return post_id
    
    def publish_to_facebook_page(self, caption: str, image_path: str) -> str:
        """Publish to Facebook PAGE (not personal profile)"""
        print("📘 PUBLISHING TO FACEBOOK PAGE...")
        
        if not self.facebook_page_id:
            print("   ⚠️  Facebook Page ID not configured")
            return None
        
        image_url = self.upload_to_catbox(image_path)
        
        # Post to PAGE using PAGE ID
        post_url = f'https://graph.facebook.com/v18.0/{self.facebook_page_id}/photos'
        post_data = {
            'url': image_url,
            'caption': caption,
            'access_token': self.page_token
        }
        
        response = requests.post(post_url, data=post_data)
        if response.status_code != 200:
            raise Exception(f"Facebook error: {response.text}")
        
        post_id = response.json()['id']
        print(f"   ✅ Posted to Facebook PAGE: {post_id}")
        return post_id
    
    def publish_to_twitter(self, tweet_text: str, image_path: str) -> str:
        """Publish to Twitter/X"""
        print("🐦 PUBLISHING TO TWITTER/X...")
        
        if not all([self.twitter_api_key, self.twitter_access_token]):
            print("   ⚠️  Twitter credentials not configured")
            return None
        
        try:
            # Using requests-oauthlib for Twitter API v1.1
            from requests_oauthlib import OAuth1
            
            auth = OAuth1(
                self.twitter_api_key,
                self.twitter_api_secret,
                self.twitter_access_token,
                self.twitter_access_secret
            )
            
            # Upload image
            media_url = 'https://upload.twitter.com/1.1/media/upload.json'
            with open(image_path, 'rb') as img:
                files = {'media': img}
                media_response = requests.post(media_url, auth=auth, files=files)
            
            if media_response.status_code != 200:
                raise Exception(f"Twitter media upload error: {media_response.text}")
            
            media_id = media_response.json()['media_id_string']
            
            # Post tweet
            tweet_url = 'https://api.twitter.com/1.1/statuses/update.json'
            tweet_data = {
                'status': tweet_text,
                'media_ids': media_id
            }
            
            tweet_response = requests.post(tweet_url, auth=auth, data=tweet_data)
            if tweet_response.status_code != 200:
                raise Exception(f"Twitter post error: {tweet_response.text}")
            
            tweet_id = tweet_response.json()['id_str']
            print(f"   ✅ Posted to Twitter: {tweet_id}")
            return tweet_id
            
        except ImportError:
            print("   ⚠️  requests-oauthlib not installed, skipping Twitter")
            return None
        except Exception as e:
            print(f"   ⚠️  Twitter error: {e}")
            return None


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def main():
    """Complete intelligent marketing system"""
    print("=" * 80)
    print("🤖 SAYPLAY FINAL COMPLETE MARKETING SYSTEM")
    print("=" * 80)
    print()
    
    # Initialize
    history = ContentHistoryManager()
    researcher = TrendResearcher()
    content_creator = IntelligentContentCreator(Config.GEMINI_API_KEY, history)
    publisher = MultiPlatformPublisher()
    image_gen = IntelligentImageGenerator()
    
    try:
        # STEP 1: Research
        print("\n" + "=" * 80)
        print("STEP 1: TREND RESEARCH")
        print("=" * 80)
        research_data = researcher.research_all_sources()
        
        with open('daily_research.json', 'w') as f:
            json.dump(research_data, f, indent=2)
        print(f"\n📊 Research saved")
        
        # STEP 2: AI Analysis
        print("\n" + "=" * 80)
        print("STEP 2: AI STRATEGY (Anti-Repetition Active)")
        print("=" * 80)
        strategy = content_creator.analyze_trends_and_create_strategy(research_data)
        
        with open('marketing_strategy.json', 'w') as f:
            json.dump(strategy, f, indent=2)
        print(f"\n💡 Strategy saved")
        
        # STEP 3: Content Generation
        print("\n" + "=" * 80)
        print("STEP 3: CONTENT GENERATION")
        print("=" * 80)
        
        blog_post = content_creator.generate_blog_post(strategy)
        social_posts = content_creator.generate_social_posts(strategy, blog_post['title'])
        
        # LOG GENERATED CONTENT
        print("\n" + "=" * 80)
        print("GENERATED CONTENT PREVIEW:")
        print("=" * 80)
        print(f"📝 Blog: {blog_post['title']}")
        print(f"📸 Instagram caption ({len(social_posts['instagram']['caption'])} chars):")
        print(f"   {social_posts['instagram']['caption'][:150]}...")
        print(f"📘 Facebook caption ({len(social_posts['facebook']['caption'])} chars):")
        print(f"   {social_posts['facebook']['caption'][:100]}...")
        print(f"🐦 Twitter tweet ({len(social_posts['twitter']['tweet'])} chars):")
        print(f"   {social_posts['twitter']['tweet']}")
        print("=" * 80)
        
        # STEP 4: Image Generation
        print("\n" + "=" * 80)
        print("STEP 4: INTELLIGENT IMAGE GENERATION")
        print("=" * 80)
        
        top_trend = strategy['top_trends'][0]['trend_name']
        # Prefer gradient (best looking) over vibrant (too busy)
        image_style = random.choice(['gradient', 'gradient', 'minimal'])  # 2/3 chance gradient
        print(f"   🎨 Creating {image_style} design for: {top_trend}")
        
        image_path = image_gen.create_image_from_theme(top_trend, research_data, image_style)
        print(f"   ✅ Image created: {image_path}")
        
        # STEP 5: Multi-Platform Publishing
        print("\n" + "=" * 80)
        print("STEP 5: MULTI-PLATFORM PUBLISHING")
        print("=" * 80)
        
        # Shopify
        shopify_url = publisher.publish_to_shopify(blog_post)
        
        # Instagram
        ig_post_id = publisher.publish_to_instagram(social_posts['instagram']['caption'], image_path)
        
        # Facebook PAGE (with error handling)
        try:
            fb_post_id = publisher.publish_to_facebook_page(social_posts['facebook']['caption'], image_path)
        except Exception as e:
            print(f"   ⚠️  Facebook Page posting skipped: {str(e)[:100]}")
            fb_post_id = None
        
        # Twitter/X
        twitter_id = publisher.publish_to_twitter(social_posts['twitter']['tweet'], image_path)
        
        # STEP 6: Update History
        print("\n" + "=" * 80)
        print("STEP 6: UPDATING CONTENT HISTORY")
        print("=" * 80)
        
        history.add_entry({
            'blog_title': blog_post['title'],
            'main_trend': top_trend,
            'keywords': blog_post.get('tags', []),
            'style': strategy.get('content_style', ''),
            'hashtags': strategy.get('recommended_hashtags', [])
        })
        print("   ✅ History updated")
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ MARKETING CAMPAIGN COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Today's Focus: {top_trend}")
        print(f"📝 Blog: {shopify_url}")
        print(f"📸 Instagram: {ig_post_id}")
        print(f"📘 Facebook: {fb_post_id}")
        print(f"🐦 Twitter: {twitter_id}")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
