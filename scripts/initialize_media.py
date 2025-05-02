import os
import argparse
from pathlib import Path

def create_directories(base_dir="uploads/media"):
    """
    Create necessary directories for media storage
    
    Args:
        base_dir: Base directory for media storage
    """
    # Make sure the base directory exists
    os.makedirs(base_dir, exist_ok=True)
    
    # Define subdirectories to create
    subdirs = [
        "health_records",
        "health_records/images",
        "health_records/videos",
        "health_records/documents",
        "pets",
        "pets/profile",
        "pets/gallery",
        "users",
        "users/profile"
    ]
    
    # Create all subdirectories
    created_dirs = []
    for subdir in subdirs:
        full_path = os.path.join(base_dir, subdir)
        os.makedirs(full_path, exist_ok=True)
        created_dirs.append(full_path)
        
        # Create a .gitkeep file in each directory to ensure they're tracked in git
        Path(os.path.join(full_path, ".gitkeep")).touch()
    
    # Print summary
    print(f"Created media storage directory: {os.path.abspath(base_dir)}")
    for directory in created_dirs:
        print(f"Created directory: {os.path.abspath(directory)}")

def set_permissions(base_dir="uploads/media"):
    """
    Set appropriate permissions for media directories
    
    Args:
        base_dir: Base directory for media storage
    """
    try:
        # Set directory permissions (755 = rwxr-xr-x)
        for root, dirs, files in os.walk(base_dir):
            os.chmod(root, 0o755)
            # Set file permissions (644 = rw-r--r--)
            for file in files:
                if file != ".gitkeep" and file != ".gitignore":
                    try:
                        os.chmod(os.path.join(root, file), 0o644)
                    except Exception as file_err:
                        print(f"Warning: Could not set permissions for {file}: {file_err}")
            
        print(f"Set permissions for {os.path.abspath(base_dir)}")
    except Exception as e:
        print(f"Error setting permissions: {e}")
        
def create_gitignore(base_dir="uploads/media"):
    """
    Create a .gitignore file to exclude media files from version control
    
    Args:
        base_dir: Base directory for media storage
    """
    gitignore_path = os.path.join(base_dir, ".gitignore")
    
    # Don't overwrite existing .gitignore
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            content = f.read()
            
        # Check if we need to append our rules
        if "# Media files" not in content:
            with open(gitignore_path, "a") as f:
                f.write("\n\n# Media files\n")
                f.write("*\n")
                f.write("!.gitkeep\n")
                f.write("!.gitignore\n")
                
            print(f"Updated .gitignore at {gitignore_path}")
    else:
        # Create new .gitignore
        with open(gitignore_path, "w") as f:
            f.write("# Media files\n")
            f.write("*\n")
            f.write("!.gitkeep\n")
            f.write("!.gitignore\n")
            
        print(f"Created .gitignore at {gitignore_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize media directories for Hanoi Pet Adoption")
    parser.add_argument("--dir", default="uploads/media", help="Base directory for media storage")
    parser.add_argument("--skip-permissions", action="store_true", help="Skip setting file permissions")
    args = parser.parse_args()
    
    create_directories(args.dir)
    
    if not args.skip_permissions:
        set_permissions(args.dir)
    else:
        print("Skipping permission settings (--skip-permissions flag used)")
        
    create_gitignore(args.dir)
    
    print("\nMedia directories initialization completed successfully!")
