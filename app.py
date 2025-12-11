"""
图片MD5修改工具 - Web版本
"""

import os
import hashlib
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from image_md5_modifier import process_image

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400
    
    try:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        num_versions = int(request.form.get('num_versions', 3))
        if num_versions < 1 or num_versions > 100:
            num_versions = 3
        
        # 为每个上传会话创建独立的文件夹（使用UUID）
        session_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位作为会话ID
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_dir, exist_ok=True)
        
        process_image(upload_path, output_dir, num_versions)
        
        # 统计生成的文件数量
        base_name = filename.rsplit('.', 1)[0]
        file_ext = '.' + filename.rsplit('.', 1)[1] if '.' in filename else '.jpg'
        
        generated_count = 0
        for i in range(1, num_versions + 1):
            output_filename = f"{base_name}_v{i:02d}{file_ext}"
            output_path = os.path.join(output_dir, output_filename)
            if os.path.exists(output_path):
                generated_count += 1
        
        original_md5 = calculate_md5(upload_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'generated_count': generated_count,
            'total_files': num_versions,
            'session_id': session_id  # 返回会话ID
        })
    
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500


@app.route('/download_all/<session_id>')
def download_all(session_id):
    """下载指定会话的所有生成文件"""
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    if not os.path.exists(output_dir):
        return jsonify({'error': '会话不存在或已过期'}), 404
    
    # 获取所有文件
    files = []
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path):
            files.append({
                'filename': filename,
                'url': f'/download_file/{session_id}/{filename}'
            })
    
    return jsonify({
        'files': files,
        'count': len(files)
    })


@app.route('/download_file/<session_id>/<filename>')
def download_file(session_id, filename):
    """下载指定会话的单个文件"""
    directory = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    if not os.path.exists(directory):
        return jsonify({'error': '会话不存在或已过期'}), 404
    return send_from_directory(directory, filename)


if __name__ == '__main__':
    # 支持环境变量PORT（用于云端部署），默认5001
    port = int(os.environ.get('PORT', 5001))
    # 云端部署时关闭debug模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"\n服务器启动在端口 {port}")
    print(f"访问地址: http://localhost:{port}\n")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
