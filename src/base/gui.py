from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from src.base.settings import MathSettingsWidget
from src.base.math_loop import MathLoopWindow

class MathSettingsWindow(QMainWindow):
    """Main window for the math settings application."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main window."""
        self.setWindowTitle("Mental Math Practice - Settings")
        self.setFixedSize(500, 400)
        
        # Create central widget
        self.settings_widget = MathSettingsWidget()
        self.setCentralWidget(self.settings_widget)
        
        # Connect start button
        self.settings_widget.start_button.clicked.connect(self.start_practice)
    
    def start_practice(self):
        """Handle start practice button click."""
        settings = self.settings_widget.get_settings()
        
        # Validate that at least one operation is selected
        if not any(settings['operations'].values()):
            # This shouldn't happen due to button disabling, but just in case
            return
        
        # Create and show the math loop window with parent reference
        self.math_window = MathLoopWindow(settings, parent_window=self)
        self.math_window.show()
        
        # Hide the settings window
        self.hide()


if __name__ == "__main__":
    app = QApplication([])
    
    window = MathSettingsWindow()
    window.show()
    
    app.exec()