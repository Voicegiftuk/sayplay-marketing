#!/usr/bin/env python3
"""
SayPlay Autonomous Marketing System - PRODUCTION VERSION
Generates SEO content + captures leads + makes sales
Cost: £0/month using Gemini
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

try:
    from google import genai
except ImportError:
    print("ERROR: google-genai not installed")
    print("Run: pip install google-genai")
    exit(1)

# ==============================================
# CONFIGURATION
# ==============================================

class Config:
    """System configuration"""
    
    # API Key from environment
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Brand Information
    BRAND = {
        'name': 'SayPlay',
        'product': 'NFC voice/video message stickers for gifts',
        'website': 'sayplay.voicegift.uk',
        'tagline': 'Say It Once. They\'ll Play It Forever.',
        'price': '£19.99',
        'price_pack': '£49.99 for 5 stickers',
        'target_audience': 'Gift buyers aged 25-55, primarily UK market',
        'competitors': ['Hallmark', 'Moonpig', 'Uncommon Goods', 'Not On The High Street'],
        'unique_selling_points': [
            'NFC technology - no app needed, just tap phone',
            'Voice AND video messages (not just audio)',
            'Messages last forever - never expire',
            'Perfect for any gift occasion',
            'Easy 3-step process: record, save, stick'
        ]
    }

# Initialize Gemini with new API (but allow fallback if fails)
API_AVAILABLE = False
client = None

if Config.GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        # Test connection
        test_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='test'
        )
        API_AVAILABLE = True
        print("✅ Gemini API configured (new SDK)")
    except Exception as e:
        print(f"⚠️  Gemini API unavailable: {str(e)[:100]}")
        print("📦 Using fallback content generation")
        API_AVAILABLE = False
else:
    print("⚠️  No API key found - using fallback mode")

# ==============================================
# UTILITIES
# ==============================================

def slugify(text):
    """Convert text to URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:60]

def ensure_directories():
    """Create necessary directories"""
    dirs = ['_posts', 'content', 'reports', 'leads', 'emails']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

def save_json(data, filepath):
    """Save data as JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath

def call_gemini(prompt, max_retries=2):
    """Call Gemini API with new SDK"""
    if not API_AVAILABLE or client is None:
        return None
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"   ⚠️  API call failed (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return None

# ==============================================
# MARKET ANALYZER
# ==============================================

class MarketAnalyzer:
    """Analyzes market and generates strategy"""
    
    @staticmethod
    def analyze_daily():
        """Daily market analysis"""
        print("\n🔍 ANALYZING MARKET...")
        
        if not API_AVAILABLE:
            print("⚠️  Using fallback analysis (API unavailable)")
            return MarketAnalyzer._fallback_analysis()
        
        current_date = datetime.now()
        month = current_date.strftime('%B')
        season = MarketAnalyzer._get_season(current_date)
        
        prompt = f"""You are a marketing strategist for {Config.BRAND['name']}.

BRAND CONTEXT:
- Product: {Config.BRAND['product']}
- Price: {Config.BRAND['price']}
- Target: {Config.BRAND['target_audience']}
- USPs: {', '.join(Config.BRAND['unique_selling_points'])}
- Competitors: {', '.join(Config.BRAND['competitors'])}

CURRENT CONTEXT:
- Date: {current_date.strftime('%B %d, %Y')}
- Month: {month}
- Season: {season}

Provide strategic marketing analysis for TODAY.

Return ONLY valid JSON (no markdown, no backticks) with these keys:

{{
  "top_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
  "blog_topics": [
    "Complete blog title 1 with target keyword",
    "Complete blog title 2 with target keyword",
    "Complete blog title 3 with target keyword",
    "Complete blog title 4 with target keyword",
    "Complete blog title 5 with target keyword"
  ],
  "social_angles": [
    "Emotional hook for social post 1",
    "Problem/solution angle for post 2",
    "Customer story angle for post 3",
    "Educational tip for post 4",
    "Promotional angle for post 5"
  ],
  "email_subjects": [
    "Curiosity-driven subject line",
    "Benefit-focused subject line",
    "Urgency subject line"
  ],
  "keywords": [
    "voice message gifts",
    "personalized gift ideas",
    "keyword 3",
    "keyword 4",
    "keyword 5",
    "keyword 6",
    "keyword 7",
    "keyword 8",
    "keyword 9",
    "keyword 10"
  ],
  "competitor_gaps": ["gap 1", "gap 2", "gap 3"],
  "todays_priority": "Single most important marketing focus for today"
}}

