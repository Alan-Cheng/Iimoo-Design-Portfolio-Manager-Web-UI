from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from git_operations_demo import GitOperationsDemo 
from portfolio_manager_demo import PortfolioManagerDemo
from dotenv import load_dotenv
import os
import threading 
from functools import wraps

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'demo-secret-key')

# Debug: Print loaded environment variables
print("=== Demo Environment Variables ===")
print(f"PORT: {os.environ.get('PORT', '5000')}")
print(f"GITHUB_TOKEN: {'Demo Mode - No Real Token'}")
print(f"GITHUB_REPO_URL: {'Demo Mode - No Real Repo'}")
print(f"GITHUB_REPO_NAME: {'Demo Mode - No Real Repo'}")
print(f"ADMIN_PASSWORD: {'demo123'}")
print("============================")

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Login Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        admin_password = 'demo123'  # 直接寫死密碼
        
        # Debug: Print password comparison
        print(f"Demo: Login attempt - Input: '{password}', Expected: '{admin_password}'")
        print(f"Demo: Password match: {password == admin_password}")
        
        if password == admin_password:
            session['logged_in'] = True
            print("Demo: Login successful")
            return redirect(url_for('index'))
        else:
            print("Demo: Login failed")
            return render_template('login_demo.html', error='密碼錯誤 (Demo: 使用 demo123)')
    
    return render_template('login_demo.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/demo-info')
def demo_info():
    return """
    <h1>Demo Mode 說明</h1>
    <p>這是一個演示版本，不會實際操作 GitHub 倉庫。</p>
    <ul>
        <li>所有 Git 操作都是模擬的</li>
        <li>作品集資料會保存在本地 demo 資料夾</li>
        <li>上傳的圖片會創建為演示檔案</li>
        <li>登入密碼: demo123</li>
    </ul>
    <a href="/">返回主頁</a>
    """

# --- Helper for Background Git Push (Demo) ---
def run_git_push(commit_message):
    """Runs add, commit, push in a background thread (Demo mode)."""
    print(f"Demo: Background task started: Simulating push for '{commit_message}'")
    
    success, message = GitOperationsDemo.add_commit_push(commit_message)
    if success:
        print(f"Demo: Background task finished: Successfully simulated push '{commit_message}'. Message: {message}")
    else:
        print(f"Demo: Background task finished: Failed to simulate push '{commit_message}'. Error: {message}")

# --- Static File Route ---
@app.route('/assets/<path:filename>')
def serve_static(filename):
    return send_from_directory(
        os.path.join(PortfolioManagerDemo.BASE_DIR, 'assets'), 
        filename
    )

# --- Demo Image Route ---
@app.route('/assets/img/portfolio/<folder_name>/<filename>')
def serve_portfolio_image(folder_name, filename):
    """Serve portfolio images for demo mode"""
    try:
        image_path = os.path.join(PortfolioManagerDemo.PORTFOLIO_DIR, folder_name, filename)
        if os.path.exists(image_path):
            return send_from_directory(
                os.path.join(PortfolioManagerDemo.PORTFOLIO_DIR, folder_name),
                filename
            )
        else:
            # Return a placeholder image or 404
            return "Demo image not found", 404
    except Exception as e:
        print(f"Demo: Error serving image {filename} from {folder_name}: {e}")
        return "Demo image error", 500

# --- Page Routes ---
@app.route('/')
@login_required
def index():
    # Simulate pulling latest changes
    print("Demo: Simulating pull latest changes...")
    pull_success, pull_msg = GitOperationsDemo.pull()
    if pull_success:
        print(f"Demo: Successfully simulated pull: {pull_msg}")
    else:
        print(f"Demo: Simulated pull failed: {pull_msg}")
    
    return render_template('portfolio.html')

@app.route('/git')
@login_required
def git_operations():
    return render_template('index.html')

# --- Portfolio API Routes ---
@app.route('/api/portfolio', methods=['GET'])
@login_required
def get_portfolio():
    try:
        items = PortfolioManagerDemo.get_portfolio_items()
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/portfolio/upload', methods=['POST'])
@login_required
def upload_portfolio():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

@app.route('/api/portfolio/update', methods=['POST']) 
@login_required
def update_portfolio():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

@app.route('/api/portfolio/delete', methods=['POST'])
@login_required
def delete_portfolio():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

# --- Git API Routes (Demo) ---
@app.route('/api/git/clone', methods=['POST'])
@login_required
def git_clone():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

@app.route('/api/git/pull', methods=['POST'])
@login_required
def git_pull():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

@app.route('/api/git/add', methods=['POST'])
@login_required
def git_add():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

@app.route('/api/git/commit', methods=['POST'])
@login_required
def git_commit():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

@app.route('/api/git/push', methods=['POST'])
@login_required
def git_push():
    return jsonify({'success': False, 'message': 'Demo: 此功能在演示模式中不可操作'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Demo: Starting demo server on port {port}")
    print("Demo: Login with password: demo123")
    app.run(host='0.0.0.0', port=port, debug=True) 