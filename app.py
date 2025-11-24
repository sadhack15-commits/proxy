"""
Simple Fast Public Proxy Server
- Forward requests qua proxy
- Full browser fingerprinting
- Anti-detection
- Siêu mượt, không lag
"""

from flask import Flask, request, Response, jsonify
import requests
import os
import random
from datetime import datetime

app = Flask(__name__)

# Perfect browser fingerprints
BROWSER_FINGERPRINTS = [
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "cache-control": "max-age=0"
    },
    {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "cache-control": "max-age=0"
    },
    {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "cache-control": "max-age=0"
    },
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
        "te": "trailers"
    },
    {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "upgrade-insecure-requests": "1",
        "cache-control": "max-age=0"
    }
]

# Stats with more details
stats = {
    'total_requests': 0,
    'successful': 0,
    'failed': 0,
    'bandwidth_used': 0,
    'avg_response_time': 0,
    'start_time': datetime.now().isoformat()
}

# Response time tracking
response_times = []

def get_random_headers():
    """Lấy headers ngẫu nhiên"""
    fingerprint = random.choice(BROWSER_FINGERPRINTS).copy()
    
    # Chuẩn hóa headers
    headers = {}
    for key, value in fingerprint.items():
        proper_key = '-'.join(word.capitalize() for word in key.split('-'))
        headers[proper_key] = value
    
    headers['Connection'] = 'keep-alive'
    headers['Dnt'] = '1'
    
    return headers

