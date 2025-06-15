# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

from configuration import Configuration
from task_list import TaskList
from main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

"""
Main function
"""
def main():
    # Create application
    app = QApplication(sys.argv)

    # load configuration
    config = Configuration()
    config.read("config.json")
    print(config.task_file_path)

    # load task list
    task_list = TaskList()
    task_list.read(config.task_file_path)
    task_list.print()

    # create main window
    main_window = MainWindow()
    main_window.show()

    # Start event loop
    sys.exit(app.exec_())


"""
Entry point
"""
if __name__ == "__main__":
    main()