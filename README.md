# Task Tool

Task Tool is a visual project management application that displays tasks organized in swim lanes by project. Each task shows time information, progress, and dependencies.

## Features

- **Swim Lane View**: Tasks are grouped by project in horizontal lanes
- **Dependency Visualization**: Tasks are positioned based on their dependencies
- **Time Tracking**: Shows required and spent time for each task
- **Progress Bars**: Visual progress indication for each task
- **Compressed Mode**: Compact view for overview of many tasks
- **Zoom Controls**: Zoom in, out, and reset view

## Toolbar Buttons

- **Zoom In**: Magnify the view to see details better
- **Zoom Out**: Reduce the view to see more content
- **Reset Zoom**: Return to the original zoom level
- **Compressed Mode**: Toggle between normal and compact task view
- **Help**: Show help dialog with usage instructions
- **Info**: Show application information and license details

## Usage

- **Zoom In/Out**: Use the zoom buttons or mouse wheel
- **Compressed Mode**: Toggle for compact task view
- **Navigation**: Scroll to view different projects and tasks
- **Help**: Click the help button (?) for detailed instructions
- **Info**: Click the info button (i) for application details and license

## File Format

The application reads CSV files with semicolon-separated values containing the following columns:

- **TaskId**: Unique identifier for each task
- **Project**: Project name for grouping
- **Task**: Task description
- **TimeRequired**: Estimated time required
- **TimeSpent**: Actual time spent
- **Progress**: Progress percentage (0-100)
- **OtherDepartments**: Space-separated department abbreviations
- **DependsOnTask**: Space-separated task IDs this task depends on

## Installation

1. Ensure Python 3.x is installed
2. Install required dependencies: `pip install PyQt5`
3. Run the application: `python main.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Jan-Eric-P
