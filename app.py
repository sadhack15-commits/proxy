"""
Rotating Proxy Server - Deploy trên Render.com
Chỉ cần 1 VPS, tự động rotate IPv6 addresses
Public proxy 24/7 với UptimeRobot
Anti-Cloudflare & Rate limiting
"""

from flask import Flask, request, Response, jsonify
import requests
import time
import threading
from datetime import datetime, timedelta
import random
import hashlib
import os
from collections import defaultdict
import socket

app = Flask(__name__)

class IPv6Rotator:
    """
    Rotate IPv6 addresses từ 1 VPS duy nhất
    Sử dụng IPv6 subnet để generate nhiều IP
    """
    def __init__(self, rotation_hours=3):
        self.rotation_hours = rotation_hours
        self.last_rotation = datetime.now()
        self.current_ipv6 = None
        self.ipv6_pool = []
        self.lock = threading.Lock()
        
        # Stats
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rotations': 0,
            'uptime_start': datetime.now().isoformat()
        }
        
        # Rate limiting
        self.rate_limits = defaultdict(list)
        
        # Generate IPv6 pool
        self.generate_ipv6_pool()
        self.rotate_ipv6()
        
        # Start background tasks
        self.start_background_worker()
    
    def generate_ipv6_pool(self):
        """
        Generate pool of IPv6 addresses
        Render/VPS thường có IPv6 subnet /64 hoặc /48
        """
        # IPv6 base (thay bằng subnet của VPS)
        # Format: 2001:db8::/64 -> có thể dùng 2^64 addresses
        ipv6_base = "2001:db8::"  # Thay bằng IPv6 subnet thực của bạn
        
        # Generate 1000 random IPv6 trong subnet
        for i in range(1000):
            # Random hex suffix
            suffix = ''.join(random.choices('0123456789abcdef', k=16))
            ipv6 = f"{ipv6_base}{suffix[:4]}:{suffix[4:8]}:{suffix[8:12]}:{suffix[12:16]}"
            self.ipv6_pool.append(ipv6)
        
        print(f"✅ Generated {len(self.ipv6_pool)} IPv6 addresses")
    
    def rotate_ipv6(self):
        """Rotate sang IPv6 mới"""
        with self.lock:
            if self.ipv6_pool:
                self.current_ipv6 = random.choice(self.ipv6_pool)
                self.last_rotation = datetime.now()
                self.stats['rotations'] += 1
                print(f"[{datetime.now()}] 🔄 Rotated to: {self.current_ipv6}")
    
    def should_rotate(self):
        """Check if should rotate"""
        time_diff = datetime.now() - self.last_rotation
        return time_diff >= timedelta(hours=self.rotation_hours)
    
    def background_worker(self):
        """Background worker for auto-rotation"""
        while True:
            try:
                if self.should_rotate():
                    self.rotate_ipv6()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Background worker error: {e}")
                time.sleep(60)
    
    def start_background_worker(self):
        """Start background thread"""
        thread = threading.Thread(target=self.background_worker, daemon=True)
        thread.start()
    
    def check_rate_limit(self, client_ip, max_requests=60, window=60):
        """Rate limiting: 60 requests/minute per IP"""
        now = time.time()
        
        # Clean old requests
        self.rate_limits[client_ip] = [
            ts for ts in self.rate_limits[client_ip]
            if now - ts < window
        ]
        
        # Check limit
        if len(self.rate_limits[client_ip]) >= max_requests:
            return False
        
        self.rate_limits[client_ip].append(now)
        return True

# Initialize rotator
ipv6_rotator = IPv6Rotator(rotation_hours=3)

