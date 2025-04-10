from flask import Flask, render_template, request, jsonify, send_from_directory
from git_operations import GitOperations
from portfolio_manager import PortfolioManager
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# 設定靜態檔案路由
@app.route('/assets/<path:filename>')
def serve_static(filename):
    return send_from_directory(
        os.path.join('resources', 'remote-access-test', 'assets'),
        filename
    )

@app.route('/')
def index():
    return render_template('portfolio.html')

@app.route('/git')
def git_operations():
    return render_template('index.html')

@app.route('/api/portfolio/upload', methods=['POST'])
def upload_portfolio():
    if 'images' not in request.files:
        return jsonify({'success': False, 'message': '沒有上傳檔案'})
    
    files = request.files.getlist('images')
    images_data = []
    
    for file in files:
        if file and file.filename.lower().endswith('.jpg'):
            images_data.append(file.read())
        else:
            # 如果有非JPG檔案，可以選擇忽略或返回錯誤
            print(f"忽略非JPG檔案: {file.filename}")
            # return jsonify({'success': False, 'message': f'只允許上傳JPG檔案，發現: {file.filename}'})
    
    if not images_data:
        return jsonify({'success': False, 'message': '沒有有效的JPG圖片上傳'})
    
    success, message = PortfolioManager.create_new_portfolio(images_data)
    return jsonify({'success': success, 'message': message})

@app.route('/api/git/clone', methods=['POST'])
def git_clone():
    try:
        success, message = GitOperations.clone()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/pull', methods=['POST'])
def git_pull():
    try:
        success, message = GitOperations.pull()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/add', methods=['POST'])
def git_add():
    data = request.json
    files = data.get('files', '.')
    
    try:
        success, message = GitOperations.add(files)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/commit', methods=['POST'])
def git_commit():
    data = request.json
    message = data.get('message', '')
    
    try:
        success, message = GitOperations.commit(message)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/push', methods=['POST'])
def git_push():
    try:
        success, message = GitOperations.push()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        items = PortfolioManager.get_portfolio_items()
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)