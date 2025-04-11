from flask import Flask, render_template, request, jsonify, send_from_directory
from git_operations import GitOperations # Import GitOperations
from portfolio_manager import PortfolioManager
from dotenv import load_dotenv
import os
import threading # To run git push in background

load_dotenv()
app = Flask(__name__)

# --- Helper for Background Git Push ---
def run_git_push(commit_message):
    """Runs add, commit, push in a background thread."""
    print(f"Background task started: Pushing changes for '{commit_message}'")
    # Ensure the repo exists before trying to push
    if not os.path.exists(GitOperations.REPO_PATH):
        print("Repository not found locally, skipping push.")
        # Optionally clone it first? Or just rely on initial setup?
        # For now, just skip if not cloned.
        # clone_success, clone_msg = GitOperations.clone()
        # if not clone_success:
        #     print(f"Failed to clone repo before push: {clone_msg}")
        #     return
        return

    # Pull first to avoid conflicts (optional, but recommended)
    pull_success, pull_msg = GitOperations.pull()
    if not pull_success:
        print(f"Pull before push failed: {pull_msg}. Attempting push anyway...")
        # Decide if you want to stop or continue if pull fails

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
def index():
    # Ensure repo is cloned on first load if not present
    if not os.path.exists(GitOperations.REPO_PATH):
        print("Repository not found locally, attempting to clone...")
        clone_success, clone_msg = GitOperations.clone()
        if not clone_success:
            print(f"Initial clone failed: {clone_msg}")
            # Maybe render an error page or message?
    return render_template('portfolio.html')

@app.route('/git')
def git_operations():
     # Ensure repo is cloned if accessing git page
    if not os.path.exists(GitOperations.REPO_PATH):
        print("Repository not found locally, attempting to clone...")
        clone_success, clone_msg = GitOperations.clone()
        if not clone_success:
            print(f"Initial clone failed: {clone_msg}")
    return render_template('index.html')

# --- Portfolio API Routes ---
@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        items = PortfolioManager.get_portfolio_items()
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/portfolio/upload', methods=['POST'])
def upload_portfolio():
    if 'images' not in request.files:
        return jsonify({'success': False, 'message': '缺少圖片檔案'})
    uploaded_files = request.files.getlist('images') 
    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
         return jsonify({'success': False, 'message': '沒有選擇任何檔案'})
    valid_files = [f for f in uploaded_files if f and f.filename.lower().endswith('.jpg')]
    if not valid_files:
         return jsonify({'success': False, 'message': '上傳的檔案中沒有有效的JPG圖片'})
    description_data = {
        "project_name": request.form.get("project_name", ""),
        "description": request.form.get("description", ""),
        "area": request.form.get("area", ""),
        "date": request.form.get("date", ""),
        "size": request.form.get("size", ""),
        "type": request.form.get("type", "")
    }
    
    # Call manager function
    success, message = PortfolioManager.create_new_portfolio(valid_files, description_data)
    
    # If successful, trigger background git push
    if success:
        commit_message = f"Add portfolio: {description_data.get('project_name', 'New Portfolio')}"
        thread = threading.Thread(target=run_git_push, args=(commit_message,))
        thread.start()
        message += " (正在背景同步到 GitHub...)" # Inform user

    return jsonify({'success': success, 'message': message})

@app.route('/api/portfolio/update', methods=['POST']) 
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
        valid_files = [f for f in uploaded_files if f and f.filename != '' and f.filename.lower().endswith('.jpg')]
        if valid_files: 
            images_replaced = True
            print(f"Replacing images for {folder_name}...")
            image_replace_success, image_replace_message = PortfolioManager.replace_portfolio_images(folder_name, valid_files)
            if not image_replace_success:
                 print(f"Image replacement failed for {folder_name}: {image_replace_message}")
        else:
            print(f"No valid new image files provided for replacement in {folder_name}.")

    # Always attempt to update description
    desc_update_success, desc_update_message = PortfolioManager.update_description_entry(folder_name, update_data)

    final_success = desc_update_success # Success primarily depends on description update
    final_message = desc_update_message
    if image_replace_message: 
        final_message += f" 图片替换状态: {image_replace_message}"

    # If description update OR image replacement succeeded, trigger push
    if desc_update_success or (images_replaced and image_replace_success):
         commit_message = f"Update portfolio: {folder_name} ({update_data.get('project_name', '')})"
         thread = threading.Thread(target=run_git_push, args=(commit_message,))
         thread.start()
         final_message += " (正在背景同步到 GitHub...)"

    return jsonify({'success': final_success, 'message': final_message})


@app.route('/api/portfolio/delete', methods=['POST'])
def delete_portfolio():
    data = request.json
    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({'success': False, 'message': '缺少作品集資料夾名稱'})
        
    # Call manager function
    success, message = PortfolioManager.delete_portfolio(folder_name)

    # If successful, trigger background git push
    if success:
        commit_message = f"Delete portfolio: {folder_name}"
        thread = threading.Thread(target=run_git_push, args=(commit_message,))
        thread.start()
        message += " (正在背景同步到 GitHub...)" # Inform user

    return jsonify({'success': success, 'message': message})

# --- Git Operations API (Manual Controls) ---
# These remain for manual triggering if needed
@app.route('/api/git/clone', methods=['POST'])
def git_clone_manual():
    try:
        success, message = GitOperations.clone()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/pull', methods=['POST'])
def git_pull_manual():
    try:
        success, message = GitOperations.pull()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/add', methods=['POST'])
def git_add_manual():
    data = request.json
    files = data.get('files', '.')
    try:
        success, message = GitOperations.add(files)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/commit', methods=['POST'])
def git_commit_manual():
    data = request.json
    message = data.get('message', '')
    try:
        success, message = GitOperations.commit(message)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/git/push', methods=['POST'])
def git_push_manual():
    try:
        success, message = GitOperations.push()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# --- Main Execution ---
if __name__ == '__main__':
    # Ensure repo is cloned on startup
    if not os.path.exists(GitOperations.REPO_PATH):
        print("Repository not found locally on startup, attempting to clone...")
        clone_success, clone_msg = GitOperations.clone()
        if not clone_success:
            print(f"Initial clone failed: {clone_msg}")
        else:
             print(f"Initial clone successful.")
             
    app.run(debug=True)