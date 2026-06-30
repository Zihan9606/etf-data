#!/usr/bin/env python3
"""
ETF数据分析 HTTP 服务器 — 支持静态文件 + 自选API
使用: python3 server.py [端口]

API端点:
  GET  /api/watchlist   → 返回 watchlist.json 内容
  POST /api/watchlist   → 写入 watchlist.json

启动后访问: http://localhost:8080/全量指数申购流入排行.html
"""
import http.server, socketserver, json, os, sys, mimetypes

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
DIR = os.path.dirname(os.path.abspath(__file__))
WATCH_FILE = os.path.join(DIR, "etf_history", "watchlist.json")

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('/api/watchlist'):
            self._serve_watchlist()
        else:
            self._serve_static()

    def do_POST(self):
        if self.path.endswith('/api/watchlist'):
            self._save_watchlist()
        else:
            self.send_error(404)

    def _serve_watchlist(self):
        data = []
        if os.path.exists(WATCH_FILE):
            try:
                with open(WATCH_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        self._json_response(data)

    def _save_watchlist(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            if not isinstance(data, list):
                raise ValueError("must be array")
            os.makedirs(os.path.dirname(WATCH_FILE), exist_ok=True)
            with open(WATCH_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._json_response({"status": "ok", "count": len(data)})
        except Exception as e:
            self._json_response({"status": "error", "msg": str(e)}, 400)

    def _serve_static(self):
        # 映射URL路径到文件系统路径
        from urllib.parse import unquote
        path = unquote(self.path.split('?')[0])  # URL解码 + 去除查询参数
        # 处理curl等工具发来的完整URL: http://host:port/path → /path
        if path.startswith('http://') or path.startswith('https://'):
            path = '/' + path.split('/', 3)[-1]
        if path == '/':
            path = '/index.html'
        elif path == '/etf':
            path = '/全量指数申购流入排行.html'
        filepath = os.path.normpath(os.path.join(DIR, path.lstrip('/')))
        if not filepath.startswith(DIR):
            self.send_error(403)
            return
        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, 'index.html')
        if os.path.exists(filepath):
            self.send_response(200)
            # 正确识别MIME类型
            content_type, _ = mimetypes.guess_type(filepath)
            if not content_type:
                if filepath.endswith('.json'):
                    content_type = 'application/json; charset=utf-8'
                elif filepath.endswith('.html'):
                    content_type = 'text/html; charset=utf-8'
                else:
                    content_type = 'application/octet-stream'
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, f"File not found: {path}")

    def _json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    # 初始化watchlist.json
    if not os.path.exists(WATCH_FILE):
        os.makedirs(os.path.dirname(WATCH_FILE), exist_ok=True)
        with open(WATCH_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

    socketserver.TCPServer.allow_reuse_address = True
    print(f"🚀 ETF分析服务器已启动")
    print(f"   地址: http://localhost:{PORT}/全量指数申购流入排行.html")
    print(f"   API: http://localhost:{PORT}/api/watchlist")
    print(f"   目录: {DIR}")
    print(f"   按 Ctrl+C 停止\n")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
