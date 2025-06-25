from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from git_operations import GitOperations 
from portfolio_manager import PortfolioManager
from dotenv import load_dotenv
import os
import threading 
from functools import wraps

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Debug: Print loaded environment variables
print("=== Environment Variables ===")
print(f"PORT: {os.environ.get('PORT', 'Not set')}")
print(f"GITHUB_TOKEN: {'Set' if os.environ.get('GITHUB_TOKEN') else 'Not set'}")
print(f"GITHUB_REPO_URL: {os.environ.get('GITHUB_REPO_URL', 'Not set')}")
print(f"GITHUB_REPO_NAME: {os.environ.get('GITHUB_REPO_NAME', 'Not set')}")
print(f"ADMIN_PASSWORD: {'Set' if os.environ.get('ADMIN_PASSWORD') else 'Not set'}")
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
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not admin_password:
            return render_template('login.html', error='管理員密碼未設定')
        
        if password == admin_password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='密碼錯誤')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- Helper for Background Git Push ---
def run_git_push(commit_message):
    """Runs add, commit, push in a background thread."""
    print(f"Background task started: Pushing changes for '{commit_message}'")
    if not os.path.exists(GitOperations.REPO_PATH):
        print("Repository not found locally, skipping push.")
        return

    pull_success, pull_msg = GitOperations.pull()
    if not pull_success:
        print(f"Pull before push failed: {pull_msg}. Attempting push anyway...")

    success, message = GitOperations.add_commit_push(commit_message)
    if success:
        print(f"Background task finished: Successfully pushed '{commit_message}'. Message: {message}")
    else:
        print(f"Background task finished: Failed to push '{commit_message}'. Error: {message}")

# --- Static File Route ---
@app.route('/assets/<path:filename>')
def serve_static(filename):
    return send_from_directory(
        os.path.join(PortfolioManager.BASE_DIR, 'assets'), 
        filename
    )

# --- Page Routes ---
@app.route('/')
@login_required
def index():
    # Pull latest changes before loading the page
    print("Pulling latest changes from GitHub...")
    pull_success, pull_msg = GitOperations.pull()
    if pull_success:
        print(f"Successfully pulled latest changes: {pull_msg}")
    else:
        print(f"Pull failed: {pull_msg}")
    
    if not os.path.exists(GitOperations.REPO_PATH):
        print("Repository not found locally, attempting to clone...")
        clone_success, clone_msg = GitOperations.clone()
        if not clone_success:
            print(f"Initial clone failed: {clone_msg}")
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
        items = PortfolioManager.get_portfolio_items()
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/portfolio/upload', methods=['POST'])
@login_required
def upload_portfolio():
    if 'images' not in request.files:
        return jsonify({'success': False, 'message': '缺少圖片檔案'})
    uploaded_files = request.files.getlist('images') 
    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
         return jsonify({'success': False, 'message': '沒有選擇任何檔案'})
    valid_files = [f for f in uploaded_files if f and (f.filename.lower().endswith('.jpg') or f.filename.lower().endswith('.webp'))]
    if not valid_files:
         return jsonify({'success': False, 'message': '上傳的檔案中沒有有效的JPG或WebP圖片'})
    description_data = {
        "project_name": request.form.get("project_name", ""),
        "description": request.form.get("description", ""),
        "area": request.form.get("area", ""),
        "date": request.form.get("date", ""),
        "size": request.form.get("size", ""),
        "type": request.form.get("type", "")
    }
    
    success, message = PortfolioManager.create_new_portfolio(valid_files, description_data)
    
    if success:
        commit_message = f"Add portfolio: {description_data.get('project_name', 'New Portfolio')}"
        thread = threading.Thread(target=run_git_push, args=(commit_message,))
        thread.start()
        message += " (正在背景上傳到 GitHub...)" 

    return jsonify({'success': success, 'message': message})

@app.route('/api/portfolio/update', methods=['POST']) 
@login_required
def update_portfolio():
    folder_name = request.form.get('folder_name')
    if not folder_name:
        return jsonify({'success': False, 'message': '缺少作品集資料夾名稱 (folder_name)'})
    update_data = {
        "project_name": request.form.get("project_name", ""),
        "description": request.form.get("description", ""),
        "area": request.form.get("area", ""),
        "date": request.form.get("date", ""),
        "size": request.form.get("size", ""),
        "type": request.form.get("type", "")
    }

    image_replace_success = True
    image_replace_message = ""
    images_replaced = False
    
    if 'images' in request.files:
        uploaded_files = request.files.getlist('images')
        valid_files = [f for f in uploaded_files if f and f.filename != '' and (f.filename.lower().endswith('.jpg') or f.filename.lower().endswith('.webp'))]
        if valid_files: 
            images_replaced = True
            print(f"Replacing images for {folder_name}...")
            image_replace_success, image_replace_message = PortfolioManager.replace_portfolio_images(folder_name, valid_files)
            if not image_replace_success:
                 print(f"Image replacement failed for {folder_name}: {image_replace_message}")
        else:
            print(f"No valid new image files provided for replacement in {folder_name}.")

    desc_update_success, desc_update_message = PortfolioManager.update_description_entry(folder_name, update_data)

    final_success = desc_update_success 
    final_message = desc_update_message
    if image_replace_message: 
        final_message += f" 圖片替換狀態: {image_replace_message}"

    if desc_update_success or (images_replaced and image_replace_success):
         commit_message = f"Update portfolio: {folder_name} ({update_data.get('project_name', '')})"
         thread = threading.Thread(target=run_git_push, args=(commit_message,))
         thread.start()
         final_message += " (正在背景上傳到 GitHub...)"

    return jsonify({'success': final_success, 'message': final_message})


@app.route('/api/portfolio/delete', methods=['POST'])
@login_required
def delete_portfolio():
    data = request.json
    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({'success': False, 'message': '缺少作品集資料夾名稱'})
        
    success, message = PortfolioManager.delete_portfolio(folder_name)

    if success:
        commit_message = f"Delete portfolio: {folder_name}"
        thread = threading.Thread(target=run_git_push, args=(commit_message,))
        thread.start()
        message += " (正在背景上傳到 GitHub...)" 

    return jsonify({'success': success, 'message': message})

# --- Git API Routes ---
@app.route('/api/git/clone', methods=['POST'])
@login_required
def git_clone():
    try:
        success, message = GitOperations.clone()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/pull', methods=['POST'])
@login_required
def git_pull():
    try:
        success, message = GitOperations.pull()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/add', methods=['POST'])
@login_required
def git_add():
    try:
        data = request.json
        files = data.get('files', '.')
        success, message = GitOperations.add(files)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/commit', methods=['POST'])
@login_required
def git_commit():
    try:
        data = request.json
        message = data.get('message', '')
        if not message:
            return jsonify({'success': False, 'message': '請輸入 commit 訊息'})
        success, message = GitOperations.commit(message)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/push', methods=['POST'])
@login_required
def git_push():
    try:
        success, message = GitOperations.push()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists(GitOperations.REPO_PATH):
        print("Repository not found locally on startup, attempting to clone...")
        clone_success, clone_msg = GitOperations.clone()
        if not clone_success:
            print(f"Initial clone failed: {clone_msg}")
        else:
             print(f"Initial clone successful.")
             
    # Bind to 0.0.0.0 to be accessible from outside the container
    # Use os.environ.get('PORT', 5000) for flexibility if needed later
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False) # Disable debug mode in Docker