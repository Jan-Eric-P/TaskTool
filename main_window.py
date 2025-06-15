# -*- coding: utf-8 -*-
"""
@author: Jan-Eric-P
"""

from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

class MainWindow(QMainWindow):
    """
    Main window of the application containing a QGraphicsView as central widget.
    """
    def __init__(self):
        super().__init__()
        
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