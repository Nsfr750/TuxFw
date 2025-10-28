import json
import logging
import os
import sys
import tempfile
import urllib.request
from typing import Optional, Dict, Any
from packaging import version
from PySide6.QtCore import QObject, Signal, QThread, QUrl
from PySide6.QtWidgets import QMessageBox, QProgressDialog
from firewall.script.logger import get_logger

class UpdateChecker(QObject):
    """Handles checking for and applying updates"""
    
    update_available = Signal(dict)  # Emitted when an update is available
    update_progress = Signal(int)    # Emitted with download progress (0-100)
    update_complete = Signal(bool)   # Emitted when update is complete (success/failure)
    
    def __init__(self, current_version: str, update_url: str):
        """
        Initialize the update checker
        
        Args:
            current_version: Current application version (e.g., "1.0.0")
            update_url: URL to check for updates
        """
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url
        self.logger = get_logger("updater")
        
    def check_for_updates(self):
        """Check if updates are available"""
        try:
            with urllib.request.urlopen(self.update_url) as response:
                data = json.loads(response.read().decode())
                
            latest_version = data.get('version')
            if version.parse(latest_version) > version.parse(self.current_version):
                self.update_available.emit(data)
                return True
            return False
                
        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
            return False
            
    def download_update(self, update_info: Dict[str, Any], progress_callback=None):
        """Download the update package"""
        try:
            download_url = update_info.get('download_url')
            if not download_url:
                raise ValueError("No download URL provided in update info")
                
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, 'tuxfw_update.pkg')
            
            def report_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(int(block_num * block_size * 100 / total_size), 100)
                    if progress_callback:
                        progress_callback(percent)
                    self.update_progress.emit(percent)
            
            urllib.request.urlretrieve(download_url, temp_file, report_progress)
            return temp_file
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {str(e)}")
            raise
            
    def apply_update(self, update_file: str) -> bool:
        """Apply the downloaded update"""
        try:
            # TODO: Implement update application logic
            # This would typically involve:
            # 1. Verifying the update package
            # 2. Extracting files
            # 3. Replacing the current installation
            # 4. Restarting the application
            
            self.logger.info(f"Applying update from {update_file}")
            # Placeholder for actual update logic
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying update: {str(e)}")
            return False

class UpdateWorker(QThread):
    """Background worker for checking and applying updates"""
    
    def __init__(self, updater: UpdateChecker):
        super().__init__()
        self.updater = updater
        
    def run(self):
        """Run the update check in a background thread"""
        self.updater.check_for_updates()

class UpdateThread(QThread):
    """Thread for downloading updates"""
    
    def __init__(self, update_info, progress_callback):
        super().__init__()
        self.update_info = update_info
        self.progress_callback = progress_callback
        self.update_file = None
        
    def run(self):
        """Run the update download"""
        try:
            self.update_file = self.updater.download_update(
                self.update_info,
                self.progress_callback
            )
        except Exception as e:
            self.updater.logger.error(f"Error in update thread: {str(e)}")
            self.update_file = None
