"""
API 工具函数
提供共享的辅助功能，如 CORS 头部设置、错误处理等
"""

from http.server import BaseHTTPRequestHandler
import json


def set_cors_headers(handler: BaseHTTPRequestHandler):
    """
    设置 CORS 响应头
    
    Args:
        handler: BaseHTTPRequestHandler 实例
    """
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    handler.send_header('Access-Control-Max-Age', '3600')


def send_json_response(handler: BaseHTTPRequestHandler, status_code: int, data: dict):
    """
    发送 JSON 响应
    
    Args:
        handler: BaseHTTPRequestHandler 实例
        status_code: HTTP 状态码
        data: 要发送的数据字典
    """
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    set_cors_headers(handler)
    handler.end_headers()
    
    # 确保中文字符正确编码
    response_json = json.dumps(data, ensure_ascii=False)
    handler.wfile.write(response_json.encode('utf-8'))


def send_error_response(handler: BaseHTTPRequestHandler, error_message: str, status_code: int = 500):
    """
    发送错误响应
    
    Args:
        handler: BaseHTTPRequestHandler 实例
        error_message: 错误消息
        status_code: HTTP 状态码，默认为 500
    """
    error_response = {
        'success': False,
        'error': error_message,
        'message': f'操作失败: {error_message}'
    }
    send_json_response(handler, status_code, error_response)


def send_success_response(handler: BaseHTTPRequestHandler, data: dict, status_code: int = 200):
    """
    发送成功响应
    
    Args:
        handler: BaseHTTPRequestHandler 实例
        data: 要发送的数据字典
        status_code: HTTP 状态码，默认为 200
    """
    response = {
        'success': True,
        **data
    }
    send_json_response(handler, status_code, response)


def handle_options_request(handler: BaseHTTPRequestHandler):
    """
    处理 OPTIONS 预检请求（用于 CORS）
    
    Args:
        handler: BaseHTTPRequestHandler 实例
    """
    handler.send_response(200)
    set_cors_headers(handler)
    handler.end_headers()


def parse_request_data(handler: BaseHTTPRequestHandler) -> dict:
    """
    解析请求数据
    
    Args:
        handler: BaseHTTPRequestHandler 实例
        
    Returns:
        解析后的 JSON 数据字典
        
    Raises:
        ValueError: 如果请求数据无效
    """
    try:
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        post_data = handler.rfile.read(content_length)
        if not post_data:
            return {}
        
        return json.loads(post_data.decode('utf-8'))
    except json.JSONDecodeError as e:
        raise ValueError(f'无效的 JSON 数据: {str(e)}')
    except Exception as e:
        raise ValueError(f'解析请求数据失败: {str(e)}')