#!/usr/bin/env python3
"""
ENTERPRISE AI MARKETING SYSTEM - 100% FREE!
============================================

Multi-AI orchestration system optimized for:
- Google SEO (traditional search)
- AI Search (ChatGPT, Claude, Perplexity, Gemini)
- Zero monthly costs
- Maximum reach and visibility

Author: Built for SayPlay
Version: 1.0 Enterprise (FIXED - Stable Gemini Model)
Budget: $0/month
"""

import os
import sys
import json
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import quote
import re

# AI & Research Libraries
import google.generativeai as genai
from duckduckgo_search import DDGS
import feedparser
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import io

# ============================================================================
# PRODUCT INFORMATION - SAYPLAY
# ============================================================================

SAYPLAY_PRODUCT = {
    'name': 'SayPlay Voice Message Sticker',
    'tagline': 'Just tap, no app!',
    'description': 'Magic tap-to-play stickers that add personal voice or video messages to any gift',
    
    'how_it_works': [
        'Tap phone to sticker - recording system opens automatically',
        'Record up to 60 seconds of audio OR 30 seconds of video',
        'Attach sticker to gift, card, or invitation',
        'Recipient taps phone to play - no app needed!'
    ],
    
    'key_features': [
        'No app required - just tap!',
        'No QR codes - clean, elegant design',
        'Works with any smartphone (iPhone & Android)',
        '60 seconds audio OR 30 seconds video recording',
        '12 months cloud storage',
        'Download message to keep forever',
        'Unlimited playbacks',
        'Share on social media',
        'Priority support (3+ packs)'
    ],
    
    'pricing': {
        'single': {
            'price': 8.99,
            'quantity': 1,
            'features': ['1 NFC Sticker', '60s Audio', '30s Video', '12 Months Storage', 'Unlimited Playbacks', 'Social Sharing']
        },
        'popular': {
            'price': 24.99,
            'original_price': 26.97,
            'quantity': 3,
            'save_percent': 8,
            'price_per': 8.33,
            'features': ['3 NFC Stickers', '60s Audio', '30s Video', '12 Months Storage', 'Unlimited Playbacks', 'Social Sharing', 'Priority Support'],
            'badge': 'Popular Pack'
        },
        'best_value': {
            'price': 49.99,
            'original_price': 53.94,
            'quantity': 6,
            'save_percent': 17,
            'price_per': 8.33,
            'bonus': '5+1 FREE!',
            'features': ['6 NFC Stickers (5+1 FREE!)', '60s Audio', '30s Video', '12 Months Storage', 'Unlimited Playbacks', 'Social Sharing', 'Priority Support'],
            'badge': 'Best Value'
        }
    },
    
    'use_cases': {
        'gifts': ['Birthday presents', 'Christmas gifts', 'Wedding gifts', 'Baby shower', 'Anniversary', 'Thank you gifts'],
        'invitations': ['Wedding invitations', 'Baptism (chrzciny)', 'Events', 'Save the dates', 'Party invites'],
        'cards': ['Birthday cards', 'Valentine cards', 'Christmas cards', 'Sympathy cards', 'Thank you cards'],
        'b2b': ['Florists (kwiaciarnie)', 'Gift shops', 'Wedding planners', 'Event organizers', 'Card retailers']
    },
    
    'website': 'https://sayplay.co.uk',
    'shop_url': 'https://sayplay.co.uk/products/voice-message-sticker',
    'contact': 'partnerships@sayplay.co.uk'
}

# ============================================================================
# FREE AI ORCHESTRATOR
# ============================================================================

