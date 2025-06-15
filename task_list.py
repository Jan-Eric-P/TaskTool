# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

import csv
from pathlib import Path
from typing import List

# Task class
class Task:
    def __init__(self, task_id: str, project: str, task: str, time_required: str,
                 time_spent: str, other_departments: List[str], depends_on_task):
        self.task_id = task_id
        self.project = project
        self.task = task
        self.time_required = time_required
        self.time_spent = time_spent
        self.other_departments = other_departments
        self.depends_on_task = depends_on_task

# TaskList class
class TaskList:
    """
    Constructor
    """
    def __init__(self):
        self.file_path = None

        self.tasks: List[Task] = []

    """
    Read a CSV file with semicolon separator and store the data as Task objects.
    
    Args:
        file_path (str): Path to the CSV file
    """
    def read(self, file_path: str) -> None:

        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Task file not found: {file_path}")
        
        if self.file_path.suffix != ".csv":
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        with open(self.file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            # Verify required columns exist
            required_columns = ['TaskId', 'Project', 'Task', 'TimeRequired', 
                              'TimeSpent', 'OtherDepartments', 'DependsOnTask']
            
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            # Clear existing data
            self.tasks = []

            # Read and process each row
            for row in reader:
                # Handle multiple values in OtherDepartments
                other_depts = row['OtherDepartments'].strip()
                other_departments = other_depts.split() if other_depts else []
                
                # Handle multiple values in DependsOnTask
                depends_on = row['DependsOnTask'].strip()
                depends_on_task = depends_on.split() if depends_on else []
                
                # Create Task object
                task = Task(
                    task_id=row['TaskId'],
                    project=row['Project'],
                    task=row['Task'],
                    time_required=row['TimeRequired'],
                    time_spent=row['TimeSpent'],
                    other_departments=other_departments,
                    depends_on_task=depends_on_task                )
                self.tasks.append(task) 

    """	
    Print all tasks in a formatted table on the command line.
    """
    def print(self) -> None:
        """
        Print all tasks in a formatted table on the command line.
        """
        if not self.tasks:
            print("No tasks available.")
            return

        # Define column widths
        col_widths = {
            'TaskId': 5,
            'Project': 12,
            'Task': 20,
            'TimeRequired': 12,
            'TimeSpent': 10,
            'OtherDepartments': 15,
            'DependsOnTask': 12
        }

        # Print header
        header = (
            f"{'TaskId':<{col_widths['TaskId']}} | "
            f"{'Project':<{col_widths['Project']}} | "
            f"{'Task':<{col_widths['Task']}} | "
            f"{'TimeRequired':<{col_widths['TimeRequired']}} | "
            f"{'TimeSpent':<{col_widths['TimeSpent']}} | "
            f"{'OtherDepts':<{col_widths['OtherDepartments']}} | "
            f"{'DependsOn':<{col_widths['DependsOnTask']}}"
        )
        print(header)
        print("-" * len(header))

        # Print each task
        for task in self.tasks:
            # Format lists as comma-separated strings
            other_depts = " ".join(task.other_departments) if task.other_departments else "-"
            depends_on = " ".join(task.depends_on_task) if task.depends_on_task else "-"

            # Print task row
            print(
                f"{task.task_id:<{col_widths['TaskId']}} | "
                f"{task.project:<{col_widths['Project']}} | "
                f"{task.task:<{col_widths['Task']}} | "
                f"{task.time_required:<{col_widths['TimeRequired']}} | "
                f"{task.time_spent:<{col_widths['TimeSpent']}} | "
                f"{other_depts:<{col_widths['OtherDepartments']}} | "
                f"{depends_on:<{col_widths['DependsOnTask']}}"
            ) 