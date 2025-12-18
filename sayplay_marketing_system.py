#!/usr/bin/env python3
"""
SayPlay Shopify Marketing AI - Direct REST API Version
Posts to Shopify using direct REST API calls
£0 budget • 100% automatic • 2025 content
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
import re

# Optional imports
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# ==============================================
# CONFIGURATION
# ==============================================

class Config:
    """System configuration"""
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    SHOPIFY_SHOP = os.getenv('SHOPIFY_SHOP', '')
    SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN', '')
    
    BRAND = {
        'name': 'SayPlay',
        'product': 'NFC voice/video message stickers for gifts',
        'website': 'sayplay.co.uk',
        'tagline': 'Say It Once. They\'ll Play It Forever.',
        'price': '£19.99',
        'price_pack': '£49.99 for 5 stickers',
        'keywords_base': [
            'voice message gifts',
            'personalized gift ideas',
            'NFC gift cards',
            'video message gifts',
            'unique gifts 2025'
        ]
    }

# Initialize AI
print("\n🔌 CONNECTING SERVICES...")

API_AVAILABLE = False
client = None
if GENAI_AVAILABLE and Config.GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        API_AVAILABLE = True
        print("✅ Gemini AI")
    except:
        print("⚠️  Gemini AI unavailable")

SHOPIFY_CONNECTED = False
if Config.SHOPIFY_SHOP and Config.SHOPIFY_ACCESS_TOKEN:
    SHOPIFY_CONNECTED = True
    print("✅ Shopify REST API")
else:
    print("⚠️  Shopify credentials missing")

# ==============================================
# MARKET INTELLIGENCE
# ==============================================

class MarketIntelligence:
    """Real-time market research"""
    
    @staticmethod
    def generate_analysis():
        """Complete market analysis"""
        print("\n" + "="*60)
        print("🧠 MARKET INTELLIGENCE ENGINE")
        print("="*60)
        
        context = MarketIntelligence._get_seasonal_context()
        print(f"📅 {context['season']} {context['year']}")
        print(f"📅 {context['month']}")
        
        if context['upcoming_events']:
            print(f"🎉 {', '.join(context['upcoming_events'])}")
        
        # Get Google Trends
        trends = []
        if PYTRENDS_AVAILABLE:
            trends = MarketIntelligence._get_trends(Config.BRAND['keywords_base'])
        
        # Generate keywords
        keywords = [t['keyword'] for t in trends] if trends else Config.BRAND['keywords_base']
        seasonal = MarketIntelligence._generate_seasonal_keywords(context)
        keywords.extend(seasonal[:5])
        
        analysis = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'season': context['season'],
            'year': context['year'],
            'month': context['month'],
            'upcoming_events': context['upcoming_events'],
            'trending_keywords': keywords[:10],
            'trends_data': trends,
            'top_priority': MarketIntelligence._determine_priority(context, trends)
        }
        
        print(f"\n✅ Analysis complete!")
        print(f"   • {len(analysis['trending_keywords'])} keywords")
        
        return analysis
    
    @staticmethod
    def _get_trends(keywords):
        """Get Google Trends data"""
        try:
            print("🔍 Google Trends...")
            pytrends = TrendReq(hl='en-GB', tz=0)
            
            trends = []
            for keyword in keywords[:3]:
                try:
                    pytrends.build_payload([keyword], timeframe='today 3-m', geo='GB')
                    interest = pytrends.interest_over_time()
                    
                    if not interest.empty:
                        avg = int(interest[keyword].mean())
                        trends.append({'keyword': keyword, 'interest': avg})
                        print(f"   ✅ {keyword}: {avg}")
                    
                    time.sleep(1)
                except:
                    continue
            
            return sorted(trends, key=lambda x: x['interest'], reverse=True)
        except:
            return []
    
    @staticmethod
    def _get_seasonal_context():
        """Get season and events"""
        now = datetime.now()
        month = now.month
        
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"
        
        events = []
        for days in range(30):
            check = now + timedelta(days=days)
            if check.month == 12 and check.day == 25:
                events.append(f"Christmas ({days} days)")
            elif check.month == 2 and check.day == 14:
                events.append(f"Valentine's Day ({days} days)")
            elif check.month == 3 and 15 <= check.day <= 21:
                events.append(f"Mother's Day ({days} days)")
            elif check.month == 6 and 15 <= check.day <= 21:
                events.append(f"Father's Day ({days} days)")
        
        return {
            'season': season,
            'month': now.strftime('%B'),
            'year': now.year,
            'upcoming_events': events[:3]
        }
    
    @staticmethod
    def _generate_seasonal_keywords(context):
        """Generate seasonal keywords"""
        year = context['year']
        
        if context['season'] == 'Winter':
            return [f'christmas gifts {year}', f'winter gift ideas {year}']
        elif context['season'] == 'Spring':
            return [f'mothers day gifts {year}', f'spring gift ideas {year}']
        elif context['season'] == 'Summer':
            return [f'fathers day gifts {year}', f'summer gift ideas {year}']
        else:
            return [f'birthday gifts {year}', f'autumn gift ideas {year}']
    
    @staticmethod
    def _determine_priority(context, trends):
        """Determine priority"""
        year = context['year']
        
        if context['upcoming_events']:
            event = context['upcoming_events'][0]
            return f"Target {event} shoppers with {year} content"
        
        return f"Create {context['season']} {year} gift content"

# ==============================================
# CONTENT GENERATOR
# ==============================================

class ContentGenerator:
    """AI content generation"""
    
    @staticmethod
    def generate_blog_post(analysis):
        """Generate blog post"""
        print(f"\n📝 GENERATING BLOG POST...")
        
        main_keyword = analysis['trending_keywords'][0]
        year = analysis['year']
        season = analysis['season']
        
        print(f"   Keyword: {main_keyword}")
        print(f"   Season: {season} {year}")
        
        if not API_AVAILABLE or client is None:
            return ContentGenerator._fallback_blog(main_keyword, analysis)
        
        prompt = f"""Write SEO blog for SayPlay Shopify store.