class FreeAIOrchestrator:
    """
    Multi-AI system using only FREE services:
    - Gemini 1.5 Flash (stable, 15 RPM FREE)
    - DuckDuckGo search (unlimited FREE)
    - Pollinations.ai images (unlimited FREE)
    """
    
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        # Initialize Gemini with STABLE model (try multiple names for compatibility)
        genai.configure(api_key=self.gemini_key)
        
        # Try multiple model names (different APIs use different naming)
        model_names = [
            'gemini-1.5-flash-latest',  # Latest stable
            'gemini-1.5-flash',          # Without -latest suffix
            'gemini-1.5-flash-001',      # Version number
            'models/gemini-1.5-flash',   # With models/ prefix
        ]
        
        model_loaded = False
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test the model with a simple call
                test_response = self.model.generate_content("Hi")
                print(f"✅ FREE AI Orchestrator initialized")
                print(f"   🤖 Gemini Model: {model_name} (stable FREE tier - 15 RPM)")
                print(f"   🔍 DuckDuckGo Search: READY (unlimited)")
                print(f"   🎨 Pollinations.ai: READY (unlimited)")
                model_loaded = True
                break
            except Exception as e:
                print(f"   ⚠️ Model '{model_name}' failed: {str(e)[:50]}")
                continue
        
        if not model_loaded:
            raise ValueError(f"Could not load any Gemini model. Tried: {', '.join(model_names)}")
    
    def generate_content(self, prompt: str, max_retries: int = 2) -> str:
        """Generate content with Gemini (FREE 15 RPM, 1M TPM)"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                print(f"   ⚠️ Gemini attempt {attempt + 1} failed: {error_msg[:100]}")
                
                # Better error messages
                if "quota" in error_msg.lower():
                    print(f"   💡 TIP: Wait a moment for quota reset (rate: 15 requests/min)")
                elif "429" in error_msg:
                    print(f"   💡 TIP: Too many requests - system will retry in 2 seconds")
                
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    print(f"   ⚠️ All attempts failed, using fallback content")
                    raise
        return ""
    
    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """FREE unlimited web search with DuckDuckGo"""
        try:
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    'title': r['title'],
                    'snippet': r['body'],
                    'url': r['href']
                }
                for r in results
            ]
        except Exception as e:
            print(f"   ⚠️ DuckDuckGo search failed: {e}")
            return []
    
    def generate_image(self, prompt: str) -> str:
        """FREE unlimited image generation with Pollinations.ai"""
        try:
            # Pollinations.ai - NO API KEY, NO LIMITS!
            encoded_prompt = quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
            
            response = requests.get(image_url, timeout=30)
            
            if response.status_code == 200:
                temp_file = f'/tmp/generated_image_{int(time.time())}.jpg'
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                return temp_file
            else:
                raise Exception(f"Image generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Pollinations.ai failed: {e}")
            # Fallback to brand color gradient
            return self._create_fallback_image(prompt)
    
    def _create_fallback_image(self, theme: str) -> str:
        """Create simple gradient fallback image"""
        img = Image.new('RGB', (1080, 1080))
        draw = ImageDraw.Draw(img)
        
        # Orange gradient (SayPlay brand)
        for y in range(1080):
            ratio = y / 1080
            r = int(255 + (255 - 255) * ratio)
            g = int(140 + (107 - 140) * ratio)
            b = int(66 + (53 - 66) * ratio)
            draw.rectangle([(0, y), (1080, y+1)], fill=(r, g, b))
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Add text
        text = "SayPlay"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1080 - text_width) // 2
        y = (1080 - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)
        
        temp_file = f'/tmp/fallback_image_{int(time.time())}.jpg'
        img.save(temp_file, 'JPEG', quality=95)
        return temp_file

# ============================================================================
# FREE RESEARCH ENGINE
# ============================================================================

class FreeResearchEngine:
    """
    FREE research using:
    - RSS feeds (gift blogs)
    - DuckDuckGo search
    - BeautifulSoup scraping
    """
    
    def __init__(self, ai: FreeAIOrchestrator):
        self.ai = ai
        
        # UK Gift Blogs RSS Feeds (FREE!)
        self.rss_feeds = {
            'giftwhale': 'https://www.giftwhale.com/feed/',
            'prezzybox': 'https://www.prezzybox.com/blog/feed/',
        }
    
    def research_trends(self) -> Dict:
        """Comprehensive FREE trend research"""
        print("\n" + "=" * 80)
        print("STEP 1: FREE COMPETITIVE RESEARCH")
        print("=" * 80)
        
        trends = {
            'web_search': [],
            'blog_topics': [],
            'keywords': []
        }
        
        # 1. DuckDuckGo search (FREE unlimited!)
        print("   🔍 Searching web trends...")
        queries = [
            'best personalized gifts UK 2025',
            'unique gift ideas trending',
            'voice message gifts'
        ]
        
        for query in queries:
            results = self.ai.search_web(query, max_results=5)
            if results:
                trends['web_search'].extend(results)
                print(f"   ✅ Found {len(results)} results for '{query}'")
            time.sleep(1)  # Be polite
        
        # 2. RSS Feeds (FREE!)
        print("   📰 Checking gift blog RSS feeds...")
        for blog_name, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    trends['blog_topics'].append({
                        'source': blog_name,
                        'title': entry.title,
                        'link': entry.link
                    })
                print(f"   ✅ {blog_name}: {len(feed.entries[:3])} posts")
            except Exception as e:
                print(f"   ⚠️ {blog_name} RSS failed: {e}")
        
        # 3. Extract keywords with AI
        print("   🤖 AI analyzing trends...")
        all_text = "\n".join([
            f"{r['title']}: {r['snippet']}" 
            for r in trends['web_search'][:10]
        ])
        
        keyword_prompt = f"""
        Analyze these trending topics and extract:
        1. Top 5 trending themes
        2. Popular keywords
        3. Content opportunities for SayPlay voice message stickers
        
        Trends: {all_text}
        
        Return JSON format:
        {{
            "themes": ["theme1", "theme2", ...],
            "keywords": ["keyword1", "keyword2", ...],
            "opportunities": ["opportunity1", "opportunity2", ...]
        }}
        """
        
        try:
            analysis = self.ai.generate_content(keyword_prompt)
            # Extract JSON
            json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
            if json_match:
                trends['analysis'] = json.loads(json_match.group())
                print(f"   ✅ Identified {len(trends['analysis'].get('themes', []))} trending themes")
        except Exception as e:
            print(f"   ⚠️ Keyword analysis failed: {e}")
            trends['analysis'] = {
                'themes': ['personalized gifts', 'unique presents', 'voice messages'],
                'keywords': ['gift ideas', 'personalization', 'memorable'],
                'opportunities': ['emotional connection', 'lasting memories']
            }
        
        return trends

# ============================================================================
# AI-FIRST CONTENT GENERATOR
# ============================================================================

class AIFirstContentGenerator:
    """
    Generate content optimized for BOTH:
    - Traditional Google SEO
    - AI Search (ChatGPT, Claude, Perplexity)
    """
    
    def __init__(self, ai: FreeAIOrchestrator):
        self.ai = ai
    
    def generate_dual_optimized_blog(self, trends: Dict, history: List[str]) -> Dict:
        """
        Generate blog post optimized for Google + AI search engines
        """
        print("\n" + "=" * 80)
        print("STEP 2: DUAL-OPTIMIZED CONTENT GENERATION")
        print("=" * 80)
        
        # Select unique topic (avoid repetition)
        theme = self._select_unique_theme(trends, history)
        print(f"   🎯 Selected theme: {theme}")
        
        # Generate blog post with AI
        blog_prompt = f"""
