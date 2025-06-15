# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF, QLineF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from task_list import TaskList
from collections import defaultdict

class MainWindow(QMainWindow):
    """
    Main window of the application containing a QGraphicsView as central widget.
    """
    def __init__(self, task_list: TaskList):
        super().__init__()
        
        # Store task list
        self.task_list = task_list
        
        # Set window properties
        self.setWindowTitle("Task Tool")
        self.resize(800, 600)
        
        # Create graphics scene and view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        
        # Configure view
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Set view as central widget
        self.setCentralWidget(self.view)

        # Display tasks
        self.display_tasks()

    def calculate_task_positions(self, tasks):
        """
        Calculate horizontal positions for tasks based on their dependencies.
        Returns a dictionary mapping task IDs to their x-positions.
        """
        # Create task lookup dictionary
        task_dict = {task.task_id: task for task in tasks}
        
        # Initialize positions
        positions = {}
        max_positions = {}  # Track the rightmost position for each task
        
        # First pass: assign initial positions
        for task in tasks:
            if not task.depends_on_task:  # No dependencies
                positions[task.task_id] = 0
            else:
                # Find the rightmost position of all dependencies
                max_dep_pos = -1
                for dep in task.depends_on_task:
                    if dep in task_dict:  # Only consider existing dependencies
                        if dep in positions:
                            max_dep_pos = max(max_dep_pos, positions[dep])
                positions[task.task_id] = max_dep_pos + 1
        
        return positions

    def display_tasks(self):
        """
        Display tasks as rectangles with centered text, grouped by project in swim lanes.
        """
        # Clear existing items
        self.scene.clear()

        # Task box dimensions
        box_width = 200
        box_height = 100
        spacing = 50
        lane_spacing = 100  # Vertical spacing between lanes
        margin = 50  # Margin from the edges
        horizontal_spacing = 0  # Space between task boxes horizontally

        # Group tasks by project
        project_tasks = defaultdict(list)
        for task in self.task_list.tasks:
            project_tasks[task.project].append(task)

        # Calculate total height needed for each lane
        lane_heights = {}
        current_y = margin
        for project, tasks in project_tasks.items():
            # Height for project name
            height = 40
            # Height for tasks
            height += len(tasks) * (box_height + spacing)
            lane_heights[project] = height
            current_y += height + lane_spacing

        # Draw swim lanes for each project
        current_y = margin
        for project, tasks in project_tasks.items():
            # Draw project name
            project_text = QGraphicsTextItem(project)
            font = QFont()
            font.setBold(True)
            project_text.setFont(font)
            project_text.setDefaultTextColor(Qt.black)
            project_text.setPos(margin, current_y)
            self.scene.addItem(project_text)

            # Calculate horizontal positions for tasks
            positions = self.calculate_task_positions(tasks)

            # Draw tasks in this lane
            task_y = current_y + 40  # Start below project name
            max_x = margin  # Track the rightmost position in this lane
            for task in tasks:
                # Calculate horizontal position
                x_pos = margin + positions[task.task_id] * (box_width + horizontal_spacing)
                max_x = max(max_x, x_pos + box_width)

                # Create task box
                rect = self.scene.addRect(
                    x_pos, task_y, box_width, box_height,
                    QPen(Qt.black),
                    QBrush(Qt.white)
                )

                # Add task name text
                text = QGraphicsTextItem(task.task)
                text.setDefaultTextColor(Qt.black)
                
                # Center text in rectangle
                text_width = text.boundingRect().width()
                text_height = text.boundingRect().height()
                text_x = x_pos + (box_width - text_width) / 2
                text_y_pos = task_y + (box_height - text_height) / 2
                text.setPos(text_x, text_y_pos)
                
                self.scene.addItem(text)
                task_y += box_height + spacing

            # Draw horizontal separator line
            if project != list(project_tasks.keys())[-1]:  # Don't draw line after last project
                line_y = current_y + lane_heights[project] + lane_spacing/2
                line = QLineF(margin, line_y, 
                            max_x + 50, line_y)  # Line extends to the rightmost task plus padding
                self.scene.addLine(line, QPen(Qt.black, 2, Qt.DashLine))

            current_y += lane_heights[project] + lane_spacing

        # Adjust scene rect to show all items with padding
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50)) 