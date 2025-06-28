import os
import subprocess
from typing import Tuple
from dotenv import load_dotenv
import time
import random

load_dotenv()

class GitOperationsDemo:
    REPO_NAME = os.getenv('GITHUB_REPO_NAME', 'demo-repo') 
    REPO_PATH = os.path.abspath(os.path.join("resources", REPO_NAME)) 
    REPO_URL = os.getenv('GITHUB_REPO_URL', 'https://github.com/demo/demo-repo') 
    TOKEN = os.getenv('GITHUB_TOKEN', 'demo-token')

    @staticmethod
    def _simulate_delay():
        """Simulate network delay for demo purposes"""
        time.sleep(random.uniform(0.5, 2.0))

    @staticmethod
    def _run_git_command(command_args: list) -> Tuple[bool, str]:
        """Simulate git command execution for demo"""
        GitOperationsDemo._simulate_delay()
        
        # Simulate different scenarios
        command_str = ' '.join(command_args)
        
        if 'pull' in command_str:
            return True, "Already up to date with origin/main"
        elif 'push' in command_str:
            return True, "Pushed 3 commits to origin/main"
        elif 'add' in command_str:
            return True, "Added 2 files to staging area"
        elif 'commit' in command_str:
            return True, "[main abc1234] Demo commit message"
        elif 'clone' in command_str:
            return True, "Cloned repository successfully"
        else:
            return True, f"Demo: Executed {' '.join(command_args)}"

    @staticmethod
    def clone() -> Tuple[bool, str]:
        """Simulate repository cloning"""
        print("Demo: Simulating repository clone...")
        GitOperationsDemo._simulate_delay()
        
        # Create demo directory structure
        demo_dir = os.path.join("resources", "demo-portfolio")
        if not os.path.exists(demo_dir):
            os.makedirs(demo_dir)
            
        return True, f"Demo: Cloned repository to {demo_dir}"

    @staticmethod
    def pull() -> Tuple[bool, str]:
        """Simulate pulling latest changes"""
        print("Demo: Simulating git pull...")
        return GitOperationsDemo._run_git_command(['pull'])

    @staticmethod
    def add(files: str = '.') -> Tuple[bool, str]:
        """Simulate adding files to staging"""
        print(f"Demo: Simulating git add {files}...")
        return GitOperationsDemo._run_git_command(['add', files])

    @staticmethod
    def commit(message: str) -> Tuple[bool, str]:
        """Simulate committing changes"""
        print(f"Demo: Simulating git commit with message: {message}")
        return GitOperationsDemo._run_git_command(['commit', '-m', message])

    @staticmethod
    def push() -> Tuple[bool, str]:
        """Simulate pushing changes"""
        print("Demo: Simulating git push...")
        return GitOperationsDemo._run_git_command(['push'])

    @staticmethod
    def add_commit_push(commit_message: str) -> Tuple[bool, str]:
        """Simulate add, commit, and push operations"""
        print(f"Demo: Simulating add, commit, push for '{commit_message}'")
        
        # Simulate the entire workflow
        GitOperationsDemo._simulate_delay()
        
        add_success, add_msg = GitOperationsDemo.add('.')
        if not add_success:
            return False, f"Demo: Add failed - {add_msg}"
            
        commit_success, commit_msg = GitOperationsDemo.commit(commit_message)
        if not commit_success:
            return False, f"Demo: Commit failed - {commit_msg}"
            
        push_success, push_msg = GitOperationsDemo.push()
        if not push_success:
            return False, f"Demo: Push failed - {push_msg}"
            
        return True, f"Demo: Successfully completed add, commit, push for '{commit_message}'" 