Create a comprehensive blog post about: {theme}

PRODUCT CONTEXT:
- SayPlay voice message stickers
- Prices: £8.99 (1 sticker), £24.99 (3-pack), £49.99 (6-pack best value)
- 60s audio OR 30s video recording
- No app needed - just tap phone!
- 12 months storage + download to keep forever
- Use cases: gifts, invitations, cards, B2B partnerships

OPTIMIZATION REQUIREMENTS:

1. GOOGLE SEO:
- Title with year "2025" and primary keyword
- 1200-1500 words
- H2 and H3 headers
- Natural keyword integration
- Internal link opportunities
- Meta description

2. AI SEARCH OPTIMIZATION:
- Quick Answer section (first 100 words)
- FAQ section with clear Q&A format
- Specific pricing mentions (£8.99, £24.99, £49.99)
- Step-by-step how-to
- Citation-friendly format
- Source attribution
- Last updated date

3. CONTENT STRUCTURE:
- Hook (problem/question)
- Quick Answer (featured snippet worthy)
- Detailed explanation with examples
- How SayPlay solves the problem
- Pricing & packages
- Real use cases
- FAQ section
- Call to action

4. WRITING STYLE:
- Conversational but authoritative
- UK English
- Personal examples
- Data points when possible
- Emotional storytelling
- Clear benefits

Return the blog post in this format:
Title: [SEO-optimized title]
Meta Description: [155 chars max]
Tags: [tag1, tag2, tag3, tag4, tag5]