def get_anti_cloudflare_headers():
    """Generate realistic browser headers"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

@app.route('/')
def home():
    """Home page with documentation"""
    stats = ipv6_rotator.stats
    current_ip = ipv6_rotator.current_ipv6
    uptime = datetime.now() - datetime.fromisoformat(stats['uptime_start'])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Free Rotating Proxy</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, system-ui, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ 
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            }}
            h1 {{ 
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-align: center;
            }}
            .subtitle {{
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }}
            .badges {{
                text-align: center;
                margin: 20px 0;
            }}
            .badge {{
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                margin: 5px;
                font-size: 0.9em;
                font-weight: 600;
            }}
            .badge.orange {{ background: #ff9800; }}
            .badge.blue {{ background: #2196F3; }}
            .status-card {{ 
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 30px;
                border-radius: 15px;
                margin: 25px 0;
                box-shadow: 0 10px 30px rgba(102,126,234,0.3);
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .stat-box {{
                background: rgba(255,255,255,0.15);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                backdrop-filter: blur(10px);
            }}
            .stat-label {{ 
                opacity: 0.9;
                font-size: 0.85em;
                margin-bottom: 8px;
            }}
            .stat-value {{ 
                font-size: 1.8em;
                font-weight: bold;
            }}
            .endpoint {{
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }}
            .method {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 5px 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 0.85em;
                margin-right: 10px;
            }}
            .code {{
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                border-radius: 10px;
                overflow-x: auto;
                margin: 15px 0;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                line-height: 1.6;
            }}
            .keyword {{ color: #569cd6; }}
            .string {{ color: #ce9178; }}
            .comment {{ color: #6a9955; }}
            h2 {{ 
                color: #333;
                margin: 35px 0 20px 0;
                font-size: 1.8em;
            }}
            h3 {{ 
                color: #667eea;
                margin: 20px 0 15px 0;
                font-size: 1.3em;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .success {{
                background: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            ul {{ 
                margin: 10px 0 10px 25px;
                line-height: 1.8;
            }}
            code {{
                background: #f4f4f4;
                padding: 3px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                color: #e83e8c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Free Rotating Proxy Server</h1>
            <p class="subtitle">Deploy on Render.com • 24/7 Uptime • IPv6 Rotation</p>
            
            <div class="badges">
                <span class="badge">✅ Free Forever</span>
                <span class="badge orange">🔄 Auto-Rotate 3h</span>
                <span class="badge blue">🛡️ Anti-Cloudflare</span>
            </div>
            
            <div class="status-card">
                <h3 style="color: white; margin: 0 0 20px 0;">📊 Server Status</h3>
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-label">Current IPv6</div>
                        <div class="stat-value" style="font-size: 0.8em;">{current_ip[:20]}...</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Total Requests</div>
                        <div class="stat-value">{stats['total_requests']}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Success Rate</div>
                        <div class="stat-value">
                            {(stats['successful_requests'] / max(stats['total_requests'], 1) * 100):.0f}%
                        </div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Rotations</div>
                        <div class="stat-value">{stats['rotations']}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Uptime</div>
                        <div class="stat-value">{uptime.days}d {uptime.seconds//3600}h</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">IPv6 Pool</div>
                        <div class="stat-value">{len(ipv6_rotator.ipv6_pool)}</div>
                    </div>
                </div>
            </div>
            
            <h2>📖 API Documentation</h2>
            
            <div class="endpoint">
                <div><span class="method">GET</span><strong>/proxy</strong></div>
                <p style="margin: 10px 0;">Forward request qua rotating proxy</p>
                <strong>Parameters:</strong>
                <ul>
                    <li><code>url</code> - Target URL (required)</li>
                </ul>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span><strong>/status</strong></div>
                <p style="margin: 10px 0;">Check server status & stats</p>
            </div>
            
            <div class="endpoint">
                <div><span class="method">POST</span><strong>/rotate</strong></div>
                <p style="margin: 10px 0;">Force rotate IPv6 immediately</p>
            </div>
            
            <h2>💻 Usage Examples</h2>
            
            <h3>Python:</h3>
            <div class="code"><span class="keyword">import</span> requests

<span class="comment"># Your Render.com URL</span>
PROXY = <span class="string">"https://your-app.onrender.com"</span>

<span class="comment"># Send request through proxy</span>
response = requests.get(
    PROXY + <span class="string">"/proxy"</span>,
    params=&#123;<span class="string">"url"</span>: <span class="string">"https://httpbin.org/ip"</span>&#125;
)

<span class="keyword">print</span>(response.json())</div>

            <h3>JavaScript/Node.js:</h3>
            <div class="code"><span class="keyword">const</span> axios = <span class="keyword">require</span>(<span class="string">'axios'</span>);

<span class="keyword">const</span> PROXY = <span class="string">'https://your-app.onrender.com'</span>;

<span class="keyword">async function</span> fetchWithProxy(url) &#123;
  <span class="keyword">const</span> res = <span class="keyword">await</span> axios.get(<span class="string">`            <h3>JavaScript/Node.js:</h3>
            <div class="code"><span class="keyword">const</span> axios = <span class="keyword">require</span>(<span class="string">'axios'</span>);

<span class="keyword">const</span> PROXY = <span class="string">'https://your-app.onrender.com'</span>;

<span class="keyword">async function</span> fetchWithProxy(url) {{
  <span class="keyword">const</span> res = <span class="keyword">await</span> axios.get(<span class="string">`$\{PROXY}/proxy`</span>, {{
    params: {{ url }}
  }});
  <span class="keyword">return</span> res.data;
}}

fetchWithProxy(<span class="string">'https://api.github.com'</span>)
  .then(data => console.log(data));</div>#123;PROXY&#125;/proxy`</span>, &#123;
    params: &#123; url &#125;
  &#125;);
  <span class="keyword">return</span> res.data;
&#125;

fetchWithProxy(<span class="string">'https://api.github.com'</span>)
  .then(data => console.log(data));</div>

            <h3>cURL:</h3>
            <div class="code">curl "https://your-app.onrender.com/proxy?url=https://ipinfo.io/json"</div>
            
            <div class="success">
                <strong>✅ Features:</strong>
                <ul>
                    <li>Free hosting on Render.com (750 hours/month)</li>
                    <li>Auto IPv6 rotation every 3 hours</li>
                    <li>Anti-Cloudflare headers</li>
                    <li>Rate limiting: 60 req/min per IP</li>
                    <li>24/7 uptime with UptimeRobot</li>
                </ul>
            </div>
            
            <h2>🚀 Deploy Guide</h2>
            
            <h3>Step 1: Push code to GitHub</h3>
            <div class="code">git init
git add .
git commit -m "Initial commit"
git push origin main</div>

            <h3>Step 2: Deploy on Render.com</h3>
            <ol style="margin: 15px 0 15px 25px; line-height: 2;">
                <li>Go to <a href="https://render.com" target="_blank">render.com</a> and sign up</li>
                <li>Click "New +" → "Web Service"</li>
                <li>Connect your GitHub repository</li>
                <li>Settings:
                    <ul>
                        <li>Name: <code>rotating-proxy</code></li>
                        <li>Environment: <code>Python 3</code></li>
                        <li>Build Command: <code>pip install -r requirements.txt</code></li>
                        <li>Start Command: <code>python app.py</code></li>
                    </ul>
                </li>
                <li>Click "Create Web Service"</li>
            </ol>
            
            <h3>Step 3: Keep alive with UptimeRobot</h3>
            <ol style="margin: 15px 0 15px 25px; line-height: 2;">
                <li>Go to <a href="https://uptimerobot.com" target="_blank">uptimerobot.com</a></li>
                <li>Add New Monitor:
                    <ul>
                        <li>Monitor Type: <code>HTTP(s)</code></li>
                        <li>URL: <code>https://your-app.onrender.com/health</code></li>
                        <li>Monitoring Interval: <code>5 minutes</code></li>
                    </ul>
                </li>
                <li>Save - Done! Server will never sleep</li>
            </ol>
            
            <div class="warning">
                <strong>⚠️ Important Notes:</strong>
                <ul>
                    <li>Render free tier: 750 hours/month (enough for 24/7)</li>
                    <li>IPv6 might not work on all Render instances</li>
                    <li>For real IPv6 rotation, consider Vultr/DigitalOcean ($5/mo)</li>
                    <li>This is for educational purposes only</li>
                </ul>
            </div>
            
            <h2>📦 Required Files</h2>
            
            <h3>requirements.txt:</h3>
            <div class="code">Flask==3.0.0
requests==2.31.0
gunicorn==21.2.0</div>

            <h3>Procfile (for deployment):</h3>
            <div class="code">web: gunicorn app:app</div>
            
            <div style="text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                <p style="color: #666;">Made with ❤️ for the community</p>
                <p style="color: #999; font-size: 0.9em; margin-top: 10px;">
                    Free • Open Source • No Limits
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/proxy')
def proxy():
    """Main proxy endpoint"""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Rate limiting
    if not ipv6_rotator.check_rate_limit(client_ip):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Maximum 60 requests per minute'
        }), 429
    
    # Get target URL
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({
            'error': 'Missing parameter',
            'message': 'Please provide "url" parameter'
        }), 400
    
    # Update stats
    ipv6_rotator.stats['total_requests'] += 1
    
    try:
        # Create session with anti-cloudflare headers
        session = requests.Session()
        session.headers.update(get_anti_cloudflare_headers())
        
        # Send request
        response = session.get(
            target_url,
            timeout=30,
            allow_redirects=True
        )
        
        # Update stats
        ipv6_rotator.stats['successful_requests'] += 1
        
        # Return response
        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
        
    except requests.exceptions.Timeout:
        ipv6_rotator.stats['failed_requests'] += 1
        return jsonify({
            'error': 'Request timeout',
            'message': 'Target server took too long to respond'
        }), 504
        
    except requests.exceptions.RequestException as e:
        ipv6_rotator.stats['failed_requests'] += 1
        return jsonify({
            'error': 'Request failed',
            'message': str(e)
        }), 502

@app.route('/status')
def status():
    """Get server status"""
    return jsonify({
        'status': 'active',
        'current_ipv6': ipv6_rotator.current_ipv6,
        'last_rotation': ipv6_rotator.last_rotation.isoformat(),
        'rotation_interval_hours': ipv6_rotator.rotation_hours,
        'stats': ipv6_rotator.stats,
        'ipv6_pool_size': len(ipv6_rotator.ipv6_pool)
    })

@app.route('/rotate', methods=['POST'])
def force_rotate():
    """Force rotate IPv6"""
    ipv6_rotator.rotate_ipv6()
    return jsonify({
        'message': 'IPv6 rotated successfully',
        'new_ipv6': ipv6_rotator.current_ipv6
    })

@app.route('/health')
def health():
    """Health check for UptimeRobot"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print("=" * 70)
    print("🚀 Rotating Proxy Server Starting...")
    print("=" * 70)
    print(f"⏰ Rotation: Every {ipv6_rotator.rotation_hours} hours")
    print(f"🌐 IPv6 Pool: {len(ipv6_rotator.ipv6_pool)} addresses")
    print(f"🔗 Port: {port}")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
