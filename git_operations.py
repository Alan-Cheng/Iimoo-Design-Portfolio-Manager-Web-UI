import os
import subprocess
from typing import Tuple
from dotenv import load_dotenv

load_dotenv()

class GitOperations:
    REPO_NAME = "remote-access-test"
    # Ensure REPO_PATH uses the correct base directory if needed, assuming it's relative to project root
    REPO_PATH = os.path.abspath(os.path.join("resources", REPO_NAME)) 
    REPO_URL = os.getenv('GITHUB_REPO_URL') 
    TOKEN = os.getenv('GITHUB_TOKEN')

    @staticmethod
    def _run_git_command(command_args: list) -> Tuple[bool, str]:
        """Helper to run git commands within the repo path."""
        try:
            # Ensure repo path exists
            if not os.path.isdir(GitOperations.REPO_PATH):
                 return False, f"Repository path does not exist: {GitOperations.REPO_PATH}"

            # Base command includes setting the working directory
            base_command = ['git', '-C', GitOperations.REPO_PATH]
            full_command = base_command + command_args
            
            print(f"Running Git Command: {' '.join(full_command)}") # Debug

            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                check=False # Don't raise exception on non-zero exit code, check manually
            )

            if result.returncode == 0:
                print(f"Git command successful: {result.stdout}") # Debug
                return True, result.stdout
            else:
                # Handle specific non-zero cases like 'nothing to commit'
                if "nothing to commit" in result.stdout or "nothing added to commit" in result.stdout:
                     print(f"Git command info: {result.stdout}") # Debug
                     return True, result.stdout # Treat as success
                elif "up-to-date" in result.stdout:
                     print(f"Git command info: {result.stdout}") # Debug
                     return True, result.stdout # Treat pull/push up-to-date as success

                print(f"Git command failed (Code {result.returncode}): {result.stderr}") # Debug
                return False, result.stderr

        except FileNotFoundError:
             return False, "Git command not found. Is Git installed and in PATH?"
        except Exception as e:
            print(f"Error running git command {' '.join(command_args)}: {e}") # Debug
            return False, str(e)

    @staticmethod
    def clone() -> Tuple[bool, str]:
        """Clone the fixed repository with authentication"""
        # Clone needs to happen *outside* the repo path initially
        target_parent_dir = os.path.dirname(GitOperations.REPO_PATH) # e.g., 'resources'
        target_repo_name = os.path.basename(GitOperations.REPO_PATH) # e.g., 'remote-access-test'
        
        if os.path.exists(GitOperations.REPO_PATH):
            return True, f"Repository already exists at {GitOperations.REPO_PATH}"
            
        try:
            auth_url = GitOperations.REPO_URL.replace('https://', f'https://{GitOperations.TOKEN}@')
            
            result = subprocess.run(
                ['git', 'clone', auth_url, target_repo_name], # Clone into parent dir
                cwd=target_parent_dir, # Set working directory for clone
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return True, f"Cloned to {GitOperations.REPO_PATH}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)

    @staticmethod
    def pull() -> Tuple[bool, str]:
        """Pull latest changes from remote"""
        # Pull needs authentication setup
        success, _ = GitOperations._configure_credentials()
        if not success:
            return False, "Failed to configure credentials for pull"
        
        pull_success, message = GitOperations._run_git_command(['pull'])
        GitOperations._remove_credentials() # Clean up credentials
        return pull_success, message

    @staticmethod
    def add(files: str = '.') -> Tuple[bool, str]:
        """Add files to git staging area"""
        return GitOperations._run_git_command(['add', files])

    @staticmethod
    def commit(message: str) -> Tuple[bool, str]:
        """Commit changes"""
        # Configure user identity if not set globally (important for commit)
        GitOperations._run_git_command(['config', 'user.email', '"action@automaton.bot"'])
        GitOperations._run_git_command(['config', 'user.name', '"Automated Action"'])
        
        return GitOperations._run_git_command(['commit', '-m', message])

    @staticmethod
    def push() -> Tuple[bool, str]:
        """Push changes to remote repository"""
        # Push needs authentication setup
        success, _ = GitOperations._configure_credentials()
        if not success:
            return False, "Failed to configure credentials for push"
            
        push_success, message = GitOperations._run_git_command(['push'])
        GitOperations._remove_credentials() # Clean up credentials
        return push_success, message

    @staticmethod
    def _configure_credentials() -> Tuple[bool, str]:
        """Configure temporary credential helper for auth."""
        if not GitOperations.TOKEN:
            return False, "GitHub token not found in environment variables."
        
        # Use credential helper store
        success, msg = GitOperations._run_git_command(['config', 'credential.helper', 'store'])
        if not success:
             return False, f"Failed to set credential.helper: {msg}"

        # Write credentials to a temporary file within .git (safer)
        # Note: This is still not perfectly secure, but better than plain text in repo root
        # Ideally, use platform-specific credential managers or SSH keys
        git_dir = os.path.join(GitOperations.REPO_PATH, '.git')
        cred_path = os.path.join(git_dir, '.git-credentials-temp') # Store inside .git
        try:
            with open(cred_path, 'w') as f:
                f.write(f"https://{GitOperations.TOKEN}:x-oauth-basic@github.com\n")
            # Tell git to use this specific file
            success_cred, msg_cred = GitOperations._run_git_command(['config', 'credential.helper', f'store --file={cred_path}'])
            if not success_cred:
                 os.remove(cred_path) # Clean up if config fails
                 return False, f"Failed to configure credential store file: {msg_cred}"
            return True, "Credentials configured."
        except Exception as e:
             print(f"Error writing credential file: {e}")
             if os.path.exists(cred_path): os.remove(cred_path)
             return False, f"Error writing credential file: {e}"


    @staticmethod
    def _remove_credentials():
        """Remove temporary credential file and unset helper config."""
        git_dir = os.path.join(GitOperations.REPO_PATH, '.git')
        cred_path = os.path.join(git_dir, '.git-credentials-temp')
        if os.path.exists(cred_path):
            try:
                os.remove(cred_path)
            except OSError as e:
                 print(f"Error removing credential file {cred_path}: {e}")
        # Unset the specific file helper, revert to default (or whatever was before)
        GitOperations._run_git_command(['config', '--unset', 'credential.helper'])


    @staticmethod
    def add_commit_push(commit_message: str) -> Tuple[bool, str]:
        """Adds all changes, commits, and pushes."""
        print(f"--- Starting Add, Commit, Push: '{commit_message}' ---")
        
        # 1. Add all changes
        add_success, add_msg = GitOperations.add('.')
        if not add_success:
            # If add fails significantly (not just 'nothing added'), report error
            if "nothing added to commit" not in add_msg: 
                 print("Add failed.")
                 return False, f"Git add failed: {add_msg}"
            print("Nothing new to add.")
            # If nothing to add, maybe nothing to commit/push either? Or maybe just commit?
            # Let's proceed to commit, it will handle 'nothing to commit'.

        # 2. Commit
        commit_success, commit_msg = GitOperations.commit(commit_message)
        if not commit_success:
             # If commit fails significantly (not just 'nothing to commit'), report error
             if "nothing to commit" not in commit_msg:
                 print("Commit failed.")
                 return False, f"Git commit failed: {commit_msg}"
             print("Nothing to commit.")
             # If nothing to commit, no need to push
             return True, "No changes detected to commit or push."

        # 3. Push
        push_success, push_msg = GitOperations.push()
        if not push_success:
            print("Push failed.")
            return False, f"Git push failed: {push_msg}"

        print("--- Add, Commit, Push successful ---")
        return True, f"Successfully pushed changes: {commit_message}"