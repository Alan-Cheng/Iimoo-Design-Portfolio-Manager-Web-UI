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