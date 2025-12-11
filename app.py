"""
图片MD5修改工具 - Web版本
"""

import os
import hashlib
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import zipfile
import tempfile
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
        
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], filename.rsplit('.', 1)[0])
        os.makedirs(output_dir, exist_ok=True)
        
        process_image(upload_path, output_dir, num_versions)
        
        output_files = []
        base_name = filename.rsplit('.', 1)[0]
        file_ext = '.' + filename.rsplit('.', 1)[1] if '.' in filename else '.jpg'
        
        for i in range(1, num_versions + 1):
            output_filename = f"{base_name}_v{i:02d}{file_ext}"
            output_path = os.path.join(output_dir, output_filename)
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                file_md5 = calculate_md5(output_path)
                output_files.append({
                    'filename': output_filename,
                    'size': file_size,
                    'md5': file_md5,
                    'url': f'/download/{base_name}/{output_filename}'
                })
        
        original_md5 = calculate_md5(upload_path)
        
        return jsonify({
            'success': True,
            'original_md5': original_md5,
            'output_files': output_files,
            'output_dir': base_name,
            'zip_url': f'/download_zip/{base_name}'
        })
    
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500


@app.route('/download/<path:dirname>/<filename>')
def download_file(dirname, filename):
    directory = os.path.join(app.config['OUTPUT_FOLDER'], dirname)
    return send_from_directory(directory, filename)


@app.route('/download_zip/<path:dirname>')
def download_zip(dirname):
    directory = os.path.join(app.config['OUTPUT_FOLDER'], dirname)
    if not os.path.exists(directory):
        return jsonify({'error': '目录不存在'}), 404
    
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    try:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, directory)
                    zipf.write(file_path, arcname)
        
        return send_file(
            temp_zip.name,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{dirname}_images.zip'
        )
    finally:
        if os.path.exists(temp_zip.name):
            os.unlink(temp_zip.name)


if __name__ == '__main__':
    # 支持环境变量PORT（用于云端部署），默认5001
    port = int(os.environ.get('PORT', 5001))
    # 云端部署时关闭debug模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"\n服务器启动在端口 {port}")
    print(f"访问地址: http://localhost:{port}\n")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
