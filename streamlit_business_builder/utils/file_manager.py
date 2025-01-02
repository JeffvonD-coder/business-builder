import os
from datetime import datetime
import re

class FileManager:
    def __init__(self):
        # Create base directories if they don't exist
        self.base_dir = "generated_files"
        self.create_directories()

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.base_dir,
            os.path.join(self.base_dir, "txt"),
            os.path.join(self.base_dir, "pdf")
        ]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def generate_filename(self, username, extension):
        """Generate filename with username and timestamp"""
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create simple filename
        filename = f"{username}_{timestamp}.{extension}"
        
        # Determine full path based on extension
        if extension == "txt":
            full_path = os.path.join(self.base_dir, "txt", filename)
        else:
            full_path = os.path.join(self.base_dir, "pdf", filename)
            
        return full_path 