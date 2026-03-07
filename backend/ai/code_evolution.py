"""Utilities for autonomous code modification."""

import ast
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
import tempfile


class CodeEvolution:
    """Handles safe code modification with validation."""
    
    def __init__(self, backup_dir: str = "backend/data/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, file_path: str) -> str:
        """Create backup of file before modification."""
        source = Path(file_path)
        if not source.exists():
            return ""
        
        timestamp = source.stat().st_mtime
        backup_path = self.backup_dir / f"{source.name}.backup_{int(timestamp)}"
        shutil.copy2(source, backup_path)
        return str(backup_path)
    
    def validate_syntax(self, code: str) -> tuple[bool, Optional[str]]:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def validate_imports(self, code: str) -> tuple[bool, List[str]]:
        """Check if imports in code are valid."""
        try:
            tree = ast.parse(code)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Basic validation - check if imports look reasonable
            invalid = []
            for imp in imports:
                # Check for obviously invalid imports
                if imp.startswith('..') or imp.count('.') > 3:
                    invalid.append(imp)
            
            return len(invalid) == 0, invalid
        except SyntaxError:
            return False, ["Syntax error prevents import validation"]
    
    def inject_code(
        self,
        file_path: str,
        code: str,
        location: str = "end",
        target_class: Optional[str] = None,
        target_function: Optional[str] = None
    ) -> tuple[bool, str]:
        """Inject code into a file at specified location."""
        # Create backup
        backup_path = self.create_backup(file_path)
        if not backup_path:
            return False, "Failed to create backup"
        
        # Validate syntax
        is_valid, error = self.validate_syntax(code)
        if not is_valid:
            return False, f"Syntax error: {error}"
        
        # Validate imports
        imports_valid, invalid_imports = self.validate_imports(code)
        if not imports_valid:
            return False, f"Invalid imports: {invalid_imports}"
        
        try:
            # Read existing file
            source = Path(file_path)
            if not source.exists():
                # Create new file
                source.parent.mkdir(parents=True, exist_ok=True)
                with open(source, 'w') as f:
                    f.write(code)
                return True, "File created"
            
            existing_code = source.read_text()
            
            # Parse AST
            tree = ast.parse(existing_code)
            
            if location == "end":
                # Append at end of file
                new_code = existing_code + "\n\n" + code
            elif location == "beginning":
                # Prepend at beginning
                new_code = code + "\n\n" + existing_code
            elif target_class:
                # Insert into class
                new_code = self._inject_into_class(existing_code, code, target_class)
            elif target_function:
                # Insert into function
                new_code = self._inject_into_function(existing_code, code, target_function)
            else:
                new_code = existing_code + "\n\n" + code
            
            # Validate final code
            is_valid, error = self.validate_syntax(new_code)
            if not is_valid:
                # Restore backup
                shutil.copy2(backup_path, file_path)
                return False, f"Final code validation failed: {error}"
            
            # Write new code
            source.write_text(new_code)
            return True, "Code injected successfully"
        
        except Exception as e:
            # Restore backup on error
            if backup_path and Path(backup_path).exists():
                shutil.copy2(backup_path, file_path)
            return False, f"Error: {str(e)}"
    
    def _inject_into_class(self, existing_code: str, new_code: str, class_name: str) -> str:
        """Inject code into a specific class."""
        lines = existing_code.split('\n')
        in_target_class = False
        indent_level = 0
        insert_index = -1
        
        for i, line in enumerate(lines):
            if f"class {class_name}" in line:
                in_target_class = True
                indent_level = len(line) - len(line.lstrip())
            elif in_target_class:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level + 4
                if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                    insert_index = i
                    break
        
        if insert_index == -1:
            insert_index = len(lines)
        
        # Insert code with proper indentation
        indented_code = '\n'.join(
            ' ' * (indent_level + 4) + line if line.strip() else line
            for line in new_code.split('\n')
        )
        lines.insert(insert_index, indented_code)
        return '\n'.join(lines)
    
    def _inject_into_function(self, existing_code: str, new_code: str, function_name: str) -> str:
        """Inject code into a specific function."""
        lines = existing_code.split('\n')
        in_target_function = False
        indent_level = 0
        insert_index = -1
        
        for i, line in enumerate(lines):
            if f"def {function_name}" in line:
                in_target_function = True
                indent_level = len(line) - len(line.lstrip())
            elif in_target_function:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level + 4
                if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                    insert_index = i
                    break
        
        if insert_index == -1:
            insert_index = len(lines)
        
        # Insert code with proper indentation
        indented_code = '\n'.join(
            ' ' * (indent_level + 4) + line if line.strip() else line
            for line in new_code.split('\n')
        )
        lines.insert(insert_index, indented_code)
        return '\n'.join(lines)
    
    def rollback(self, file_path: str, backup_path: str) -> bool:
        """Rollback file to backup."""
        try:
            source = Path(file_path)
            backup = Path(backup_path)
            
            if backup.exists():
                shutil.copy2(backup, source)
                return True
            return False
        except Exception:
            return False
