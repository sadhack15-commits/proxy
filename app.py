"""
Advanced Web Proxy Server
- Render HTML/CSS/JS như trình duyệt thật
- Mở được mọi website mượt mà
- Rewrite links để redirect qua proxy
- Anti-Cloudflare với realistic headers
"""

from flask import Flask, request, Response, render_template_string
import requests
from urllib.parse import urljoin, urlparse, quote
import re
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_realistic_headers():
    """Headers giả trình duyệt thật"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

def rewrite_urls(html_content, target_url, proxy_url):
    """Rewrite tất cả URLs trong HTML để redirect qua proxy"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        base_url = target_url.rsplit('/', target_url.count('/') - 2)[0] if target_url.count('/') > 2 else target_url
        
        # Rewrite <a> tags
        for tag in soup.find_all('a', href=True):
            original_url = tag['href']
            if original_url.startswith(('http://', 'https://')):
                new_url = f"{proxy_url}/proxy?url={quote(original_url)}"
            elif original_url.startswith('//'):
                new_url = f"{proxy_url}/proxy?url={quote('https:' + original_url)}"
            elif original_url.startswith('/'):
                new_url = f"{proxy_url}/proxy?url={quote(base_url + original_url)}"
            else:
                continue
            tag['href'] = new_url
        
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
        
        return str(soup)
    except Exception as e:
        print(f"Error rewriting URLs: {e}")
        return html_content

@app.route('/')
def home():
    """Trang chủ với search box"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌐 Advanced Web Proxy</title>
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
                padding: 10px;
                margin: 8px 0;
                background: white;
                border-radius: 8px;
                color: #667eea;
                text-decoration: none;
                transition: all 0.2s;
            }
            .example-link:hover {
                background: #667eea;
                color: white;
                transform: translateX(5px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Web Proxy</h1>
            <p class="subtitle">Duyệt web ẩn danh, mượt mà, không giới hạn</p>
            
            <form class="search-box" action="/proxy" method="GET">
                <input 
                    type="text" 
                    name="url" 
                    placeholder="Nhập URL (ví dụ: https://google.com)" 
                    required
                    value=""
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
                    <div class="feature-text">Ẩn danh</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🌍</div>
                    <div class="feature-text">Mọi website</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-text">Miễn phí</div>
                </div>
            </div>
            
            <div class="examples">
                <h3>📌 Thử ngay:</h3>
                <a class="example-link" href="/proxy?url=https://google.com">🔍 Google.com</a>
                <a class="example-link" href="/proxy?url=https://youtube.com">📺 YouTube.com</a>
                <a class="example-link" href="/proxy?url=https://facebook.com">📘 Facebook.com</a>
                <a class="example-link" href="/proxy?url=https://github.com">💻 GitHub.com</a>
                <a class="example-link" href="/proxy?url=https://vio.edu.vn">📚 VioEdu.vn</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/proxy')
def proxy():
    """Main proxy endpoint - render full website"""
    target_url = request.args.get('url')
    
    if not target_url:
        return "Missing URL parameter", 400
    
    # Add https:// if missing
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    try:
        # Get proxy URL
        proxy_url = request.url_root.rstrip('/')
        
        # Create session with realistic headers
        session = requests.Session()
        session.headers.update(get_realistic_headers())
        
        # Get the page
        response = session.get(target_url, timeout=30, allow_redirects=True)
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        
        # If HTML, rewrite URLs
        if 'text/html' in content_type:
            modified_content = rewrite_urls(response.text, target_url, proxy_url)
            return Response(
                modified_content,
                status=response.status_code,
                content_type='text/html; charset=utf-8'
            )
        else:
            # Return as-is for other content types
            return Response(
                response.content,
                status=response.status_code,
                headers=dict(response.headers)
            )
            
    except requests.exceptions.Timeout:
        return "Request timeout - Website took too long to respond", 504
    except requests.exceptions.RequestException as e:
        return f"Error loading website: {str(e)}", 502
    except Exception as e:
        return f"Unexpected error: {str(e)}", 500

@app.route('/asset')
def asset():
    """Proxy for assets (images, CSS, JS)"""
    asset_url = request.args.get('url')
    
    if not asset_url:
        return "Missing URL parameter", 400
    
    try:
        session = requests.Session()
        session.headers.update(get_realistic_headers())
        
        response = session.get(asset_url, timeout=15)
        
        return Response(
            response.content,
            status=response.status_code,
            headers={
                'Content-Type': response.headers.get('Content-Type', 'application/octet-stream'),
                'Cache-Control': 'public, max-age=3600'
            }
        )
    except Exception as e:
        return f"Error loading asset: {str(e)}", 502

@app.route('/health')
def health():
    """Health check"""
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("=" * 70)
    print("🌐 Advanced Web Proxy Server")
    print("=" * 70)
    print(f"🔗 Port: {port}")
    print("🚀 Ready to browse any website anonymously!")
    print("=" * 70)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
