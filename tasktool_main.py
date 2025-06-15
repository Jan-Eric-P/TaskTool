# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""
from configuration import Configuration

def main():
    # load configuration
    config = Configuration("config.json")
    config.read()
    print(config.task_file_path)
    

# entry point
if __name__ == "__main__":
    main()