@app.route('/')
def home():
    """Trang chủ hiển thị proxy info"""
    uptime = datetime.now() - datetime.fromisoformat(stats['start_time'])
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Public Proxy Server</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Courier New', monospace;
                background: #0a0a0a;
                color: #00ff00;
                padding: 40px 20px;
                line-height: 1.6;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: #1a1a1a;
                border: 2px solid #00ff00;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 0 30px rgba(0, 255, 0, 0.2);
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-align: center;
                text-shadow: 0 0 10px #00ff00;
            }
            .subtitle {
                text-align: center;
                color: #00cc00;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .section {
                background: #0f0f0f;
                border: 1px solid #00ff00;
                border-radius: 5px;
                padding: 20px;
                margin: 20px 0;
            }
            .section h2 {
                color: #00ff00;
                margin-bottom: 15px;
                font-size: 1.5em;
            }
            .proxy-url {
                background: #000;
                padding: 15px;
                border: 1px solid #00ff00;
                border-radius: 5px;
                font-size: 1.2em;
                word-break: break-all;
                color: #00ff00;
                text-align: center;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .stat-box {
                background: #000;
                border: 1px solid #00ff00;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
            }
            .stat-label {
                color: #00cc00;
                font-size: 0.9em;
                margin-bottom: 5px;
            }
            .stat-value {
                font-size: 1.8em;
                font-weight: bold;
            }
            .code {
                background: #000;
                border: 1px solid #00ff00;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                overflow-x: auto;
                font-size: 0.95em;
            }
            .example {
                margin: 10px 0;
                padding: 10px;
                background: #0a0a0a;
                border-left: 3px solid #00ff00;
            }
            .badge {
                display: inline-block;
                background: #00ff00;
                color: #000;
                padding: 3px 10px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 0.8em;
                margin-left: 10px;
            }
            a { color: #00ff00; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .blink {
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ PUBLIC PROXY SERVER</h1>
            <p class="subtitle">Fast • Anonymous • No Limits <span class="blink">●</span></p>
            
            <div class="section">
                <h2>📡 PROXY URL</h2>
                <div class="proxy-url">
                    https://proxy-g7kt.onrender.com
                </div>
            </div>
            
            <div class="section">
                <h2>📊 STATS</h2>
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-label">TOTAL REQUESTS</div>
                        <div class="stat-value">""" + str(stats['total_requests']) + """</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">SUCCESS</div>
                        <div class="stat-value">""" + str(stats['successful']) + """</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">FAILED</div>
                        <div class="stat-value">""" + str(stats['failed']) + """</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">UPTIME</div>
                        <div class="stat-value">""" + str(uptime.days) + """d """ + str(uptime.seconds//3600) + """h</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">BANDWIDTH</div>
                        <div class="stat-value">""" + str(round(stats['bandwidth_used']/1024/1024, 2)) + """MB</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">AVG SPEED</div>
                        <div class="stat-value">""" + str(round(stats['avg_response_time'], 2)) + """s</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>💻 USAGE</h2>
                
                <div class="example">
                    <strong>Python:</strong>
                    <div class="code">import requests

proxies = {
    'http': 'https://proxy-g7kt.onrender.com',
    'https': 'https://proxy-g7kt.onrender.com'
}

response = requests.get('https://google.com', proxies=proxies)
print(response.text)</div>
                </div>
                
                <div class="example">
                    <strong>cURL:</strong>
                    <div class="code">curl -x https://proxy-g7kt.onrender.com https://google.com</div>
                </div>
                
                <div class="example">
                    <strong>Browser Extension:</strong>
                    <div class="code">Proxy: proxy-g7kt.onrender.com
Port: 443
Type: HTTPS</div>
                </div>
            </div>
            
            <div class="section">
                <h2>✨ FEATURES</h2>
                <div style="padding: 10px 0;">
                    ✓ Fake browser fingerprinting <span class="badge">ANTI-DETECT</span><br>
                    ✓ Random User-Agent rotation<br>
                    ✓ Full headers spoofing<br>
                    ✓ HTTPS support<br>
                    ✓ No rate limiting<br>
                    ✓ 24/7 uptime<br>
                    ✓ Free forever
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 ENDPOINTS</h2>
                <div class="example">
                    <strong>GET /proxy</strong><br>
                    Forward any HTTP/HTTPS request<br>
                    <div class="code">?url=https://example.com</div>
                </div>
                <div class="example">
                    <strong>GET /status</strong><br>
                    Check proxy status & stats
                </div>
                <div class="example">
                    <strong>GET /health</strong><br>
                    Health check endpoint
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #00ff00;">
                <p>Powered by Render.com • Made with 💚</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/proxy')
def proxy():
    """Main proxy endpoint"""
    import time
    start_time = time.time()
    
    target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({'error': 'Missing url parameter'}), 400
    
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    stats['total_requests'] += 1
    
    try:
        # Create session với random headers
        session = requests.Session()
        headers = get_random_headers()
        session.headers.update(headers)
        
        # Forward request method
        method = request.method
        
        # Get request data
        data = request.get_data()
        params = dict(request.args)
        params.pop('url', None)  # Remove proxy param
        
        # Forward request
        response = session.request(
            method=method,
            url=target_url,
            data=data if data else None,
            params=params if params else None,
            timeout=30,
            allow_redirects=True,
            stream=True
        )
        
        # Calculate response time
        elapsed = time.time() - start_time
        response_times.append(elapsed)
        if len(response_times) > 100:
            response_times.pop(0)
        stats['avg_response_time'] = sum(response_times) / len(response_times)
        
        stats['successful'] += 1
        stats['bandwidth_used'] += len(response.content)
        
        # Return response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = {
            key: value for key, value in response.headers.items()
            if key.lower() not in excluded_headers
        }
        
        return Response(
            response.content,
            status=response.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.Timeout:
        stats['failed'] += 1
        return jsonify({'error': 'Request timeout'}), 504
        
    except requests.exceptions.RequestException as e:
        stats['failed'] += 1
        return jsonify({'error': str(e)}), 502
        
    except Exception as e:
        stats['failed'] += 1
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Status endpoint"""
    uptime = datetime.now() - datetime.fromisoformat(stats['start_time'])
    
    return jsonify({
        'status': 'active',
        'proxy_url': 'https://proxy-g7kt.onrender.com',
        'stats': {
            'total_requests': stats['total_requests'],
            'successful': stats['successful'],
            'failed': stats['failed'],
            'success_rate': f"{(stats['successful'] / max(stats['total_requests'], 1) * 100):.2f}%",
            'bandwidth_mb': round(stats['bandwidth_used'] / 1024 / 1024, 2),
            'avg_response_time': round(stats['avg_response_time'], 3)
        },
        'uptime': {
            'days': uptime.days,
            'hours': uptime.seconds // 3600,
            'total_hours': round(uptime.total_seconds() / 3600, 2)
        },
        'fingerprints': len(BROWSER_FINGERPRINTS),
        'features': [
            'Browser fingerprinting',
            'Random User-Agent',
            'Anti-detection',
            'HTTPS support',
            'No rate limiting'
        ]
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print("=" * 70)
    print("⚡ PUBLIC PROXY SERVER")
    print("=" * 70)
    print(f"🔗 Port: {port}")
    print(f"🎭 Fingerprints: {len(BROWSER_FINGERPRINTS)}")
    print("🚀 Status: ONLINE")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
