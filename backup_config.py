#!/usr/bin/env python3
import os
import shutil
from datetime import datetime
import logging
from pathlib import Path
import sys
import zipfile
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/Library/Logs/config_backup.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configuration
HOME = str(Path.home())
BACKUP_DIR = os.path.join(HOME, "ConfigBackups")
BACKUP_ITEMS = [
    ".bash_profile",
    ".bash_history",
    ".bash_sessions",
    ".bashrc",
    ".bash_logout",
    ".BurpSuite",
    ".CFUserTextEncoding",
    ".cups",
    ".gam",
    ".gitconfig",
    ".profile",
    ".ssh",
    ".viminfo",
    ".vscode",
    ".zprofile",
    ".zsh_history",
    ".zsh_sessions",
    ".zshrc"
]
MAX_BACKUPS = 7

def create_backup():
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create timestamp for the zip file name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = os.path.join(BACKUP_DIR, f'config_backup_{timestamp}.zip')
    
    try:
        # Create zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in BACKUP_ITEMS:
                source = os.path.join(HOME, item)
                
                if os.path.exists(source):
                    try:
                        if os.path.isdir(source):
                            # Walk through directory
                            for root, dirs, files in os.walk(source):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    # Calculate path relative to HOME
                                    arcname = os.path.relpath(file_path, HOME)
                                    try:
                                        zipf.write(file_path, arcname)
                                        logging.info(f"Added {arcname} to zip")
                                    except Exception as e:
                                        logging.error(f"Failed to add {file_path} to zip: {str(e)}")
                        else:
                            # Add single file
                            arcname = os.path.relpath(source, HOME)
                            zipf.write(source, arcname)
                            logging.info(f"Added {arcname} to zip")
                    except Exception as e:
                        logging.error(f"Failed to backup {item}: {str(e)}")
                else:
                    logging.warning(f"Source {item} does not exist, skipping")

        logging.info(f"Created backup archive: {zip_filename}")
        
        # Cleanup old backups
        cleanup_old_backups()
        
    except Exception as e:
        logging.error(f"Backup failed: {str(e)}")
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

    return True

def cleanup_old_backups():
    """Remove old backup zip files keeping only MAX_BACKUPS most recent ones"""
    try:
        backups = sorted([f for f in os.listdir(BACKUP_DIR) 
                         if f.startswith('config_backup_') and f.endswith('.zip')])
        
        if len(backups) > MAX_BACKUPS:
            for old_backup in backups[:-MAX_BACKUPS]:
                old_backup_path = os.path.join(BACKUP_DIR, old_backup)
                os.remove(old_backup_path)
                logging.info(f"Removed old backup: {old_backup}")
    except Exception as e:
        logging.error(f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    if create_backup():
        logging.info("Backup completed successfully")
    else:
        logging.error("Backup failed")