# scripts/show_structure.py

from pathlib import Path
import sys

def print_tree(directory: Path, prefix: str = "", is_last: bool = True):
    """Print directory tree structure."""
    # Print current directory/file
    print(prefix + ("└── " if is_last else "├── ") + directory.name)

    if directory.is_dir():
        items = list(directory.iterdir())
        # Filter out hidden files/folders, __pycache__, and PNG files
        items = [item for item in items if not (item.name.startswith(('.', '__pycache__')) or item.name.endswith('.png'))]
        items.sort(key=lambda x: (x.is_file(), x.name))

        # Print all items
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            print_tree(item, prefix + ("    " if is_last else "│   "), is_last_item)

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    print(f"\nProject structure for: {project_root.name}")
    print_tree(project_root)