#!/usr/bin/env python3
"""
Project Cleanup and Organization Script
Cleans redundant files and organizes project structure
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Main cleanup function"""
    print("🧹 Starting MT5-MatchTrader Project Cleanup")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # Remove __pycache__ directories
    print("🗑️  Removing __pycache__ directories...")
    for pycache in project_root.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            print(f"   Removed: {pycache}")
    
    # Remove .pyc files
    print("🗑️  Removing .pyc files...")
    for pyc_file in project_root.rglob("*.pyc"):
        pyc_file.unlink()
        print(f"   Removed: {pyc_file}")
    
    # Archive backup_old_files if it exists
    backup_dir = project_root / "backup_old_files"
    if backup_dir.exists():
        print("📦 Archiving backup_old_files...")
        archive_dir = project_root / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        shutil.move(str(backup_dir), str(archive_dir / "backup_old_files"))
        print(f"   Moved to: {archive_dir / 'backup_old_files'}")
    
    # Organize research files
    research_dir = project_root / "research_and_debug"
    if research_dir.exists():
        print("📁 Organizing research files...")
        dev_dir = project_root / "development"
        dev_dir.mkdir(exist_ok=True)
        
        shutil.move(str(research_dir), str(dev_dir / "research_and_debug"))
        print(f"   Moved to: {dev_dir / 'research_and_debug'}")
    
    # Create proper directory structure
    print("📁 Creating organized directory structure...")
    directories = [
        "logs",
        "data",
        "config",
        "tests",
        "docs",
        "development",
        "archive"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    # Move configuration files to config directory
    config_dir = project_root / "config"
    config_files = [
        "config_mvp.json",
        "config_mvp.sample.json", 
        "config_mvp.private.json"
    ]
    
    for config_file in config_files:
        source = project_root / config_file
        if source.exists():
            destination = config_dir / config_file
            if not destination.exists():
                shutil.move(str(source), str(destination))
                print(f"   Moved: {config_file} → config/{config_file}")
    
    print("\n✅ Project cleanup completed!")
    print("\n📋 Project Structure:")
    print("├── src/                 # Core application code")
    print("├── tests/               # Test suites")  
    print("├── config/              # Configuration files")
    print("├── logs/                # Application logs")
    print("├── data/                # Data files")
    print("├── docs/                # Documentation")
    print("├── development/         # Development files")
    print("├── archive/             # Archived old files")
    print("└── requirements.txt     # Dependencies")

if __name__ == "__main__":
    cleanup_project()
