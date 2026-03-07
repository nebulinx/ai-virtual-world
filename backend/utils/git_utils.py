"""Git utilities for Conventional Commits automation."""

import subprocess
import os
from typing import List, Optional
from pathlib import Path
from backend.config import GIT_USER_NAME, GIT_USER_EMAIL, GITHUB_TOKEN, GIT_REPO_URL, WORLD_JSON_PATH, NEWS_JSON_PATH


class GitUtils:
    """Handles git operations with Conventional Commits."""
    
    def __init__(self):
        self.repo_path = Path(".")
        self.git_user_name = GIT_USER_NAME
        self.git_user_email = GIT_USER_EMAIL
    
    def _run_git(self, args: List[str]) -> tuple[bool, str]:
        """Run git command."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def _configure_git(self) -> bool:
        """Configure git user name and email."""
        success1, _ = self._run_git(["config", "user.name", self.git_user_name])
        success2, _ = self._run_git(["config", "user.email", self.git_user_email])
        return success1 and success2
    
    def _determine_commit_type(self, changed_files: List[str]) -> str:
        """Determine commit type based on changed files."""
        # Check for new features
        if any("entities.py" in f or "physics.py" in f for f in changed_files):
            return "feat"
        # Check for fixes
        if any("fix" in f.lower() or "bug" in f.lower() for f in changed_files):
            return "fix"
        # Check for refactoring
        if any("refactor" in f.lower() for f in changed_files):
            return "refactor"
        # Check for documentation
        if any("README" in f or "docs" in f.lower() for f in changed_files):
            return "docs"
        # World state updates
        if any("world.json" in f or "news.json" in f for f in changed_files):
            return "chore"
        return "chore"
    
    def _generate_commit_message(self, commit_type: str, changed_files: List[str]) -> str:
        """Generate Conventional Commits message."""
        scope = None
        
        # Determine scope
        if "world.json" in str(changed_files):
            scope = "world"
        elif "news.json" in str(changed_files):
            scope = "news"
        elif any("entities" in f for f in changed_files):
            scope = "entities"
        elif any("physics" in f for f in changed_files):
            scope = "physics"
        
        # Generate description
        if "world.json" in str(changed_files):
            desc = "update world state"
        elif "news.json" in str(changed_files):
            desc = "update news feed"
        elif len(changed_files) == 1:
            desc = f"update {Path(changed_files[0]).stem}"
        else:
            desc = f"update {len(changed_files)} files"
        
        if scope:
            return f"{commit_type}({scope}): {desc}"
        else:
            return f"{commit_type}: {desc}"
    
    def commit_changes(self, message: Optional[str] = None) -> tuple[bool, str]:
        """Commit changes following Conventional Commits."""
        # Configure git
        self._configure_git()
        
        # Get changed files
        success, output = self._run_git(["status", "--porcelain"])
        if not success:
            return False, f"Failed to get git status: {output}"
        
        changed_files = [line.split()[-1] for line in output.strip().split('\n') if line.strip()]
        
        if not changed_files:
            return False, "No changes to commit"
        
        # Stage files
        success, output = self._run_git(["add", "."])
        if not success:
            return False, f"Failed to stage files: {output}"
        
        # Generate commit message if not provided
        if not message:
            commit_type = self._determine_commit_type(changed_files)
            message = self._generate_commit_message(commit_type, changed_files)
        
        # Commit
        success, output = self._run_git(["commit", "-m", message])
        if not success:
            return False, f"Failed to commit: {output}"
        
        return True, f"Committed: {message}"
    
    def push_changes(self) -> tuple[bool, str]:
        """Push changes to remote repository."""
        success, output = self._run_git(["push", "origin", "main"])
        if not success:
            # Try to set upstream if needed
            self._run_git(["push", "-u", "origin", "main"])
            success, output = self._run_git(["push", "origin", "main"])
        return success, output
    
    def commit_and_push(self, message: Optional[str] = None) -> tuple[bool, str]:
        """Commit and push changes."""
        success, msg = self.commit_changes(message)
        if not success:
            return False, msg
        
        success, output = self.push_changes()
        if not success:
            return False, f"Committed but failed to push: {output}"
        
        return True, "Changes committed and pushed successfully"
