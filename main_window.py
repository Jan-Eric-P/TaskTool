# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QToolBar, QAction, QStyle
from PyQt5.QtCore import Qt, QRectF, QLineF, QSize
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTextOption, QIcon, QPixmap
from task_list import TaskList
from collections import defaultdict
import resources_rc
import os

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

        # Create toolbar
        self.create_toolbar()

        # Display tasks
        self.display_tasks()

    """
    Create toolbar with zoom controls.
    """
    def create_toolbar(self):
        toolbar = QToolBar("Zoom Controls")
        self.addToolBar(toolbar)

        # Zoom in action
        zoom_in_action = QAction(QIcon(":/icons/zoom_in_24dp.png"), "Zoom In", self)
        zoom_in_action.setStatusTip("Zoom in")
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        # Zoom out action
        zoom_out_action = QAction(QIcon(":/icons/zoom_out_24dp.png"), "Zoom Out", self)
        zoom_out_action.setStatusTip("Zoom out")
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        # Reset zoom action
        reset_zoom_action = QAction(QIcon(":/icons/view_real_size_24dp.png"), "Reset Zoom", self)
        reset_zoom_action.setStatusTip("Reset zoom level")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        toolbar.addAction(reset_zoom_action)

    """
    Zoom in by scaling the view.
    """
    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    """
    Zoom out by scaling the view.
    """
    def zoom_out(self):
        self.view.scale(1/1.2, 1/1.2)

    """
    Reset zoom level to 1.0.
    """
    def reset_zoom(self):
        self.view.resetTransform()

    """
    Calculate horizontal positions for tasks based on their dependencies.
    Tasks without dependencies are placed at position 0, while tasks with dependencies
    are positioned to the right of their most rightward dependency.

    Args:
        tasks: List of Task objects to position

    Returns:
        Dictionary mapping task IDs to their x-positions
    """
    def calculate_task_positions(self, tasks):
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

    """
    Create and add time information items to the scene.
    Displays 'Required' time in black and 'Spent' time in green (if within limit) or red (if exceeded).

    Args:
        task: Task object containing time information
        x_pos: X-coordinate for positioning
        y_pos: Y-coordinate for positioning
        box_width: Width of the task box
        text_padding: Padding for text within the box

    Returns:
        Height of the time information section
    """
    def create_time_info(self, task, x_pos, y_pos, box_width, text_padding):
        # Create time required text
        time_required = QGraphicsTextItem(f"Required: {task.time_required}")
        time_required.setDefaultTextColor(Qt.black)
        time_required.setPos(x_pos + text_padding, y_pos + text_padding)
        self.scene.addItem(time_required)

        # Create time spent text
        time_spent = QGraphicsTextItem(f"Spent: {task.time_spent}")
        try:
            if int(task.time_spent) > int(task.time_required):
                time_spent.setDefaultTextColor(Qt.red)
            else:
                time_spent.setDefaultTextColor(QColor(0, 100, 0))  # Dark green
        except ValueError:
            time_spent.setDefaultTextColor(Qt.black)  # Fallback to black if conversion fails
        
        time_spent_width = time_spent.boundingRect().width()
        time_spent_x = x_pos + box_width - time_spent_width - text_padding
        time_spent.setPos(time_spent_x, y_pos + text_padding)
        self.scene.addItem(time_spent)

        return max(time_required.boundingRect().height(), time_spent.boundingRect().height())

    """
    Create and add task text item to the scene.
    Displays the task name with department abbreviations in parentheses if available.

    Args:
        task: Task object containing task information
        x_pos: X-coordinate for positioning
        y_pos: Y-coordinate for positioning
        box_width: Width of the task box
        text_padding: Padding for text within the box

    Returns:
        Height of the task text
    """
    def create_task_text(self, task, x_pos, y_pos, box_width, text_padding):
        task_text = task.task
        if task.other_departments:
            task_text += f" ({', '.join(task.other_departments)})"
        
        text = QGraphicsTextItem(task_text)
        text.setDefaultTextColor(Qt.black)
        text.setTextWidth(box_width - 2 * text_padding)  # Enable text wrapping
        
        # Set text alignment to center
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignCenter)
        text.document().setDefaultTextOption(text_option)
        
        text.setPos(x_pos + text_padding, y_pos)
        self.scene.addItem(text)
        
        return text.boundingRect().height()

    """
    Create and add progress bar to the scene.
    Displays a blue progress bar with percentage text, or skips if progress value is invalid.

    Args:
        task: Task object containing progress information
        x_pos: X-coordinate for positioning
        y_pos: Y-coordinate for positioning
        box_width: Width of the task box
        text_padding: Padding for text within the box
        progress_bar_height: Height of the progress bar
        progress_bar_margin: Margin between progress bar and bottom edge
    """
    def create_progress_bar(self, task, x_pos, y_pos, box_width, text_padding, progress_bar_height, progress_bar_margin):
        try:
            progress = int(task.progress)
            progress_width = (box_width - 2 * text_padding) * (progress / 100)
            
            # Draw progress bar background
            progress_bg = self.scene.addRect(
                x_pos + text_padding,
                y_pos - progress_bar_height - progress_bar_margin,
                box_width - 2 * text_padding,
                progress_bar_height,
                QPen(Qt.lightGray),
                QBrush(Qt.lightGray)
            )
            
            # Draw progress bar
            progress_bar = self.scene.addRect(
                x_pos + text_padding,
                y_pos - progress_bar_height - progress_bar_margin,
                progress_width,
                progress_bar_height,
                QPen(Qt.blue),
                QBrush(Qt.blue)
            )
            
            # Add progress text
            progress_text = QGraphicsTextItem(f"{progress}%")
            progress_text.setDefaultTextColor(Qt.white)
            progress_text.setFont(QFont("Arial", 8, QFont.Bold))
            
            # Center progress text on the bar
            text_width = progress_text.boundingRect().width()
            text_height = progress_text.boundingRect().height()
            text_x = x_pos + text_padding + (box_width - 2 * text_padding - text_width) / 2
            text_y = y_pos - progress_bar_height - progress_bar_margin + (progress_bar_height - text_height) / 2
            progress_text.setPos(text_x, text_y)
            self.scene.addItem(progress_text)
        except ValueError:
            pass  # Skip progress bar if progress value is invalid

    """
    Calculate the height needed for each project lane.
    Includes space for project name and all associated tasks.

    Args:
        project_tasks: Dictionary mapping project names to their tasks
        min_box_height: Minimum height for task boxes
        spacing: Vertical spacing between tasks

    Returns:
        Dictionary mapping project names to their total heights
    """
    def calculate_lane_heights(self, project_tasks, min_box_height, spacing):
        lane_heights = {}
        for project, tasks in project_tasks.items():
            # Height for project name
            height = 40
            # Height for tasks (will be adjusted based on text wrapping)
            height += len(tasks) * (min_box_height + spacing)
            lane_heights[project] = height
        return lane_heights

    """
    Display tasks as rectangles with centered text, grouped by project in swim lanes.
    Each task box shows:
    - Time information (Required/Spent) in the upper corners
    - Task name with department abbreviations in the center
    - Progress bar at the bottom
    Tasks are arranged horizontally based on their dependencies.
    """
    def display_tasks(self):
        # Clear existing items
        self.scene.clear()

        # Task box dimensions
        box_width = 200
        min_box_height = 100  # Minimum height for task boxes
        spacing = 50
        lane_spacing = 100  # Vertical spacing between lanes
        margin = 50  # Margin from the edges
        horizontal_spacing = 0  # Space between task boxes horizontally
        text_padding = 10  # Padding for text within boxes
        progress_bar_height = 20  # Height of the progress bar
        progress_bar_margin = 10  # Margin between progress bar and bottom edge
        vertical_spacing = 15  # Consistent vertical spacing between elements

        # Group tasks by project
        project_tasks = defaultdict(list)
        for task in self.task_list.tasks:
            project_tasks[task.project].append(task)

        # Calculate lane heights
        lane_heights = self.calculate_lane_heights(project_tasks, min_box_height, spacing)

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

                # Create temporary time items to calculate their height
                temp_time_required = QGraphicsTextItem(f"Required: {task.time_required}")
                temp_time_spent = QGraphicsTextItem(f"Spent: {task.time_spent}")
                time_info_height = max(temp_time_required.boundingRect().height(), temp_time_spent.boundingRect().height())

                # Create temporary task text to calculate its height
                temp_task_text = QGraphicsTextItem(task.task)
                temp_task_text.setTextWidth(box_width - 2 * text_padding)
                text_height = temp_task_text.boundingRect().height()

                # Calculate box height
                box_height = max(min_box_height, 
                               text_padding +  # Top padding
                               time_info_height +  # Time info height
                               vertical_spacing +  # Space after time info
                               text_height +  # Task name height
                               vertical_spacing +  # Space after task name
                               progress_bar_height +  # Progress bar height
                               progress_bar_margin)  # Bottom margin

                # Create task box
                rect = self.scene.addRect(
                    x_pos, task_y, box_width, box_height,
                    QPen(Qt.black),
                    QBrush(Qt.white)
                )

                # Add time information
                self.create_time_info(task, x_pos, task_y, box_width, text_padding)

                # Create task name text with wrapping
                self.create_task_text(task, x_pos, task_y + text_padding + time_info_height + vertical_spacing, 
                                    box_width, text_padding)

                # Add progress bar
                self.create_progress_bar(task, x_pos, task_y + box_height, box_width, text_padding, 
                                       progress_bar_height, progress_bar_margin)

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