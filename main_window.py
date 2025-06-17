# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QToolBar, QAction, QStyle, QGraphicsItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QRectF, QLineF, QSize
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTextOption, QIcon, QPixmap
from task_list import TaskList
from collections import defaultdict
import resources_rc
import os

class TaskGraphicsItem(QGraphicsItem):
    """
    Custom graphics item that represents a single task with all its visual elements.
    Encapsulates the drawing of the task box, time information, task text, and progress bar.
    """
    
    def __init__(self, task, box_width=200, min_box_height=100, text_padding=10, 
                 progress_bar_height=20, progress_bar_margin=10, vertical_spacing=15):
        super().__init__()
        self.task = task
        self.box_width = box_width
        self.min_box_height = min_box_height
        self.text_padding = text_padding
        self.progress_bar_height = progress_bar_height
        self.progress_bar_margin = progress_bar_margin
        self.vertical_spacing = vertical_spacing
        self.compressed_mode = False  # Default to normal mode
        
        # Calculate the required height for this task
        self.box_height = self._calculate_box_height()
    
    def set_compressed_mode(self, compressed: bool):
        """
        Switch between compressed and normal display modes.
        
        Args:
            compressed (bool): True for compressed mode, False for normal mode
        """
        if self.compressed_mode != compressed:
            self.compressed_mode = compressed
            self.box_height = self._calculate_box_height()
            # Trigger a redraw
            self.update()
    
    def is_compressed_mode(self) -> bool:
        """Return True if the item is in compressed mode."""
        return self.compressed_mode
    
    def _calculate_box_height(self):
        """Calculate the required height for the task box based on content."""
        if self.compressed_mode:
            # Compressed mode: smaller height, less padding, no progress bar, no time info, same font size
            compressed_min_height = 60
            compressed_text_padding = 5
            compressed_vertical_spacing = 8
            
            # Calculate task text height
            task_text = self.task.task
            if self.task.other_departments:
                task_text += f" ({', '.join(self.task.other_departments)})"
            
            # Estimate text height based on text length and wrapping (same font size as normal mode)
            text_width = self.box_width - 2 * compressed_text_padding
            estimated_chars_per_line = int(text_width / 8)  # Rough estimate
            estimated_lines = max(1, len(task_text) // estimated_chars_per_line + 1)
            text_height = estimated_lines * 16  # Same line height as normal mode
            
            # Calculate total height for compressed mode (no progress bar, no time info)
            total_height = (compressed_text_padding +  # Top padding
                           text_height +  # Task name height
                           compressed_text_padding)  # Bottom padding
            
            return max(compressed_min_height, total_height)
        else:
            # Normal mode: original calculation
            # Calculate time info height (simplified calculation)
            time_info_height = 20  # Approximate height for time text
            
            # Calculate task text height
            task_text = self.task.task
            if self.task.other_departments:
                task_text += f" ({', '.join(self.task.other_departments)})"
            
            # Estimate text height based on text length and wrapping
            text_width = self.box_width - 2 * self.text_padding
            estimated_chars_per_line = int(text_width / 8)  # Rough estimate
            estimated_lines = max(1, len(task_text) // estimated_chars_per_line + 1)
            text_height = estimated_lines * 16  # Approximate line height
            
            # Calculate total height
            total_height = (self.text_padding +  # Top padding
                           time_info_height +  # Time info height
                           self.vertical_spacing +  # Space after time info
                           text_height +  # Task name height
                           self.vertical_spacing +  # Space after task name
                           self.progress_bar_height +  # Progress bar height
                           self.progress_bar_margin)  # Bottom margin
            
            return max(self.min_box_height, total_height)
    
    def boundingRect(self):
        """Return the bounding rectangle of the task item."""
        return QRectF(0, 0, self.box_width, self.box_height)
    
    def paint(self, painter, option, widget):
        """Paint the task item with all its visual elements."""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the main task box
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(0, 0, self.box_width, self.box_height)
        
        # Draw time information
        self._draw_time_info(painter)
        
        # Draw task text
        self._draw_task_text(painter)
        
        # Draw progress bar
        self._draw_progress_bar(painter)
    
    def _draw_time_info(self, painter):
        """Draw the time required and time spent information."""
        # Don't draw time info in compressed mode
        if self.compressed_mode:
            return
            
        if self.compressed_mode:
            # Compressed mode: smaller padding, same font size
            text_padding = 5
            font_size = 9  # Same as normal mode
            y_offset = 15  # Same as normal mode
        else:
            # Normal mode: original parameters
            text_padding = self.text_padding
            font_size = 9
            y_offset = 15
        
        # Time required (top left)
        time_required_text = f"Required: {self.task.time_required}"
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", font_size))
        painter.drawText(text_padding, text_padding + y_offset, time_required_text)
        
        # Time spent (top right)
        time_spent_text = f"Spent: {self.task.time_spent}"
        try:
            if int(self.task.time_spent) > int(self.task.time_required):
                painter.setPen(Qt.red)
            else:
                painter.setPen(QColor(0, 100, 0))  # Dark green
        except ValueError:
            painter.setPen(Qt.black)
        
        # Calculate position for right-aligned text
        text_rect = painter.fontMetrics().boundingRect(time_spent_text)
        text_x = int(self.box_width - text_padding - text_rect.width())
        painter.drawText(text_x, text_padding + y_offset, time_spent_text)
    
    def _draw_task_text(self, painter):
        """Draw the task name with department abbreviations."""
        if self.compressed_mode:
            # Compressed mode: smaller padding, same font size, no time info
            text_padding = 5
            font_size = 10  # Same as normal mode
        else:
            # Normal mode: original parameters
            text_padding = self.text_padding
            font_size = 10
            vertical_spacing = self.vertical_spacing
            time_info_height = 20
            progress_bar_height = self.progress_bar_height
            progress_bar_margin = self.progress_bar_margin
        
        task_text = self.task.task
        if self.task.other_departments:
            task_text += f" ({', '.join(self.task.other_departments)})"
        
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", font_size))
        
        # Calculate text position (centered horizontally, below time info)
        if self.compressed_mode:
            # Compressed mode: no time info, no progress bar, so text can extend to full height
            text_rect = QRectF(text_padding, 
                              text_padding,
                              self.box_width - 2 * text_padding,
                              self.box_height - 2 * text_padding)
        else:
            # Normal mode: leave space for time info and progress bar
            text_rect = QRectF(text_padding, 
                              text_padding + time_info_height + vertical_spacing,
                              self.box_width - 2 * text_padding,
                              self.box_height - text_padding - time_info_height - 2 * vertical_spacing - progress_bar_height - progress_bar_margin)
        
        # Draw text with word wrapping and center alignment
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, task_text)
    
    def _draw_progress_bar(self, painter):
        """Draw the progress bar at the bottom of the task box."""
        # Don't draw progress bar in compressed mode
        if self.compressed_mode:
            return
            
        if self.compressed_mode:
            # Compressed mode: smaller progress bar
            text_padding = 5
            progress_bar_height = 12
            progress_bar_margin = 5
            font_size = 8  # Same as normal mode
        else:
            # Normal mode: original parameters
            text_padding = self.text_padding
            progress_bar_height = self.progress_bar_height
            progress_bar_margin = self.progress_bar_margin
            font_size = 8
        
        try:
            progress = int(self.task.progress)
            progress_width = int((self.box_width - 2 * text_padding) * (progress / 100))
            
            # Progress bar position
            bar_y = int(self.box_height - progress_bar_height - progress_bar_margin)
            bar_x = text_padding
            
            # Draw progress bar background
            painter.setPen(QPen(Qt.lightGray))
            painter.setBrush(QBrush(Qt.lightGray))
            painter.drawRect(bar_x, bar_y, 
                           int(self.box_width - 2 * text_padding), 
                           progress_bar_height)
            
            # Draw progress bar
            painter.setPen(QPen(Qt.blue))
            painter.setBrush(QBrush(Qt.blue))
            painter.drawRect(bar_x, bar_y, progress_width, progress_bar_height)
            
            # Draw progress text
            progress_text = f"{progress}%"
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", font_size, QFont.Bold))
            
            # Center progress text on the bar
            text_rect = painter.fontMetrics().boundingRect(progress_text)
            text_x = int(bar_x + (self.box_width - 2 * text_padding - text_rect.width()) / 2)
            text_y = int(bar_y + (progress_bar_height - text_rect.height()) / 2 + text_rect.height())
            painter.drawText(text_x, text_y, progress_text)
            
        except ValueError:
            pass  # Skip progress bar if progress value is invalid

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

        # Add separator
        toolbar.addSeparator()

        # Toggle compressed mode action
        self.toggle_compressed_action = QAction(QIcon(":/icons/compress_24dp.png"), "Compressed Mode", self)
        self.toggle_compressed_action.setStatusTip("Toggle compressed/compact view")
        self.toggle_compressed_action.setCheckable(True)
        self.toggle_compressed_action.triggered.connect(self.toggle_compressed_mode)
        toolbar.addAction(self.toggle_compressed_action)

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
    Toggle compressed mode for all task items.
    """
    def toggle_compressed_mode(self):
        """Toggle between compressed and normal display modes for all task items."""
        compressed = self.toggle_compressed_action.isChecked()
        
        # Find all TaskGraphicsItem objects in the scene
        for item in self.scene.items():
            if isinstance(item, TaskGraphicsItem):
                item.set_compressed_mode(compressed)
        
        # Recalculate vertical positioning for all task items
        self.reposition_task_items()
        
        # Update the scene to reflect the changes
        self.scene.update()
        
        # Adjust scene rect to show all items with padding
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))

    """
    Reposition all task items after compressed mode changes.
    """
    def reposition_task_items(self):
        """Recalculate and update the vertical positions of all task items."""
        # Task box dimensions
        box_width = 200
        spacing = 12  # Reduced from 50 to 12 (25% of original)
        lane_spacing = 50  # Doubled from 25 to 50 for better visual separation
        margin = 50
        horizontal_spacing = 0

        # Group tasks by project
        project_tasks = defaultdict(list)
        for task in self.task_list.tasks:
            project_tasks[task.project].append(task)

        # Collect all separator lines first
        separator_lines = [item for item in self.scene.items() if isinstance(item, QGraphicsLineItem)]
        line_index = 0

        # Reposition tasks in each lane
        current_y = margin
        for project, tasks in project_tasks.items():
            # Find project name item
            project_items = [item for item in self.scene.items() 
                           if isinstance(item, QGraphicsTextItem) and item.toPlainText() == project]
            if project_items:
                project_text = project_items[0]
                project_text.setPos(margin, current_y)

            # Calculate horizontal positions for tasks
            positions = self.calculate_task_positions(tasks)

            # Reposition tasks in this lane
            task_y = current_y + 60  # Increased from 40 to 60 to accommodate larger project name
            max_x = margin
            lane_height = 0
            
            for task in tasks:
                # Find the task item
                task_items = [item for item in self.scene.items() 
                            if isinstance(item, TaskGraphicsItem) and item.task.task_id == task.task_id]
                if task_items:
                    task_item = task_items[0]
                    
                    # Calculate horizontal position
                    x_pos = margin + positions[task.task_id] * (box_width + horizontal_spacing)
                    
                    # Update position
                    task_item.setPos(x_pos, task_y)
                    
                    # Update tracking variables
                    max_x = max(max_x, x_pos + box_width)
                    lane_height = max(lane_height, task_y + task_item.box_height - (current_y + 60))
                    
                    task_y += task_item.box_height + spacing

            # Update separator line position (if not the last project)
            if project != list(project_tasks.keys())[-1] and line_index < len(separator_lines):
                line = separator_lines[line_index]
                line_y = current_y + 60 + lane_height + 25  # Updated to use 60 instead of 40
                line.setLine(margin, line_y, max_x + 50, line_y)
                line_index += 1

            # Move to next lane
            current_y += 60 + lane_height + lane_spacing

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
        spacing = 12  # Reduced from 50 to 12 (25% of original)
        lane_spacing = 50  # Doubled from 25 to 50 for better visual separation
        margin = 50  # Margin from the edges
        horizontal_spacing = 0  # Space between task boxes horizontally

        # Group tasks by project
        project_tasks = defaultdict(list)
        for task in self.task_list.tasks:
            project_tasks[task.project].append(task)

        # Draw swim lanes for each project
        current_y = margin
        for project, tasks in project_tasks.items():
            # Draw project name
            project_text = QGraphicsTextItem(project)
            font = QFont()
            font.setBold(True)
            font.setPointSize(20)  # Doubled from default ~10 to 20
            project_text.setFont(font)
            project_text.setDefaultTextColor(Qt.black)
            project_text.setPos(margin, current_y)
            self.scene.addItem(project_text)

            # Calculate horizontal positions for tasks
            positions = self.calculate_task_positions(tasks)

            # Draw tasks in this lane
            task_y = current_y + 60  # Increased from 40 to 60 to accommodate larger project name
            max_x = margin  # Track the rightmost position in this lane
            lane_height = 0  # Track the total height of this lane
            
            for task in tasks:
                # Calculate horizontal position
                x_pos = margin + positions[task.task_id] * (box_width + horizontal_spacing)
                
                # Create and add the task graphics item
                task_item = TaskGraphicsItem(task, box_width, min_box_height)
                task_item.setPos(x_pos, task_y)
                self.scene.addItem(task_item)
                
                # Update tracking variables
                max_x = max(max_x, x_pos + box_width)
                lane_height = max(lane_height, task_y + task_item.box_height - (current_y + 60))  # Height from project name to bottom of this task
                
                task_y += task_item.box_height + spacing

            # Draw horizontal separator line
            if project != list(project_tasks.keys())[-1]:  # Don't draw line after last project
                line_y = current_y + 60 + lane_height + 25  # Updated to use 60 instead of 40
                line = QLineF(margin, line_y, 
                            max_x + 50, line_y)  # Line extends to the rightmost task plus padding
                self.scene.addLine(line, QPen(Qt.black, 2, Qt.DashLine))

            # Move to next lane: project name (60) + lane height + spacing
            current_y += 60 + lane_height + lane_spacing

        # Adjust scene rect to show all items with padding
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50)) 