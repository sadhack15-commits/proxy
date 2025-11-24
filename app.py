"""
Advanced Web Proxy Server with Real Browser Fingerprinting
- Full browser headers rotation
- Anti-detection với realistic fingerprints
- Render HTML/CSS/JS như trình duyệt thật
- Bypass Cloudflare & anti-bot systems
"""

from flask import Flask, request, Response
import requests
from urllib.parse import quote
import os
import random
from bs4 import BeautifulSoup

app = Flask(__name__)

# Browser fingerprints thực từ nhiều nguồn - Perfect matching
BROWSER_FINGERPRINTS = [
    # Chrome 103 - Windows 10
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "cache-control": "max-age=0"
    },
    # Chrome 103 - Linux
    {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "cache-control": "max-age=0"
    },
    # Chrome 120 - macOS
    {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-ch-ua-full-version": '"120.0.6099.109"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "cache-control": "max-age=0"
    },
    # Firefox 121 - Windows 10
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "te": "trailers"
    },
    # Edge 120 - Windows 10
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-full-version": '"120.0.2210.91"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "cache-control": "max-age=0"
    },
    # Chrome 119 - Windows 11
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9,vi;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-full-version": '"119.0.6045.199"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "cache-control": "max-age=0"
    },
    # Safari 17 - macOS Sonoma
    {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "cache-control": "max-age=0"
    },
    # Chrome 118 - Android
    {
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1"
    },
    # Chrome 117 - Ubuntu
    {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "cache-control": "max-age=0"
    },
    # Firefox 120 - macOS
    {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "te": "trailers"
    }
]

def get_random_fingerprint():
    """Lấy fingerprint ngẫu nhiên từ pool - PERFECT MATCHING"""
    fingerprint = random.choice(BROWSER_FINGERPRINTS).copy()
    
    # Chuẩn hóa headers (capitalize keys theo HTTP standard)
    headers = {}
    for key, value in fingerprint.items():
        # Convert key to proper HTTP header format: User-Agent, Sec-Ch-Ua, etc
        proper_key = '-'.join(word.capitalize() for word in key.split('-'))
        headers[proper_key] = value
    
    # Thêm Connection header (quan trọng)
    headers['Connection'] = 'keep-alive'
    
    # Thêm Priority header cho Chrome-based browsers
    if 'Chrome' in headers.get('User-Agent', ''):
        headers['Priority'] = 'u=0, i'
    
    return headers