[Full blog content in markdown]
"""
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"   🤖 AI generation attempt {attempt + 1}/{max_retries}...")
                content = self.ai.generate_content(blog_prompt)
                
                # Parse content
                blog = self._parse_blog_content(content)
                
                if len(blog['content']) > 500:
                    print(f"   ✅ Blog post generated: {len(blog['content'])} chars")
                    
                    # Add schemas
                    blog['schemas'] = self._generate_schemas(blog, theme)
                    blog['theme'] = theme  # Save theme for history
                    
                    return blog
                else:
                    print(f"   ⚠️ Content too short, retrying...")
                    continue
                    
            except Exception as e:
                print(f"   ⚠️ Attempt {attempt + 1} failed: {str(e)[:100]}")
                if attempt < max_retries - 1:
                    time.sleep(3)  # Wait a bit longer before retry
                    continue
        
        # Fallback content
        print("   ⚠️ Using fallback content template")
        return self._create_fallback_blog(theme)
    
    def _select_unique_theme(self, trends: Dict, history: List[str]) -> str:
        """Select theme that hasn't been used recently"""
        
        # Theme pool
        themes = [
            "Creative Ways to Use Voice Message Gifts",
            "Best Personalized Gifts UK 2025",
            "Wedding Gift Ideas That Feel Thoughtful",
            "Birthday Gift Ideas Beyond Generic Cards",
            "Baby Shower Gifts New Parents Will Love",
            "Christmas Gift Ideas With Personal Touch",
            "Valentine's Day Gifts That Show You Care",
            "Anniversary Gift Ideas For Couples",
            "Thank You Gifts That Actually Mean Something",
            "Graduation Gifts They'll Remember Forever",
            "Long Distance Relationship Gift Ideas",
            "Gifts For Him That Aren't Generic",
            "Gifts For Her That Show Effort",
            "Corporate Gift Ideas That Stand Out",
            "Wedding Invitation Ideas That Get Noticed"
        ]
        
        # Add trending themes from research
        if 'analysis' in trends and 'themes' in trends['analysis']:
            for theme in trends['analysis']['themes']:
                themes.append(f"{theme.title()} - Ultimate Guide 2025")
        
        # Filter out recent themes
        recent_keywords = set()
        for hist in history[-7:]:  # Last 7 days
            recent_keywords.update(hist.lower().split())
        
        # Score themes
        scored_themes = []
        for theme in themes:
            theme_words = set(theme.lower().split())
            overlap = len(theme_words & recent_keywords)
            scored_themes.append((theme, overlap))
        
        # Sort by least overlap (most unique)
        scored_themes.sort(key=lambda x: x[1])
        
        # Return most unique theme
        return scored_themes[0][0]
    
    def _parse_blog_content(self, content: str) -> Dict:
        """Parse AI-generated blog content"""
        lines = content.strip().split('\n')
        
        blog = {
            'title': '',
            'meta_description': '',
            'tags': [],
            'content': '',
            'theme': ''  # ✅ FIXED: Always include theme key
        }
        
        content_start = 0
        for i, line in enumerate(lines):
            if line.startswith('Title:'):
                blog['title'] = line.replace('Title:', '').strip()
            elif line.startswith('Meta Description:'):
                blog['meta_description'] = line.replace('Meta Description:', '').strip()
            elif line.startswith('Tags:'):
                tags_str = line.replace('Tags:', '').strip()
                blog['tags'] = [t.strip() for t in tags_str.split(',')]
                content_start = i + 1
                break
        
        # Rest is content
        blog['content'] = '\n'.join(lines[content_start:]).strip()
        
        # Ensure we have required fields
        if not blog['title']:
            blog['title'] = "Voice Message Gifts - Ultimate Guide 2025"
        if not blog['meta_description']:
            blog['meta_description'] = f"Discover {SAYPLAY_PRODUCT['tagline']} Add personal voice messages to gifts from £8.99. No app needed!"
        if not blog['tags']:
            blog['tags'] = ['voice-message-gifts', 'personalized-gifts', 'sayplay', 'uk-gifts', 'gift-ideas-2025']
        
        return blog
    
    def _generate_schemas(self, blog: Dict, theme: str) -> Dict:
        """Generate schema markup for SEO and AI"""
        
        today = datetime.now().isoformat()
        
        schemas = {
            'article': {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": blog['title'],
                "description": blog['meta_description'],
                "author": {
                    "@type": "Organization",
                    "name": "SayPlay"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "SayPlay",
                    "url": SAYPLAY_PRODUCT['website']
                },
                "datePublished": today,
                "dateModified": today
            },
            'product': {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": SAYPLAY_PRODUCT['name'],
                "description": SAYPLAY_PRODUCT['description'],
                "brand": {
                    "@type": "Brand",
                    "name": "SayPlay"
                },
                "offers": {
                    "@type": "Offer",
                    "price": str(SAYPLAY_PRODUCT['pricing']['single']['price']),
                    "priceCurrency": "GBP",
                    "availability": "https://schema.org/InStock",
                    "url": SAYPLAY_PRODUCT['shop_url']
                }
            },
            'faq': {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "How much does SayPlay cost?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"SayPlay voice message stickers start from £{SAYPLAY_PRODUCT['pricing']['single']['price']} for a single sticker. Popular pack of 3 is £{SAYPLAY_PRODUCT['pricing']['popular']['price']}, and best value 6-pack (5+1 FREE) is £{SAYPLAY_PRODUCT['pricing']['best_value']['price']}."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Do I need an app to use SayPlay?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "No! SayPlay works without any app. Just tap your phone to the sticker and the recording system opens automatically. Recipients also just tap to play - no app needed for iPhone or Android."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "How long can I record?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "You can record up to 60 seconds of audio OR 30 seconds of video per sticker. Messages are stored in the cloud for 12 months and can be downloaded to keep forever."
                        }
                    }
                ]
            }
        }
        
        return schemas
    
    def _create_fallback_blog(self, theme: str) -> Dict:
        """High-quality fallback content"""
        
        title = f"{theme} | SayPlay Voice Message Gifts"
        
        content = f"""# {title}

## Quick Answer

Looking for meaningful {theme.lower()}? **SayPlay voice message stickers** (from £8.99) let you add personal 60-second voice or 30-second video messages to any gift, card, or invitation.

**Why SayPlay?**
- ✅ No app needed - just tap phone!
- ✅ From £8.99 with free UK delivery
- ✅ 60s audio OR 30s video recording
- ✅ Messages last forever (download to keep)
- ✅ Works with any smartphone

**Shop now**: [{SAYPLAY_PRODUCT['website']}]({SAYPLAY_PRODUCT['website']})

---

## The Problem With Generic Gifts

Generic gifts get forgotten. Cards get thrown away. But what if you could capture the emotion in your voice?

That's where SayPlay changes everything.

## What Are Voice Message Gifts?

SayPlay stickers are magic tap-to-play stickers that bring gifts to life:

1. **Tap** your phone to the sticker
2. **Record** up to 60 seconds of audio OR 30 seconds of video
3. **Attach** sticker to your gift, card, or invitation
4. **Recipient taps** their phone → your message plays!

No app download. No QR codes. Just tap and play! 🎵

## Why SayPlay Is Perfect For {theme}

### 🎯 Personal Connection

Unlike generic gifts, voice messages capture the emotion and warmth in your voice. Recipients can hear your laughter, feel your love, and treasure your words forever.

### 💰 Affordable

Starting from just £8.99, SayPlay makes any gift unforgettable without breaking the bank.

### ⚡ Instant Setup

Record your message in 2 minutes. No complicated setup, no technical knowledge needed.

### ♾️ Keeps Forever

Recipients can download messages and keep them forever. Unlike cards that get thrown away, voice messages become treasured keepsakes.

## Pricing & Packages

### 🎁 Single Sticker - £{SAYPLAY_PRODUCT['pricing']['single']['price']}

Perfect for: One special gift

**Includes**:
{chr(10).join([f"- ✅ {feature}" for feature in SAYPLAY_PRODUCT['pricing']['single']['features']])}

---

### 🔥 Popular Pack - £{SAYPLAY_PRODUCT['pricing']['popular']['price']} (Save {SAYPLAY_PRODUCT['pricing']['popular']['save_percent']}%!)

Perfect for: Multiple occasions

**Includes**:
{chr(10).join([f"- ✅ {feature}" for feature in SAYPLAY_PRODUCT['pricing']['popular']['features']])}

---

### ⭐ Best Value - £{SAYPLAY_PRODUCT['pricing']['best_value']['price']} (Save {SAYPLAY_PRODUCT['pricing']['best_value']['save_percent']}% + 1 FREE!)

Perfect for: Events, bulk needs

**Includes**:
{chr(10).join([f"- ✅ {feature}" for feature in SAYPLAY_PRODUCT['pricing']['best_value']['features']])}

---

## How It Works

{chr(10).join([f"{i+1}. **{step.split('-')[0].strip()}**: {step.split('-')[1].strip() if '-' in step else step}" for i, step in enumerate(SAYPLAY_PRODUCT['how_it_works'])])}

## Real Use Cases

{chr(10).join([f"### {category.title()}n{chr(10).join([f'- {use}' for use in uses[:3]])}" for category, uses in SAYPLAY_PRODUCT['use_cases'].items()])}

## Frequently Asked Questions

### How long can I record?
**Audio**: 60 seconds (perfect for heartfelt messages)
**Video**: 30 seconds (great for visual greetings)

### Do recipients need an app?
**NO!** Just tap any smartphone to the sticker. Works with iPhone and Android. No app download needed!

### Are there QR codes?
**NO!** That's the beauty - clean, elegant sticker with no ugly QR code. Just tap and play!

### What happens after 12 months?
You can **download your message anytime** and keep it forever! The 12 months is for cloud storage, but you own the recording.

### Can I use it multiple times?
**YES!** Unlimited playbacks. Tap as many times as you want.

### How do I record?
1. Tap phone to sticker
2. System opens automatically (no app!)
3. Record your message
4. Done! Now anyone can tap and listen

## Why Choose SayPlay?

| Feature | SayPlay | QR Codes | Greeting Cards | Digital Only |
|---------|---------|----------|----------------|--------------|
| **Price** | From £8.99 | Free but ugly | £3-5 (thrown away) | Free but no physical |
| **App needed** | ❌ NO! | ✅ YES (scanner) | N/A | ✅ YES |
| **Keeps forever** | ✅ Download | ❌ Link breaks | ❌ Gets binned | ❌ Lost in messages |
| **Visual appeal** | ✅ Elegant | ❌ Ugly code | ✅ Pretty but disposable | ❌ No physical |
| **Emotional impact** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## Get Started Today

**🎁 Ready to make your gifts unforgettable?**

**Choose your package**:
- **Try it**: 1 sticker - £{SAYPLAY_PRODUCT['pricing']['single']['price']}
- **Popular**: 3 stickers - £{SAYPLAY_PRODUCT['pricing']['popular']['price']} (save {SAYPLAY_PRODUCT['pricing']['popular']['save_percent']}%)
- **Best Value**: 6 stickers - £{SAYPLAY_PRODUCT['pricing']['best_value']['price']} (save {SAYPLAY_PRODUCT['pricing']['best_value']['save_percent']}% + 1 FREE!)

**👉 Shop now**: [{SAYPLAY_PRODUCT['website']}]({SAYPLAY_PRODUCT['website']})

**Free UK delivery on all orders!**

---

## Business Partnerships

Are you a florist, gift shop, or event planner?

**Partner with SayPlay**:
- Bulk pricing available
- Increase average order value
- Co-marketing opportunities

**Contact**: {SAYPLAY_PRODUCT['contact']}

---

*Last updated: {datetime.now().strftime('%d %B %Y')}*
*Source: SayPlay Official Blog*
*Author: SayPlay Team*
"""
        
        return {
            'title': title,
            'meta_description': f"Discover {theme.lower()} with SayPlay voice message stickers. From £8.99, no app needed. Add personal voice messages to any gift!",
            'tags': ['sayplay', 'voice-message-gifts', 'personalized-gifts', 'uk-gifts', 'gift-ideas-2025'],
            'content': content,
            'schemas': self._generate_schemas({'title': title, 'meta_description': ''}, theme),
            'theme': theme
        }