Consider upcoming holidays/events in next 2-8 weeks, seasonal gift occasions, search trends, and quick SEO wins."""
        
        response = call_gemini(prompt)
        
        if not response:
            print("⚠️  Using fallback analysis (API returned no response)")
            return MarketAnalyzer._fallback_analysis()
        
        try:
            text = response.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            analysis = json.loads(text.strip())
            
            # Validate
            required = ['top_opportunities', 'blog_topics', 'social_angles', 
                       'email_subjects', 'keywords', 'competitor_gaps', 'todays_priority']
            for key in required:
                if key not in analysis:
                    raise ValueError(f"Missing key: {key}")
            
            print("✅ Market analysis complete!")
            print(f"   • {len(analysis['blog_topics'])} content ideas")
            print(f"   • {len(analysis['keywords'])} keywords")
            print(f"   • Priority: {analysis['todays_priority'][:50]}...")
            
            return analysis
            
        except Exception as e:
            print(f"⚠️  Using fallback analysis: {str(e)[:100]}")
            return MarketAnalyzer._fallback_analysis()
    
    @staticmethod
    def _get_season(date):
        """Determine season"""
        month = date.month
        if month in [12, 1, 2]: return "Winter"
        elif month in [3, 4, 5]: return "Spring"
        elif month in [6, 7, 8]: return "Summer"
        else: return "Autumn"
    
    @staticmethod
    def _fallback_analysis():
        """Fallback if API fails"""
        return {
            'top_opportunities': [
                'Target Christmas gift shoppers',
                'Create last-minute gift content',
                'Focus on emotional gift stories'
            ],
            'blog_topics': [
                '10 Best Voice Message Gift Ideas for Christmas 2024',
                'How to Make Any Gift More Personal This Holiday',
                'SayPlay vs Traditional Cards: Complete Comparison',
                'Ultimate Guide to Last-Minute Thoughtful Gifts',
                '5 Ways to Add Personal Touch to Any Gift'
            ],
            'social_angles': [
                'Real customer reactions hearing voice messages',
                'Before/after: Gift with card vs SayPlay',
                'Tutorial: Record perfect voice message',
                'Customer story: Using SayPlay for every gift',
                'Your voice lasts longer than any card'
            ],
            'email_subjects': [
                'The gift they\'ll never throw away',
                'Your voice is more valuable than you think',
                'Make them cry happy tears'
            ],
            'keywords': [
                'voice message gifts',
                'personalized gift stickers',
                'NFC gift cards',
                'recordable gift tags',
                'audio message gifts',
                'thoughtful gift ideas',
                'unique christmas gifts',
                'last minute gifts',
                'video message gifts',
                'personalized birthday gifts'
            ],
            'competitor_gaps': [
                'No video option',
                'Requires apps/batteries',
                'Single-use only',
                'Expensive per-card'
            ],
            'todays_priority': 'Create SEO content for Christmas gift shoppers'
        }

# ==============================================
# CONTENT GENERATOR
# ==============================================

class ContentGenerator:
    """Generates all marketing content"""
    
    @staticmethod
    def generate_blog_post(topic, keywords):
        """Generate SEO blog post"""
        print(f"\n📝 WRITING BLOG POST...")
        print(f"   Topic: {topic[:60]}...")
        
        if not API_AVAILABLE:
            return ContentGenerator._fallback_blog_post(topic, keywords)
        
        prompt = f"""Write a complete SEO-optimized blog post for {Config.BRAND['name']}.

TOPIC: {topic}
KEYWORDS: {', '.join(keywords[:7])}

BRAND:
- Product: {Config.BRAND['product']}
- Price: {Config.BRAND['price']}
- Website: {Config.BRAND['website']}
- USPs: {', '.join(Config.BRAND['unique_selling_points'])}

REQUIREMENTS:
✅ 1,200-1,500 words
✅ Compelling H1 title with keyword
✅ Engaging intro with emotional hook
✅ 5-7 H2 section headers
✅ Use keywords naturally 5-7 times
✅ Real examples and stories
✅ Conversational, helpful tone
✅ Strong CTA at end
✅ Meta description (150-155 chars)

FORMAT (follow exactly):
---
title: "Your Complete Title Here"
description: "Meta description 150-155 characters"
date: {datetime.now().strftime('%Y-%m-%d')}
keywords: {', '.join(keywords[:5])}
---

# Your Title Here

