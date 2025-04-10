import os
import subprocess
from typing import Tuple
from dotenv import load_dotenv

load_dotenv()

class GitOperations:
    REPO_NAME = "remote-access-test"
    REPO_PATH = os.path.join("resources", REPO_NAME)
    REPO_URL = "https://github.com/Alan-Cheng/remote-access-test.git"
    TOKEN = os.getenv('GITHUB_TOKEN')

    @staticmethod
    def clone() -> Tuple[bool, str]:
        """Clone the fixed repository with authentication"""
        try:
            auth_url = GitOperations.REPO_URL.replace(
                'https://', 
                f'https://{GitOperations.TOKEN}@'
            )
            
            result = subprocess.run(
                ['git', 'clone', auth_url, GitOperations.REPO_PATH],
                capture_output=True,
                text=True
            )
            return (True, f"Cloned to {GitOperations.REPO_PATH}") if result.returncode == 0 else (False, result.stderr)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def pull() -> Tuple[bool, str]:
        """Pull latest changes from remote"""
        try:
            # Configure git to use stored token
            subprocess.run(
                ['git', '-C', GitOperations.REPO_PATH, 'config', 'credential.helper', 'store'],
                check=True
            )
            
            with open(os.path.join(GitOperations.REPO_PATH, '.git-credentials'), 'w') as f:
                f.write(f"https://{GitOperations.TOKEN}:x-oauth-basic@github.com\n")
            
            result = subprocess.run(
                ['git', '-C', GitOperations.REPO_PATH, 'pull'],
                capture_output=True,
                text=True
            )
            return (True, "Pulled latest changes") if result.returncode == 0 else (False, result.stderr)
        except Exception as e:
            return False, str(e)
        finally:
            cred_file = os.path.join(GitOperations.REPO_PATH, '.git-credentials')
            if os.path.exists(cred_file):
                os.remove(cred_file)

    @staticmethod
    def add(files: str = '.') -> Tuple[bool, str]:
        """Add files to git staging area"""
        try:
            result = subprocess.run(
                ['git', '-C', GitOperations.REPO_PATH, 'add', files],
                capture_output=True,
                text=True
            )
            return (True, f"Added {files}") if result.returncode == 0 else (False, result.stderr)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def commit(message: str) -> Tuple[bool, str]:
        """Commit changes"""
        try:
            result = subprocess.run(
                ['git', '-C', GitOperations.REPO_PATH, 'commit', '-m', message],
                capture_output=True,
                text=True
            )
            return (True, "Changes committed") if result.returncode == 0 else (False, result.stderr)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def push() -> Tuple[bool, str]:
        """Push changes to remote repository"""
        try:
            # Configure git to use stored token
            subprocess.run(
                ['git', '-C', GitOperations.REPO_PATH, 'config', 'credential.helper', 'store'],
                check=True
            )
            
            with open(os.path.join(GitOperations.REPO_PATH, '.git-credentials'), 'w') as f:
                f.write(f"https://{GitOperations.TOKEN}:x-oauth-basic@github.com\n")
            
            result = subprocess.run(
                ['git', '-C', GitOperations.REPO_PATH, 'push'],
                capture_output=True,
                text=True
            )
            return (True, "Changes pushed") if result.returncode == 0 else (False, result.stderr)
        except Exception as e:
            return False, str(e)
        finally:
            cred_file = os.path.join(GitOperations.REPO_PATH, '.git-credentials')
            if os.path.exists(cred_file):
                os.remove(cred_file)

    @staticmethod
    def add_commit_push(commit_message: str) -> Tuple[bool, str]:
        """Adds all changes, commits with a message, and pushes to remote."""
        try:
            # 1. Add
            add_success, add_msg = GitOperations.add('.')
            if not add_success:
                return False, f"Git Add 失敗: {add_msg}"

            # 2. Commit
            commit_success, commit_msg = GitOperations.commit(commit_message)
            # Allow "nothing to commit" as a non-fatal error for commit
            if not commit_success and "nothing to commit" not in commit_msg.lower():
                 return False, f"Git Commit 失敗: {commit_msg}"
            
            # If commit reported "nothing to commit", we can skip push
            if "nothing to commit" in commit_msg.lower():
                return True, "沒有偵測到變更，無需 commit 或 push。"

            # 3. Push
            push_success, push_msg = GitOperations.push()
            # Allow "Everything up-to-date" as a non-fatal error for push
            if not push_success and "everything up-to-date" not in push_msg.lower():
                 return False, f"Git Push 失敗: {push_msg}"

            return True, f"Git 操作成功: Add='{add_msg}', Commit='{commit_msg}', Push='{push_msg}'"

        except Exception as e:
            return False, f"執行 Git 操作時發生未預期錯誤: {str(e)}"