# ============================================================================
# FREE IMAGE GENERATOR
# ============================================================================

class FreeImageGenerator:
    """Generate professional images using FREE Pollinations.ai"""
    
    def __init__(self, ai: FreeAIOrchestrator):
        self.ai = ai
    
    def generate_blog_image(self, blog_title: str, theme: str) -> str:
        """Generate professional product image"""
        print("\n" + "=" * 80)
        print("STEP 3: FREE IMAGE GENERATION")
        print("=" * 80)
        
        # Create AI-optimized prompt
        prompt = f"""
        Professional product photography,
        voice message gift sticker on elegant wrapped present,
        {theme},
        soft natural lighting,
        lifestyle shot,
        high quality,
        no text,
        centered composition,
        warm and inviting atmosphere
        """
        
        print(f"   🎨 Theme: {theme}")
        print(f"   🎨 Generating with Pollinations.ai (FREE unlimited!)...")
        
        image_path = self.ai.generate_image(prompt)
        
        if image_path and os.path.exists(image_path):
            print(f"   ✅ Image generated: {image_path}")
            return image_path
        else:
            print(f"   ⚠️ Using fallback image")
            return self.ai._create_fallback_image(theme)

# ============================================================================
# MULTI-PLATFORM PUBLISHER
# ============================================================================

