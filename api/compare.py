from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.text_compare import compare_texts, TextDiff

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text1 = data.get('text1', '')
            text2 = data.get('text2', '')
            
            if not text1 or not text2:
                response = {
                    'success': False,
                    'error': '请提供两个文本内容',
                    'message': '需要两个文本才能进行比对'
                }
            else:
                # 比较文本
                diffs1, diffs2 = compare_texts(text1, text2)
                
                # 转换为字典列表
                diffs1_dict = [diff.to_dict() for diff in diffs1]
                diffs2_dict = [diff.to_dict() for diff in diffs2]
                
                response = {
                    'success': True,
                    'diffs1': diffs1_dict,
                    'diffs2': diffs2_dict,
                    'message': '比对完成'
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e),
                'message': f'比对失败: {str(e)}'
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
