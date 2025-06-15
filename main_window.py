# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from task_list import TaskList

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

    def display_tasks(self):
        """
        Display tasks as rectangles with centered text.
        """
        # Clear existing items
        self.scene.clear()

        # Task box dimensions
        box_width = 200
        box_height = 100
        spacing = 50

        # Draw each task
        for i, task in enumerate(self.task_list.tasks):
            # Calculate position
            x = 50  # Fixed x position
            y = i * (box_height + spacing) + 50  # Vertical spacing

            # Create task box
            rect = self.scene.addRect(
                x, y, box_width, box_height,
                QPen(Qt.black),
                QBrush(Qt.white)
            )

            # Add task name text
            text = QGraphicsTextItem(task.task)
            text.setDefaultTextColor(Qt.black)
            
            # Center text in rectangle
            text_width = text.boundingRect().width()
            text_height = text.boundingRect().height()
            text_x = x + (box_width - text_width) / 2
            text_y = y + (box_height - text_height) / 2
            text.setPos(text_x, text_y)
            
            self.scene.addItem(text)

        # Adjust scene rect to show all items with padding
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50)) 