def rewrite_urls(html_content, target_url, proxy_url):
    """Rewrite tất cả URLs trong HTML để redirect qua proxy"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Parse base URL
        from urllib.parse import urlparse
        parsed = urlparse(target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Rewrite <a> tags
        for tag in soup.find_all('a', href=True):
            original_url = tag['href']
            if original_url.startswith(('http://', 'https://')):
                tag['href'] = f"{proxy_url}/proxy?url={quote(original_url)}"
            elif original_url.startswith('//'):
                tag['href'] = f"{proxy_url}/proxy?url={quote('https:' + original_url)}"
            elif original_url.startswith('/'):
                tag['href'] = f"{proxy_url}/proxy?url={quote(base_url + original_url)}"
        
        # Rewrite <img> tags
        for tag in soup.find_all('img', src=True):
            original_url = tag['src']
            if original_url.startswith(('http://', 'https://')):
                tag['src'] = f"{proxy_url}/asset?url={quote(original_url)}"
            elif original_url.startswith('//'):
                tag['src'] = f"{proxy_url}/asset?url={quote('https:' + original_url)}"
            elif original_url.startswith('/'):
                tag['src'] = f"{proxy_url}/asset?url={quote(base_url + original_url)}"
        
        # Rewrite <link> tags (CSS)
        for tag in soup.find_all('link', href=True):
            if tag.get('rel') and 'stylesheet' in tag.get('rel'):
                original_url = tag['href']
                if original_url.startswith(('http://', 'https://')):
                    tag['href'] = f"{proxy_url}/asset?url={quote(original_url)}"
                elif original_url.startswith('//'):
                    tag['href'] = f"{proxy_url}/asset?url={quote('https:' + original_url)}"
                elif original_url.startswith('/'):
                    tag['href'] = f"{proxy_url}/asset?url={quote(base_url + original_url)}"
        
        # Rewrite <script> tags
        for tag in soup.find_all('script', src=True):
            original_url = tag['src']
            if original_url.startswith(('http://', 'https://')):
                tag['src'] = f"{proxy_url}/asset?url={quote(original_url)}"
            elif original_url.startswith('//'):
                tag['src'] = f"{proxy_url}/asset?url={quote('https:' + original_url)}"
            elif original_url.startswith('/'):
                tag['src'] = f"{proxy_url}/asset?url={quote(base_url + original_url)}"
        
        # Rewrite <form> actions
        for tag in soup.find_all('form', action=True):
            original_url = tag['action']
            if original_url.startswith(('http://', 'https://')):
                tag['action'] = f"{proxy_url}/proxy?url={quote(original_url)}"
            elif original_url.startswith('/'):
                tag['action'] = f"{proxy_url}/proxy?url={quote(base_url + original_url)}"
        
        # Rewrite <video> and <source> tags
        for tag in soup.find_all(['video', 'source'], src=True):
            original_url = tag['src']
            if original_url.startswith(('http://', 'https://')):
                tag['src'] = f"{proxy_url}/asset?url={quote(original_url)}"
            elif original_url.startswith('//'):
                tag['src'] = f"{proxy_url}/asset?url={quote('https:' + original_url)}"
            elif original_url.startswith('/'):
                tag['src'] = f"{proxy_url}/asset?url={quote(base_url + original_url)}"
        
        # Rewrite CSS background images in style tags
        for tag in soup.find_all('style'):
            if tag.string:
                css = tag.string
                # Replace url() in CSS
                import re
                def replace_css_url(match):
                    url = match.group(1).strip('\'"')
                    if url.startswith(('http://', 'https://')):
                        return f"url('{proxy_url}/asset?url={quote(url)}')"
                    elif url.startswith('//'):
                        return f"url('{proxy_url}/asset?url={quote('https:' + url)}')"
                    elif url.startswith('/'):
                        return f"url('{proxy_url}/asset?url={quote(base_url + url)}')"
                    return match.group(0)
                
                css = re.sub(r'url\([\'"]?([^\'")]+)[\'"]?\)', replace_css_url, css)
                tag.string = css
        
        return str(soup)
    except Exception as e:
        print(f"Error rewriting URLs: {e}")
        return html_content

@app.route('/')
def home():
    """Trang chủ với search box"""
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <title>🌐 Advanced Web Proxy - Duyệt web ẩn danh</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.3);
                max-width: 700px;
                width: 100%;
            }
            h1 {
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3em;
                text-align: center;
                margin-bottom: 15px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 40px;
                font-size: 1.1em;
            }
            .search-box {
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
            }
            input[type="text"] {
                flex: 1;
                padding: 18px 20px;
                font-size: 1.1em;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                outline: none;
                transition: all 0.3s;
            }
            input[type="text"]:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            button {
                padding: 18px 35px;
                font-size: 1.1em;
                font-weight: 600;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }
            .feature {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .feature-text {
                color: #666;
                font-size: 0.9em;
                font-weight: 500;
            }
            .examples {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 12px;
            }
            .examples h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            .example-link {
                display: block;
                padding: 10px 15px;
                margin: 8px 0;
                background: white;
                border-radius: 8px;
                color: #667eea;
                text-decoration: none;
                transition: all 0.2s;
                font-weight: 500;
            }
            .example-link:hover {
                background: #667eea;
                color: white;
                transform: translateX(5px);
            }
            .badge {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 0.75em;
                font-weight: 600;
                margin-left: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Web Proxy</h1>
            <p class="subtitle">Duyệt web ẩn danh với browser fingerprinting thực</p>
            
            <form class="search-box" action="/proxy" method="GET">
                <input 
                    type="text" 
                    name="url" 
                    placeholder="Nhập URL (ví dụ: https://google.com)" 
                    required
                    autofocus
                >
                <button type="submit">🚀 Truy cập</button>
            </form>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-text">Siêu mượt</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔒</div>
                    <div class="feature-text">100% Ẩn danh</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🌍</div>
                    <div class="feature-text">Mọi website</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🛡️</div>
                    <div class="feature-text">Anti-detect</div>
                </div>
            </div>
            
            <div class="examples">
                <h3>📌 Thử ngay các website phổ biến:</h3>
                <a class="example-link" href="/proxy?url=https://google.com">
                    🔍 Google.com <span class="badge">HOT</span>
                </a>
                <a class="example-link" href="/proxy?url=https://youtube.com">
                    📺 YouTube.com
                </a>
                <a class="example-link" href="/proxy?url=https://facebook.com">
                    📘 Facebook.com
                </a>
                <a class="example-link" href="/proxy?url=https://github.com">
                    💻 GitHub.com
                </a>
                <a class="example-link" href="/proxy?url=https://vio.edu.vn">
                    📚 VioEdu.vn
                </a>
                <a class="example-link" href="/proxy?url=https://reddit.com">
                    🎯 Reddit.com
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/proxy')
def proxy():
    """Main proxy endpoint - render full website với real fingerprinting"""
    target_url = request.args.get('url')
    
    if not target_url:
        return "❌ Missing URL parameter", 400
    
    # Add https:// if missing
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    try:
        # Get proxy URL
        proxy_url = request.url_root.rstrip('/')
        
        # Create session with random fingerprint
        session = requests.Session()
        fingerprint = get_random_fingerprint()
        session.headers.update(fingerprint)
        
        # Add referer if navigating from proxy
        referer = request.headers.get('Referer')
        if referer and 'proxy?url=' in referer:
            session.headers['Referer'] = target_url
        
        # Get the page
        response = session.get(
            target_url, 
            timeout=30, 
            allow_redirects=True,
            verify=True
        )
        
        # Fix encoding - Let requests auto-detect from content
        if response.encoding == 'ISO-8859-1' and response.apparent_encoding:
            response.encoding = response.apparent_encoding
        
        # Check content type
        content_type = response.headers.get('Content-Type', '').lower()
        
        # If HTML, rewrite URLs
        if 'text/html' in content_type:
            # Get text with proper encoding
            try:
                html_text = response.text
            except UnicodeDecodeError:
                # Fallback: try common encodings
                for encoding in ['utf-8', 'gbk', 'gb2312', 'big5', 'shift_jis', 'euc-kr', 'iso-8859-1']:
                    try:
                        html_text = response.content.decode(encoding)
                        break
                    except:
                        continue
                else:
                    # Last resort: decode with error replacement
                    html_text = response.content.decode('utf-8', errors='replace')
            
            modified_content = rewrite_urls(html_text, target_url, proxy_url)
            
            # Return with proper headers
            resp = Response(
                modified_content,
                status=response.status_code,
                content_type='text/html; charset=utf-8'
            )
            
            # Copy some headers from original response
            for header in ['Set-Cookie', 'Content-Language']:
                if header in response.headers:
                    resp.headers[header] = response.headers[header]
            
            return resp
        else:
            # Return as-is for other content types
            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/octet-stream')
            )
            
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout - Website quá lâu để phản hồi", 504
    except requests.exceptions.SSLError:
        return "🔒 SSL Error - Không thể xác thực chứng chỉ website", 502
    except requests.exceptions.ConnectionError:
        return "🚫 Connection Error - Không thể kết nối tới website", 502
    except requests.exceptions.RequestException as e:
        return f"❌ Error loading website: {str(e)}", 502
    except Exception as e:
        return f"💥 Unexpected error: {str(e)}", 500

@app.route('/asset')
def asset():
    """Proxy for assets (images, CSS, JS) với fingerprinting"""
    asset_url = request.args.get('url')
    
    if not asset_url:
        return "Missing URL parameter", 400
    
    try:
        # Create session with random fingerprint
        session = requests.Session()
        fingerprint = get_random_fingerprint()
        session.headers.update(fingerprint)
        
        # Get asset
        response = session.get(asset_url, timeout=15, verify=True)
        
        # Return with proper caching
        resp = Response(
            response.content,
            status=response.status_code
        )
        
        # Set content type
        if 'Content-Type' in response.headers:
            resp.headers['Content-Type'] = response.headers['Content-Type']
        
        # Set caching headers
        resp.headers['Cache-Control'] = 'public, max-age=86400'
        
        return resp
        
    except Exception as e:
        print(f"Error loading asset: {e}")
        return "", 404

@app.route('/health')
def health():
    """Health check for UptimeRobot"""
    return {'status': 'healthy', 'fingerprints': len(BROWSER_FINGERPRINTS)}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("=" * 70)
    print("🌐 Advanced Web Proxy with Real Browser Fingerprinting")
    print("=" * 70)
    print(f"🔗 Port: {port}")
    print(f"🎭 Browser Fingerprints: {len(BROWSER_FINGERPRINTS)}")
    print("🚀 Ready to browse ANY website anonymously!")
    print("🛡️ Anti-detection enabled")
    print("=" * 70)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