TARGET: {main_keyword}
SEASON: {season} {year}

Write 1,200+ words HTML. Include:
- {year} references naturally
- {season} context
- Use "{main_keyword}" 5-7 times
- Emotional stories
- Product benefits (£19.99 NFC voice/video stickers)
- CTA to sayplay.co.uk

Clean HTML only (no markdown)."""

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            content = response.text
            
            if '```html' in content:
                content = content.split('```html')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            print("✅ AI generated!")
            return {
                'title': f"{main_keyword.title()} - {year} Guide | SayPlay",
                'content': content,
                'tags': ','.join(analysis['trending_keywords'][:5])
            }
        except Exception as e:
            print(f"⚠️  AI failed: {str(e)[:60]}")
            return ContentGenerator._fallback_blog(main_keyword, analysis)
    
    @staticmethod
    def _fallback_blog(keyword, analysis):
        """Fallback content"""
        year = analysis['year']
        season = analysis['season']
        
        html = f"""<p>Looking for <strong>{keyword}</strong> this {season} {year}? SayPlay is transforming gift-giving.</p>

<h2>Why Voice Message Gifts for {year}</h2>
<p>SayPlay lets you record voice or video messages that play back instantly. No apps needed.</p>

<h2>Perfect for {season} {year}</h2>
<ul>
<li>Birthday surprises with your voice</li>
<li>Anniversary messages they'll treasure</li>
<li>Baby shower congratulations</li>
<li>Graduation wisdom</li>
<li>{season} celebrations</li>
</ul>

<h2>How SayPlay Works</h2>
<ol>
<li><strong>Record:</strong> Voice or video on your phone</li>
<li><strong>Save:</strong> Message stored forever</li>
<li><strong>Stick:</strong> Attach to any gift</li>
</ol>

<h2>Why Choose SayPlay in {year}</h2>
<p><strong>No app required</strong> • <strong>Voice AND video</strong> • <strong>Never expires</strong> • <strong>Just £19.99</strong></p>

<h2>Real {year} Stories</h2>
<p>"Used SayPlay for grandmother's birthday. She plays it daily!" - Sarah, London</p>

<h2>Get Started</h2>
<p>Visit <a href="https://sayplay.co.uk">sayplay.co.uk</a> to order your SayPlay stickers.</p>

<p><strong>Say It Once. They'll Play It Forever.</strong></p>"""
        
        return {
            'title': f"{keyword.title()} - {year} Guide | SayPlay",
            'content': html,
            'tags': ','.join(analysis['trending_keywords'][:5])
        }

# ==============================================
# SHOPIFY REST API
# ==============================================