class MultiPlatformPublisher:
    """Publish to Shopify, Instagram, Facebook, Pinterest"""
    
    def __init__(self):
        self.shopify_shop = os.getenv('SHOPIFY_SHOP')
        self.shopify_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        self.fb_token = os.getenv('FACEBOOK_PAGE_TOKEN')
        self.ig_account = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        
        if not all([self.shopify_shop, self.shopify_token]):
            print("   ⚠️ Shopify credentials missing")
        
        print("✅ Multi-Platform Publisher initialized")
    
    def publish_to_shopify(self, blog: Dict) -> Optional[str]:
        """Publish blog to Shopify"""
        print("\n" + "=" * 80)
        print("STEP 4: PUBLISHING TO SHOPIFY")
        print("=" * 80)
        
        if not self.shopify_shop or not self.shopify_token:
            print("   ⚠️ Shopify not configured")
            return None
        
        try:
            # TODO: Replace YOUR_BLOG_ID with actual blog ID from Shopify
            url = f"https://{self.shopify_shop}/admin/api/2024-01/blogs/YOUR_BLOG_ID/articles.json"
            
            # Add schema markup to content
            schema_html = f"\n\n<!-- Schema Markup -->\n"
            for schema_type, schema_data in blog.get('schemas', {}).items():
                schema_html += f'<script type="application/ld+json">\n{json.dumps(schema_data, indent=2)}\n</script>\n'
            
            full_content = blog['content'] + schema_html
            
            data = {
                "article": {
                    "title": blog['title'],
                    "body_html": full_content,
                    "tags": ", ".join(blog['tags']),
                    "published": True,
                    "metafields": [
                        {
                            "namespace": "seo",
                            "key": "description",
                            "value": blog['meta_description'],
                            "type": "single_line_text_field"
                        }
                    ]
                }
            }
            
            headers = {
                "X-Shopify-Access-Token": self.shopify_token,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                article = response.json()['article']
                print(f"   ✅ Published: {blog['title']}")
                return str(article['id'])
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:200]}")
            return None
    
    def publish_to_instagram(self, caption: str, image_path: str) -> Optional[str]:
        """Publish to Instagram with error handling"""
        print("\n" + "=" * 80)
        print("STEP 5: PUBLISHING TO INSTAGRAM")
        print("=" * 80)
        
        if not self.fb_token or not self.ig_account:
            print("   ⚠️ Instagram not configured")
            return None
        
        try:
            # Validate caption
            if not caption or len(caption.strip()) == 0:
                caption = f"Add your voice to any gift! {SAYPLAY_PRODUCT['tagline']} From £8.99. sayplay.co.uk 🎁"
                print("   ⚠️ Using fallback caption")
            
            # Instagram limit
            if len(caption) > 2200:
                caption = caption[:2180] + "... 🎁"
            
            print(f"   📝 Caption: {len(caption)} chars")
            
            # Upload to Catbox (FREE!)
            with open(image_path, 'rb') as img:
                files = {'fileToUpload': img}
                data = {'reqtype': 'fileupload'}
                response = requests.post('https://catbox.moe/user/api.php', data=data, files=files, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Catbox upload failed: {response.status_code}")
            
            image_url = response.text.strip()
            print(f"   ✅ Image uploaded: {image_url}")
            
            # Create Instagram container
            container_url = f'https://graph.facebook.com/v18.0/{self.ig_account}/media'
            container_data = {
                'image_url': image_url,
                'caption': caption,
                'access_token': self.fb_token
            }
            
            print(f"   📦 Creating container...")
            container_response = requests.post(container_url, data=container_data, timeout=30)
            
            if container_response.status_code != 200:
                raise Exception(f"Container failed: {container_response.text}")
            
            container_id = container_response.json()['id']
            print(f"   ✅ Container: {container_id}")
            
            # Wait for Instagram to process
            print(f"   ⏳ Waiting 20 seconds...")
            time.sleep(20)
            
            # Publish
            publish_url = f'https://graph.facebook.com/v18.0/{self.ig_account}/media_publish'
            publish_data = {
                'creation_id': container_id,
                'access_token': self.fb_token
            }
            
            print(f"   🚀 Publishing...")
            publish_response = requests.post(publish_url, data=publish_data, timeout=30)
            
            if publish_response.status_code != 200:
                raise Exception(f"Publish failed: {publish_response.text}")
            
            post_id = publish_response.json()['id']
            print(f"   ✅ Posted to Instagram: {post_id}")
            return post_id
            
        except Exception as e:
            print(f"   ❌ Instagram error: {str(e)[:200]}")
            return None
    
    def publish_to_facebook(self, caption: str, image_path: str) -> Optional[str]:
        """Publish to Facebook Page (with error handling)"""
        print("\n" + "=" * 80)
        print("STEP 6: PUBLISHING TO FACEBOOK")
        print("=" * 80)
        
        try:
            # Upload to Catbox
            with open(image_path, 'rb') as img:
                files = {'fileToUpload': img}
                data = {'reqtype': 'fileupload'}
                response = requests.post('https://catbox.moe/user/api.php', data=data, files=files, timeout=30)
            
            image_url = response.text.strip()
            print(f"   ✅ Image uploaded: {image_url}")
            
            # Post to Facebook
            # Implementation here...
            print(f"   ⚠️ Facebook posting skipped (implement if needed)")
            return None
            
        except Exception as e:
            print(f"   ⚠️ Facebook skipped: {str(e)[:100]}")
            return None

# ============================================================================
# CONTENT HISTORY & ANTI-REPETITION
# ============================================================================

class ContentHistory:
    """Track content history to avoid repetition"""
    
    def __init__(self, history_file: str = 'content_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self, entry: Dict):
        """Save new entry to history"""
        self.history.append({
            'date': datetime.now().isoformat(),
            'title': entry.get('title', ''),
            'theme': entry.get('theme', ''),
            'platforms': entry.get('platforms', [])
        })
        
        # Keep last 30 days only
        cutoff = datetime.now() - timedelta(days=30)
        self.history = [
            h for h in self.history 
            if datetime.fromisoformat(h['date']) > cutoff
        ]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_recent_themes(self, days: int = 7) -> List[str]:
        """Get themes from last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            h['theme'] for h in self.history
            if datetime.fromisoformat(h['date']) > cutoff
        ]
        return recent

# ============================================================================
# MAIN ENTERPRISE SYSTEM
# ============================================================================

def main():
    """Run enterprise AI marketing system"""
    
    print("\n" + "=" * 80)
    print("🚀 ENTERPRISE AI MARKETING SYSTEM - 100% FREE!")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Product: {SAYPLAY_PRODUCT['name']}")
    print(f"Budget: $0/month")
    print(f"Version: 1.0 (FIXED - Stable Gemini 1.5 Flash)")
    print("=" * 80)
    
    try:
        # Initialize systems
        ai = FreeAIOrchestrator()
        research = FreeResearchEngine(ai)
        content_gen = AIFirstContentGenerator(ai)
        image_gen = FreeImageGenerator(ai)
        publisher = MultiPlatformPublisher()
        history = ContentHistory()
        
        # STEP 1: Research
        trends = research.research_trends()
        
        # Save research
        with open('daily_research.json', 'w') as f:
            json.dump(trends, f, indent=2)
        print("\n   💾 Research saved to daily_research.json")
        
        # STEP 2: Generate content
        recent_themes = history.get_recent_themes(days=7)
        blog = content_gen.generate_dual_optimized_blog(trends, recent_themes)
        
        # Save blog
        with open('generated_blog.json', 'w') as f:
            json.dump(blog, f, indent=2)
        print("\n   💾 Blog saved to generated_blog.json")
        
        # STEP 3: Generate image
        image_path = image_gen.generate_blog_image(blog['title'], blog.get('theme', 'gift ideas'))
        
        # STEP 4-6: Publish
        results = {
            'shopify': publisher.publish_to_shopify(blog),
            'instagram': publisher.publish_to_instagram(blog['content'][:400], image_path),
            'facebook': publisher.publish_to_facebook(blog['content'][:400], image_path)
        }
        
        # Update history
        history.save_history({
            'title': blog['title'],
            'theme': blog.get('theme', ''),
            'platforms': [k for k, v in results.items() if v]
        })
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ CAMPAIGN COMPLETE!")
        print("=" * 80)
        print(f"📝 Blog: {blog['title']}")
        print(f"📸 Instagram: {'✅' if results['instagram'] else '❌'}")
        print(f"📘 Facebook: {'✅' if results['facebook'] else '❌'}")
        print(f"🛒 Shopify: {'✅' if results['shopify'] else '❌'}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
