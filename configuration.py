# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

import json
from pathlib import Path

# Configuration class
class Configuration:
    """
    Constructor
    """
    def __init__(self):
        self.file_path = None
        
        self.task_file_path = ""

    """
    Read a JSON file with configuration data and store the content.
    
    Args:
        file_path (str): Path to the config file
    """
    def read(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.file_path}")
        
        if self.file_path.suffix != ".json":
            raise ValueError(f"Unsupported file type: {self.file_path.suffix}")
        
        config_data = json.loads(self.file_path.read_text())

        if 'TASK_FILE_PATH' in config_data:
            self.task_file_path = config_data['TASK_FILE_PATH']
        else:
            raise ValueError("TASK_FILE_PATH attribute not found in configuration")