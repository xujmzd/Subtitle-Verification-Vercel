from http.server import BaseHTTPRequestHandler
import json
import base64
import io
from docx import Document
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.file_handler import normalize_text

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            file_name = data.get('file_name')
            file_content = data.get('file_content')  # base64 编码
            file_extension = data.get('file_extension')
            file_index = data.get('file_index', 1)
            
            # 解码 base64
            file_bytes = base64.b64decode(file_content)
            
            # 根据扩展名处理文件
            if file_extension.lower() == '.txt':
                try:
                    original_text = file_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        original_text = file_bytes.decode('gbk')
                    except UnicodeDecodeError:
                        original_text = file_bytes.decode('latin-1', errors='ignore')
            elif file_extension.lower() == '.docx':
                doc_file = io.BytesIO(file_bytes)
                doc = Document(doc_file)
                paragraphs = []
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        paragraphs.append(paragraph.text)
                original_text = '\n'.join(paragraphs)
            else:
                raise ValueError(f"不支持的文件格式: {file_extension}")
            
            # 规范化文本
            normalized_text = normalize_text(original_text)
            
            response = {
                'success': True,
                'original_text': original_text,
                'normalized_text': normalized_text,
                'file_name': file_name,
                'message': '文件加载成功'
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
                'message': f'加载文件失败: {str(e)}'
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