"""Git utilities for Conventional Commits automation."""

import subprocess
import os
from typing import List, Optional
from pathlib import Path
from backend.config import GIT_USER_NAME, GIT_USER_EMAIL, GITHUB_TOKEN, GIT_REPO_URL, WORLD_JSON_PATH, NEWS_JSON_PATH, DIRECTION_JSON_PATH


def _find_repo_root() -> Path:
    """Resolve repo root (directory containing .git) from this file's location."""
    path = Path(__file__).resolve().parent
    while path != path.parent:
        if (path / ".git").exists():
            return path
        path = path.parent
    return Path(".").resolve()


class GitUtils:
    """Handles git operations with Conventional Commits."""
    
    def __init__(self):
        self.repo_path = _find_repo_root()
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
        if any("world.json" in f or "news.json" in f or "direction.json" in f for f in changed_files):
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
        elif "direction.json" in str(changed_files):
            scope = "direction"
        elif any("entities" in f for f in changed_files):
            scope = "entities"
        elif any("physics" in f for f in changed_files):
            scope = "physics"
        
        # Generate description
        if "world.json" in str(changed_files):
            desc = "update world state"
        elif "news.json" in str(changed_files):
            desc = "update news feed"
        elif "direction.json" in str(changed_files):
            desc = "update PM direction"
        elif len(changed_files) == 1:
            desc = f"update {Path(changed_files[0]).stem}"
        else:
            desc = f"update {len(changed_files)} files"
        
        if scope:
            return f"{commit_type}({scope}): {desc}"
        else:
            return f"{commit_type}: {desc}"
    
    def _get_allowed_files(self, changed_files: List[str]) -> List[str]:
        """Filter changed files to only include allowed files."""
        allowed_patterns = [
            "backend/data/world.json",
            "backend/data/news.json",
            "backend/data/direction.json",
            "backend/data/history/",
            "backend/",
        ]
        
        # Critical files that should never be deleted
        critical_files = [
            "Dockerfile",
            "docker-compose.yml",
            "README.md",
            ".gitignore",
            ".github/",
            "docs/",
            "scripts/",
            "package.json",
            "pyproject.toml",
            "poetry.lock",
        ]
        
        repo_path = Path(self.repo_path)
        allowed = []
        for original_path in changed_files:
            file_path = original_path.strip()
            if file_path.startswith("./"):
                file_path = file_path[2:]
            # Normalize absolute paths to relative (e.g. Docker: /app/backend/data/world.json -> backend/data/world.json)
            try:
                p = Path(file_path)
                if p.is_absolute() and str(p).startswith(str(repo_path)):
                    file_path = str(p.relative_to(repo_path))
            except (ValueError, TypeError):
                pass

            if "__pycache__" in file_path or file_path.endswith(".pyc"):
                continue

            is_allowed = False
            for pattern in allowed_patterns:
                if file_path.startswith(pattern):
                    is_allowed = True
                    break

            is_critical_deletion = False
            for critical in critical_files:
                if file_path.startswith(critical):
                    is_critical_deletion = True
                    break

            if is_allowed:
                allowed.append(original_path)
            elif is_critical_deletion:
                print(f"Warning: Critical file {original_path} detected in changes, skipping")

        return allowed
    
    def _check_critical_file_deletions(
        self, deleted_paths: List[str], staged_paths: List[str]
    ) -> tuple[bool, str]:
        """Block only if we are actually staging a deletion of a critical file.
        In Docker, many paths show as deleted (not mounted); we only stage allowed_files,
        so we must not block unless a critical path is in both deleted_paths and staged_paths."""
        critical_files = [
            "Dockerfile",
            "docker-compose.yml",
            "README.md",
            ".gitignore",
            ".github/workflows/",
            "docs/",
            "scripts/",
            "package.json",
            "pyproject.toml",
        ]
        staged_set = set(staged_paths)
        for file_path in deleted_paths:
            if file_path not in staged_set:
                continue
            for critical in critical_files:
                if file_path.startswith(critical):
                    return False, f"Blocked: Attempt to delete critical file {file_path}"
        return True, ""
    
    def commit_changes(self, message: Optional[str] = None) -> tuple[bool, str]:
        """Commit changes following Conventional Commits."""
        # Configure git
        self._configure_git()
        
        # Get changed files (respecting .gitignore)
        success, output = self._run_git(["status", "--porcelain", "--ignored"])
        if not success:
            return False, f"Failed to get git status: {output}"
        
        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
        changed_files = []
        deleted_paths = []
        
        for line in lines:
            # Parse git status output: XY filename (or " Y path" after strip when leading space)
            # X = index status, Y = working tree status; path starts after first 2 chars
            if len(line) < 3:
                continue
            
            status = line[:2]
            file_path = line[2:].strip()
            
            # Skip ignored files (!!)
            if status == "!!":
                continue
            
            # Only track modifications, additions, and deletions of tracked files
            if status[0] in ['M', 'A', 'D'] or status[1] in ['M', 'A', 'D']:
                changed_files.append(file_path)
                if status[0] == 'D' or status[1] == 'D':
                    deleted_paths.append(file_path)
        
        if not changed_files:
            return False, "No changes to commit"
        
        # Filter to only allowed files (we only ever stage these)
        allowed_files = self._get_allowed_files(changed_files)
        
        # Block only if we would stage a deletion of a critical file (e.g. in Docker we do not stage Dockerfile)
        check_ok, check_msg = self._check_critical_file_deletions(deleted_paths, allowed_files)
        if not check_ok:
            return False, check_msg
        
        if not allowed_files:
            sample = ", ".join(changed_files[:5])
            if len(changed_files) > 5:
                sample += ", ..."
            return False, f"No allowed files to commit (all changes are in ignored or critical files). Changed: [{sample}]"
        
        # Stage only allowed files (respecting .gitignore)
        for file_path in allowed_files:
            # Use git add with --ignore-errors to skip files that don't exist
            success, output = self._run_git(["add", "--ignore-errors", file_path])
            if not success:
                print(f"Warning: Failed to stage {file_path}: {output}")
        
        # Generate commit message if not provided
        if not message:
            commit_type = self._determine_commit_type(allowed_files)
            message = self._generate_commit_message(commit_type, allowed_files)
        
        # Commit
        success, output = self._run_git(["commit", "-m", message])
        if not success:
            return False, f"Failed to commit: {output}"
        
        return True, f"Committed: {message}"
    
    def push_changes(self) -> tuple[bool, str]:
        """Push changes to remote repository. Uses SSH by default; uses HTTPS with GITHUB_TOKEN if set."""
        # If GITHUB_TOKEN is set, use HTTPS remote so push can authenticate
        if GITHUB_TOKEN and GIT_REPO_URL.startswith("git@"):
            # git@github.com:user/repo.git -> https://github.com/user/repo
            parts = GIT_REPO_URL.replace("git@github.com:", "").replace(".git", "")
            self._run_git(
                ["remote", "set-url", "origin", f"https://x-access-token:{GITHUB_TOKEN}@github.com/{parts}.git"]
            )
        success, output = self._run_git(["push", "origin", "main"])
        if not success:
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
