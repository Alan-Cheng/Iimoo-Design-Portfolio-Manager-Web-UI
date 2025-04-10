from flask import Flask, render_template, request, jsonify, send_from_directory
from git_operations import GitOperations
from portfolio_manager import PortfolioManager
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

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
    return render_template('portfolio.html')

@app.route('/git')
def git_operations():
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
    success, message_or_folder = PortfolioManager.create_new_portfolio(valid_files, description_data)
    if success:
        folder_name = message_or_folder # On success, create_new_portfolio returns the folder name
        commit_message = f"新增作品集: {folder_name}"
        git_success, git_message = GitOperations.add_commit_push(commit_message)
        if not git_success:
            # Log the Git error but still return success for the portfolio creation
            print(f"警告: 作品集 '{folder_name}' 已成功建立，但 Git 操作失敗: {git_message}")
            message = f"{message_or_folder} (Git 操作失敗: {git_message})" # Append warning
        else:
             message = f"{message_or_folder} (Git 操作成功)"
    else:
        message = message_or_folder # On failure, it returns the error message

    return jsonify({'success': success, 'message': message})

@app.route('/api/portfolio/update', methods=['POST']) # Using POST for simplicity
def update_portfolio():
    data = request.json
    folder_name = data.get('folder_name')
    update_data = data.get('update_data')

    if not folder_name or not update_data:
        return jsonify({'success': False, 'message': '缺少必要參數 (folder_name 或 update_data)'})
        
    success, message = PortfolioManager.update_description_entry(folder_name, update_data)
    if success:
        commit_message = f"更新作品集描述: {folder_name}"
        git_success, git_message = GitOperations.add_commit_push(commit_message)
        if not git_success:
            print(f"警告: 作品集 '{folder_name}' 描述已成功更新，但 Git 操作失敗: {git_message}")
            message = f"{message} (Git 操作失敗: {git_message})"
        else:
            message = f"{message} (Git 操作成功)"

    return jsonify({'success': success, 'message': message})


@app.route('/api/portfolio/delete', methods=['POST'])
def delete_portfolio():
    data = request.json
    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({'success': False, 'message': '缺少作品集資料夾名稱'})
    # Store the folder name before deletion for the commit message
    deleted_folder_name = folder_name
    success, message = PortfolioManager.delete_portfolio(folder_name)
    if success:
        commit_message = f"刪除作品集: {deleted_folder_name}"
        git_success, git_message = GitOperations.add_commit_push(commit_message)
        if not git_success:
             print(f"警告: 作品集 '{deleted_folder_name}' 已成功刪除，但 Git 操作失敗: {git_message}")
             message = f"{message} (Git 操作失敗: {git_message})"
        else:
             message = f"{message} (Git 操作成功)"

    return jsonify({'success': success, 'message': message})

# --- Git Operations API ---
# ... (Git API routes remain the same) ...
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

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True)