class ShopifyAPI:
    """Direct Shopify REST API calls"""
    
    @staticmethod
    def post_article(blog_data):
        """Post article via REST API"""
        if not SHOPIFY_CONNECTED:
            print("\n⚠️  Shopify not connected")
            return None
        
        try:
            print("\n🚀 POSTING TO SHOPIFY...")
            
            # Get blog ID
            blog_id = ShopifyAPI._get_blog_id()
            if not blog_id:
                print("❌ No blog found")
                return None
            
            # API endpoint
            url = f"https://{Config.SHOPIFY_SHOP}/admin/api/2024-10/blogs/{blog_id}/articles.json"
            
            headers = {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': Config.SHOPIFY_ACCESS_TOKEN
            }
            
            # Article data
            data = {
                'article': {
                    'title': blog_data['title'],
                    'body_html': blog_data['content'],
                    'tags': blog_data['tags'],
                    'published': True
                }
            }
            
            # POST request
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 201:
                article = response.json()['article']
                handle = article['handle']
                article_url = f"https://{Config.SHOPIFY_SHOP.replace('.myshopify.com', '.co.uk')}/blogs/news/{handle}"
                
                print(f"✅ Published!")
                print(f"   📝 {blog_data['title'][:60]}...")
                print(f"   🔗 {article_url}")
                
                return {
                    'success': True,
                    'id': article['id'],
                    'url': article_url,
                    'handle': handle
                }
            else:
                print(f"❌ Shopify error: {response.status_code}")
                print(f"   {response.text[:200]}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _get_blog_id():
        """Get blog ID via REST API"""
        try:
            url = f"https://{Config.SHOPIFY_SHOP}/admin/api/2024-10/blogs.json"
            
            headers = {
                'X-Shopify-Access-Token': Config.SHOPIFY_ACCESS_TOKEN
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                blogs = response.json().get('blogs', [])
                if blogs:
                    print(f"   📚 Found blog: {blogs[0]['title']}")
                    return blogs[0]['id']
            
            return None
        except:
            return None

# ==============================================
# LOCAL BACKUP
# ==============================================

class LocalBackup:
    """Save backup"""
    
    @staticmethod
    def save(blog_data, analysis):
        """Save files"""
        print("\n💾 SAVING BACKUP...")
        
        for d in ['_posts', 'data', 'reports']:
            Path(d).mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Blog
        keyword = analysis['trending_keywords'][0]
        slug = re.sub(r'[^\w\s-]', '', keyword.lower())
        slug = re.sub(r'[-\s]+', '-', slug)[:50]
        blog_file = f'_posts/{date_str}-{slug}.md'
        
        Path(blog_file).write_text(f"---\n{blog_data['title']}\n---\n\n{blog_data['content']}", encoding='utf-8')
        print(f"   ✅ {blog_file}")
        
        # Data
        data_file = f'data/market-{date_str}.json'
        Path(data_file).write_text(json.dumps(analysis, indent=2), encoding='utf-8')
        
        return {'blog': blog_file, 'data': data_file}

# ==============================================
# REPORTS
# ==============================================

class Reporter:
    """Generate reports"""
    
    @staticmethod
    def generate(analysis, shopify_result, files):
        """Generate report"""
        
        posts = len(list(Path('_posts').glob('*.md'))) if Path('_posts').exists() else 0
        
        report = f"""
╔════════════════════════════════════════════════╗
║   SAYPLAY SHOPIFY MARKETING REPORT            ║
║   {datetime.now().strftime('%B %d, %Y - %H:%M UTC')}                       ║
╚════════════════════════════════════════════════╝

🎯 {analysis['top_priority']}

📅 {analysis['season']} {analysis['year']} • {analysis['month']}

🔥 TOP KEYWORDS:
{chr(10).join(f'   {i+1}. {kw}' for i, kw in enumerate(analysis['trending_keywords'][:5]))}

📝 PUBLISHED:
- Shopify: {('✅ ' + shopify_result['url']) if shopify_result and shopify_result.get('success') else '❌ Failed'}
- Backup: {files['blog']}

📊 STATUS:
- Posts: {posts}
- AI: {"✅ Gemini" if API_AVAILABLE else "📦 Template"}
- Shopify: {"✅ Connected" if SHOPIFY_CONNECTED else "❌ Not connected"}

═══════════════════════════════════════════════
SayPlay Marketing AI • £0 • sayplay.co.uk/blogs/news
═══════════════════════════════════════════════
"""
        
        report_file = f'reports/daily-{datetime.now().strftime("%Y-%m-%d")}.txt'
        Path(report_file).write_text(report, encoding='utf-8')
        
        print(report)
        return report

# ==============================================
# MAIN
# ==============================================

def run_cycle():
    """Run marketing cycle"""
    
    print("\n" + "="*60)
    print("🤖 SAYPLAY SHOPIFY MARKETING AI")
    print("="*60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"🌐 sayplay.co.uk")
    print("="*60)
    
    try:
        # Market research
        analysis = MarketIntelligence.generate_analysis()
        
        # Generate content
        blog = ContentGenerator.generate_blog_post(analysis)
        
        # Post to Shopify
        shopify_result = ShopifyAPI.post_article(blog)
        
        # Save backup
        files = LocalBackup.save(blog, analysis)
        
        # Report
        report = Reporter.generate(analysis, shopify_result, files)
        
        print("\n" + "="*60)
        print("✅ COMPLETE!")
        print("="*60)
        
        if shopify_result and shopify_result.get('success'):
            print(f"\n🎉 LIVE: {shopify_result['url']}")
        
        return {'success': True}
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False}

if __name__ == "__main__":
    run_cycle()
