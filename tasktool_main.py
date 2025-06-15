# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

from configuration import Configuration
from task_list import TaskList

"""
Main function
"""
def main():
    # load configuration
    config = Configuration()
    config.read("config.json")
    print(config.task_file_path)

    # load task list
    task_list = TaskList()
    task_list.read(config.task_file_path)
    task_list.print()

"""
Entry point
"""
if __name__ == "__main__":
    main()