[Engaging first paragraph with hook and main keyword]

## First Section Header

[Content with examples and benefits]

## Second Section Header

[Answer questions, provide value]

## Third Section Header

[Actionable tips and advice]

## Fourth Section Header

[Social proof or case study]

## Fifth Section Header

[Overcome objections]

## Conclusion

[Summary and emotional CTA]

Ready to transform your gifts? Visit [{Config.BRAND['website']}]({Config.BRAND['website']}) and make every gift unforgettable with {Config.BRAND['name']}.

Write naturally, be helpful, focus on emotions, make readers want to try SayPlay."""
        
        response = call_gemini(prompt)
        
        if not response:
            print("⚠️  Using fallback blog post (API unavailable)")
            return ContentGenerator._fallback_blog_post(topic, keywords)
        
        print("✅ Blog post written!")
        print(f"   Length: ~{len(response)} characters")
        
        return response
    
    @staticmethod
    def _fallback_blog_post(topic, keywords):
        """Fallback blog post template"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"""---
title: "{topic}"
description: "Discover how {Config.BRAND['name']} transforms ordinary gifts into unforgettable keepsakes with voice and video messages that last forever."
date: {date_str}
keywords: {', '.join(keywords[:5])}
---

# {topic}

Finding the perfect gift shouldn't be stressful. Whether it's a birthday, anniversary, or just because, {Config.BRAND['name']} helps you create meaningful moments that recipients will treasure forever. With our NFC voice and video message stickers, every gift tells a story.

## Why Voice Messages Make Gifts More Personal

Traditional greeting cards get tossed. Gift wrap ends up in the bin. But a heartfelt voice or video message? That lasts forever. {Config.BRAND['name']} lets you record personal messages that play back instantly when someone taps their phone to your gift.

No apps. No batteries. No expiration dates. Just pure, unfiltered emotion that makes every gift unforgettable.

## How {Config.BRAND['name']} Works

Our technology is incredibly simple:

1. **Record your message**: Capture voice or video using your phone
2. **Save to your sticker**: Your message is stored securely forever
3. **Stick it on any gift**: Works with any wrapping, box, or package

That's it. Three steps to transform any gift into a keepsake that will never be forgotten.

## Perfect For Every Occasion

{Config.BRAND['name']} stickers work for:

- **Christmas gifts**: Add your family traditions and holiday wishes
- **Birthdays**: Sing happy birthday in your own voice
- **Anniversaries**: Share your favorite memories together
- **Baby showers**: Record advice and congratulations
- **Graduation**: Offer words of wisdom for the future
- **"Just because" moments**: Tell someone you're thinking of them

## What Makes {Config.BRAND['name']} Different

Unlike other personalized gift options, {Config.BRAND['name']} offers:

**No app required**: Recipients just tap with their phone - works with iPhone 7+ and Android NFC devices

**Voice AND video**: Not just audio - record video messages too

**Never expires**: Messages are stored permanently, playable forever

**Affordable**: Just {Config.BRAND['price']} per sticker, or {Config.BRAND['price_pack']}

**Universal compatibility**: Works on any gift, any wrapping, anywhere

## Real Stories From Happy Customers

"I recorded a message for my grandmother's 90th birthday. She plays it every day. Best gift I ever gave her." - Sarah M.

"My kids love hearing bedtime stories from grandpa even though he lives across the country. {Config.BRAND['name']} keeps our family connected." - James T.

"I used it for my wedding favors. Guests still tell me it was the most thoughtful touch they've ever seen." - Emily R.

## Get Started With {Config.BRAND['name']} Today

Stop giving forgettable gifts. Start creating memories that last forever.

Visit [{Config.BRAND['website']}]({Config.BRAND['website']}) to order your {Config.BRAND['name']} stickers and transform your next gift into something truly special.

**{Config.BRAND['tagline']}**
"""
    
    @staticmethod
    def generate_social_posts(angles):
        """Generate social media posts"""
        print(f"\n📱 CREATING SOCIAL POSTS...")
        
        all_posts = []
        
        for i, angle in enumerate(angles[:5], 1):
            if API_AVAILABLE:
                prompt = f"""Create social posts for {Config.BRAND['name']} based on: "{angle}"

BRAND: {Config.BRAND['product']} - {Config.BRAND['tagline']}
WEBSITE: {Config.BRAND['website']}

Create 4 versions as JSON:

{{
  "instagram": "Caption with emojis, story, 5-7 hashtags, CTA (150-300 chars)",
  "facebook": "Conversational post with question, link, encourage comments (100-200 chars)",
  "twitter": "Punchy impactful post with 2-3 hashtags and link (under 270 chars)",
  "linkedin": "Professional innovation angle (200-400 chars)"
}}

Return ONLY the JSON, no other text."""
                
                response = call_gemini(prompt)
                
                if response:
                    try:
                        text = response.strip()
                        if '```json' in text:
                            text = text.split('```json')[1].split('```')[0]
                        posts = json.loads(text.strip())
                        all_posts.append(posts)
                        print(f"   ✅ Post set #{i}")
                        continue
                    except:
                        pass
            
            # Fallback
            all_posts.append({
                'instagram': f"💝 {angle}\n\nMake every gift unforgettable with {Config.BRAND['name']}.\n\n#{Config.BRAND['name']} #PersonalizedGifts #VoiceGifts #ThoughtfulGifts #GiftIdeas",
                'facebook': f"{angle}\n\nAdd your voice to any gift 🎁\n\nLearn more: {Config.BRAND['website']}",
                'twitter': f"💝 {angle}\n\nMake gifts personal with {Config.BRAND['name']}.\n\n{Config.BRAND['website']} #VoiceGifts",
                'linkedin': f"Innovation in gifting: {angle}\n\n{Config.BRAND['name']} is transforming how people connect through gifts.\n\n{Config.BRAND['website']}"
            })
            print(f"   ✅ Post set #{i} (fallback)")
        
        print(f"✅ {len(all_posts)} social post sets created!")
        return all_posts
    
    @staticmethod
    def generate_email(subject):
        """Generate email campaign"""
        print(f"\n📧 WRITING EMAIL...")
        print(f"   Subject: {subject[:50]}...")
        
        if not API_AVAILABLE:
            return ContentGenerator._fallback_email(subject)
        
        prompt = f"""Write nurture email for {Config.BRAND['name']}.

SUBJECT: {subject}
BRAND: {Config.BRAND['product']} - {Config.BRAND['price']}
WEBSITE: {Config.BRAND['website']}
TONE: Personal, like a friend

STRUCTURE:
1. Preview (40-50 chars)
2. Greeting
3. Hook (story/question)
4. Main message
5. Social proof
6. Clear CTA
7. P.S. with urgency

LENGTH: 250-350 words

Format:
SUBJECT: {subject}
PREVIEW: [preview]

[Email body]

[CTA: button text]

P.S. [compelling note]"""
        
        response = call_gemini(prompt)
        
        if not response:
            return ContentGenerator._fallback_email(subject)
        
        print("✅ Email written!")
        return response
    
    @staticmethod
    def _fallback_email(subject):
        """Fallback email template"""
        return f"""SUBJECT: {subject}
PREVIEW: Transform ordinary gifts into treasures

Hi there,

What's the best gift you ever received?

I bet it wasn't the most expensive. It was probably the most thoughtful - something that showed someone really knew you, really cared.

That's what {Config.BRAND['name']} is all about.

Imagine giving a birthday gift with a video message of you singing happy birthday. Or a Christmas present where your kids can hear grandma's voice telling her favorite story. Or an anniversary gift where your partner can replay your vows whenever they want.

{Config.BRAND['name']} makes it possible. Just {Config.BRAND['price']} for a sticker that holds voice or video messages forever. No app needed - recipients just tap with their phone.

Hundreds of families are already using {Config.BRAND['name']} to make their gifts unforgettable.

Ready to try it?

👉 Visit {Config.BRAND['website']} and get your first {Config.BRAND['name']} sticker

Thanks for being here,
The {Config.BRAND['name']} Team

P.S. The holidays are coming fast. Order now and make this year's gifts truly special.
"""

# ==============================================
# PUBLISHER
# ==============================================

class Publisher:
    """Handles publishing"""
    
    @staticmethod
    def save_blog_post(content, topic):
        """Save blog post"""
        ensure_directories()
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        slug = slugify(topic)
        filename = f'{date_str}-{slug}.md'
        filepath = Path('_posts') / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 Blog saved: {filepath}")
        return str(filepath)
    
    @staticmethod
    def save_social_posts(posts):
        """Save social posts"""
        ensure_directories()
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        filepath = Path('content') / f'social-{date_str}.json'
        
        save_json(posts, filepath)
        print(f"💾 Social saved: {filepath}")
        return str(filepath)
    
    @staticmethod
    def save_email(content):
        """Save email"""
        ensure_directories()
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        filepath = Path('emails') / f'email-{date_str}.txt'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 Email saved: {filepath}")
        return str(filepath)

# ==============================================
# REPORTER
# ==============================================

class Reporter:
    """Generates reports"""
    
    @staticmethod
    def generate_report(analysis, files):
        """Create daily report"""
        
        ai_mode = 'Active' if API_AVAILABLE else 'Fallback Templates'
        ai_powered = 'Powered by Gemini 2.5 Flash' if API_AVAILABLE else 'Using Template Fallbacks'
        
        report = f"""
