# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""
import json
from pathlib import Path

# Configuration class
class Configuration:
    # constructor
    def __init__(self, file_path):
        self.file_path = Path(file_path)

        self.task_file_path = ""

    # read and parse the configuration file
    def read(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.file_path}")
        
        if self.file_path.suffix != ".json":
            raise ValueError(f"Unsupported file type: {self.file_path.suffix}")
        
        config_data = json.loads(self.file_path.read_text())

        if 'TASK_FILE_PATH' in config_data:
            self.task_file_path = config_data['TASK_FILE_PATH']
        else:
            raise ValueError("TASK_FILE_PATH attribute not found in configuration")