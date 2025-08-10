#Backup Tool
---
This is a simple yet powerful desktop application for backing up files, built with Python and customtkinter. It's designed to be a fast and reliable solution for creating backup copies of important project folders.
✨ **Features**
Graphical User Interface (GUI): A user-friendly interface to easily select source and destination folders.Efficient Copying: Utilizes system-specific commands for optimal performance:Windows: Employs robocopy for multithreaded and robust file synchronization.Other OS (e.g., macOS, Linux): Uses rsync for efficient and fast transfers.Progress Bar: Displays the progress of the backup process in real-time.Custom Naming: Allows for custom backup folder names or automatic naming based on the current date and time.Configuration: Saves user settings (like default naming preference) in a config.json file.
🛠️ **Prerequisites**
To run this application, you need to have Python installed on your system. This tool has been tested with Python 3.You will also need to install the following Python libraries:customtkinterPillowYou can install them using pip:pip install customtkinter Pillow
🚀 **Installation and Usage**
Clone or download this repository to your local machine.Navigate to the project directory in your terminal or command prompt.Run the script:python backup_tool.py
The application window will open, and you can then select your folders and start the backup process.
📄 **License**
This project is licensed under the MIT License.