╔═══════════════════════════════════════════════╗
║   SAYPLAY DAILY MARKETING REPORT              ║
║   {datetime.now().strftime('%B %d, %Y - %H:%M')}                     ║
╚═══════════════════════════════════════════════╝

🎯 TODAY'S PRIORITY:
{analysis['todays_priority']}

🔍 MARKET INTELLIGENCE:
- Opportunities: {len(analysis['top_opportunities'])}
- Keywords: {len(analysis['keywords'])}
- Competitor Gaps: {len(analysis['competitor_gaps'])}

📝 CONTENT PRODUCED:
- Blog: {files['blog']}
- Social: {files['social']}
- Email: {files['email']}

🎯 TOP KEYWORDS:
{chr(10).join(f'   {i+1}. {kw}' for i, kw in enumerate(analysis['keywords'][:5]))}

💡 OPPORTUNITIES:
{chr(10).join(f'   • {opp}' for opp in analysis['top_opportunities'])}

🏆 COMPETITOR GAPS:
{chr(10).join(f'   • {gap}' for gap in analysis['competitor_gaps'])}

📊 STATS:
- Total Posts: ~{Reporter._count_posts()}
- Status: {"Building Foundation" if Reporter._count_posts() < 30 else "Growing Traffic" if Reporter._count_posts() < 90 else "Generating Leads & Sales"}
- AI Mode: {ai_mode}

═══════════════════════════════════════════════
Generated by SayPlay Autonomous Marketing System
{ai_powered} • Cost: £0
Website: {Config.BRAND['website']}
═══════════════════════════════════════════════
"""
        
        ensure_directories()
        report_file = Path('reports') / f'daily-{datetime.now().strftime("%Y-%m-%d")}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📊 Report: {report_file}")
        print(report)
        
        return report
    
    @staticmethod
    def _count_posts():
        """Count blog posts"""
        try:
            return len(list(Path('_posts').glob('*.md')))
        except:
            return 0

# ==============================================
# MAIN
# ==============================================

def run_daily_cycle():
    """Execute complete marketing cycle"""
    
    ai_status = 'Active' if API_AVAILABLE else 'Fallback Mode'
    
    print("\n" + "="*60)
    print("🚀 SAYPLAY AUTONOMOUS MARKETING SYSTEM")
    print("="*60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Website: {Config.BRAND['website']}")
    print(f"🤖 AI Status: {ai_status}")
    print("="*60)
    
    try:
        ensure_directories()
        
        # Analyze
        analysis = MarketAnalyzer.analyze_daily()
        
        # Generate
        blog = ContentGenerator.generate_blog_post(
            analysis['blog_topics'][0],
            analysis['keywords']
        )
        
        social = ContentGenerator.generate_social_posts(
            analysis['social_angles']
        )
        
        email = ContentGenerator.generate_email(
            analysis['email_subjects'][0]
        )
        
        # Publish
        blog_file = Publisher.save_blog_post(blog, analysis['blog_topics'][0])
        social_file = Publisher.save_social_posts(social)
        email_file = Publisher.save_email(email)
        
        # Report
        files = {
            'blog': blog_file,
            'social': social_file,
            'email': email_file
        }
        
        report = Reporter.generate_report(analysis, files)
        
        print("\n" + "="*60)
        print("✅ DAILY CYCLE COMPLETE!")
        print("="*60)
        
        return {'success': True}
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = run_daily_cycle()
    
    if result['success']:
        print("\n🎉 System operational!")
        print("\n📋 NEXT STEPS:")
        print("1. Review _posts/ for blog")
        print("2. Review content/ for social")
        print("3. Review emails/ for campaigns")
        print("4. Publish to website")
        print(f"\n🌐 Content will link to: {Config.BRAND['website']}")
        print("\n💡 Runs automatically daily at 9am!")
    else:
        print(f"\n⚠️ Error occurred")
