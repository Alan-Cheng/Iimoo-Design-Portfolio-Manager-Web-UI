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