from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QCheckBox, QLineEdit)


class MathSettingsWidget(QWidget):
    """Settings widget for configuring mental math problems."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Dynamic Zetamac Settings")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Operation selection group
        operations_group = QGroupBox("Select Operations")
        operations_layout = QVBoxLayout(operations_group)
        
        operations_layout = self.create_ops_layout(operations_layout)
        
        main_layout.addWidget(operations_group)

        # Difficulty selection group
        self.dynamic_checkbox = QCheckBox("Enable Dynamic Difficulty")
        self.dynamic_checkbox.setChecked(True)
        main_layout.addWidget(self.dynamic_checkbox)

        # Start button
        self.start_button = QPushButton("Start Practice")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        main_layout.addWidget(self.start_button)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()

    def create_ops_layout(self, layout):
        """Create the operations layout with checkboxes and range widgets."""
        self.addition_checkbox = QCheckBox("Addition")
        self.subtraction_checkbox = QCheckBox("Subtraction")
        self.multiplication_checkbox = QCheckBox("Multiplication")
        self.division_checkbox = QCheckBox("Division")

        # Set default selections
        self.addition_checkbox.setChecked(True)
        self.addition_range_widget = self.create_range_widget("Addition Range:", 2, 100, 2, 100)
        self.subtraction_checkbox.setChecked(True)
        self.multiplication_checkbox.setChecked(True)
        self.multiplication_range_widget = self.create_range_widget("Multiplication Range:", 2, 12, 2, 100)
        self.division_checkbox.setChecked(True)

        layout.addWidget(self.addition_checkbox)
        layout.addWidget(self.addition_range_widget)
        layout.addWidget(self.subtraction_checkbox)
        layout.addWidget(QLabel("Addition Problems in Reverse"))
        layout.addWidget(self.multiplication_checkbox)
        layout.addWidget(self.multiplication_range_widget)
        layout.addWidget(self.division_checkbox)
        layout.addWidget(QLabel("Multiplication Problems in Reverse"))
        return layout

    def create_range_widget(self, label_text, r1_min, r1_max, r2_min, r2_max):
        """Create a range selection widget with two number inputs using QLineEdit."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Label
        label = QLabel(label_text)
        label.setMinimumWidth(150)
        layout.addWidget(label)
        
        # Left parenthesis
        layout.addWidget(QLabel("("))
        
        # First number range
        min_edit1 = QLineEdit()
        min_edit1.setText(str(r1_min))
        min_edit1.setMinimumWidth(60)
        min_edit1.setMaximumWidth(80)
        layout.addWidget(min_edit1)
        
        layout.addWidget(QLabel("to"))
        
        max_edit1 = QLineEdit()
        max_edit1.setText(str(r1_max))
        max_edit1.setMinimumWidth(60)
        max_edit1.setMaximumWidth(80)
        layout.addWidget(max_edit1)
        
        layout.addWidget(QLabel(") + ("))
        
        # Second number range
        min_edit2 = QLineEdit()
        min_edit2.setText(str(r2_min))
        min_edit2.setMinimumWidth(60)
        min_edit2.setMaximumWidth(80)
        layout.addWidget(min_edit2)
        
        layout.addWidget(QLabel("to"))
        
        max_edit2 = QLineEdit()
        max_edit2.setText(str(r2_max))
        max_edit2.setMinimumWidth(60)
        max_edit2.setMaximumWidth(80)
        layout.addWidget(max_edit2)
        
        layout.addWidget(QLabel(")"))
        
        # Add stretch to align left
        layout.addStretch()
        
        # Store line edits as attributes of the widget for easy access
        widget.min_edit1 = min_edit1
        widget.max_edit1 = max_edit1
        widget.min_edit2 = min_edit2
        widget.max_edit2 = max_edit2
        
        return widget
    
    def connect_signals(self):
        """Connect signals and slots."""
        # Enable/disable range widgets based on checkbox states
        self.addition_checkbox.toggled.connect(
            lambda checked: self.addition_range_widget.setEnabled(checked)
        )
        self.multiplication_checkbox.toggled.connect(
            lambda checked: self.multiplication_range_widget.setEnabled(checked)
        )
        
        # Update start button state when checkboxes change
        for checkbox in [self.addition_checkbox, self.subtraction_checkbox, 
                        self.multiplication_checkbox, self.division_checkbox]:
            checkbox.toggled.connect(self.update_start_button)
        
        # Initial update
        self.update_start_button()
    
    def update_start_button(self):
        """Enable/disable start button based on whether any operation is selected."""
        any_selected = any([
            self.addition_checkbox.isChecked(),
            self.subtraction_checkbox.isChecked(),
            self.multiplication_checkbox.isChecked(),
            self.division_checkbox.isChecked()
        ])
        self.start_button.setEnabled(any_selected)
    
    def get_settings(self):
        """Get the current settings as a dictionary."""
        settings = {
            'operations': {
                'addition': self.addition_checkbox.isChecked(),
                'subtraction': self.subtraction_checkbox.isChecked(),
                'multiplication': self.multiplication_checkbox.isChecked(),
                'division': self.division_checkbox.isChecked()
            },
            'ranges': {}
        }
        
        if self.addition_checkbox.isChecked():
            settings['ranges']['addition'] = {
                'operand1': (int(self.addition_range_widget.min_edit1.text()) if self.addition_range_widget.min_edit1.text().isdigit() else 2, 
                           int(self.addition_range_widget.max_edit1.text()) if self.addition_range_widget.max_edit1.text().isdigit() else 100),
                'operand2': (int(self.addition_range_widget.min_edit2.text()) if self.addition_range_widget.min_edit2.text().isdigit() else 2, 
                           int(self.addition_range_widget.max_edit2.text()) if self.addition_range_widget.max_edit2.text().isdigit() else 100)
            }
        
        if self.multiplication_checkbox.isChecked():
            settings['ranges']['multiplication'] = {
                'operand1': (int(self.multiplication_range_widget.min_edit1.text()) if self.multiplication_range_widget.min_edit1.text().isdigit() else 2, 
                           int(self.multiplication_range_widget.max_edit1.text()) if self.multiplication_range_widget.max_edit1.text().isdigit() else 100),
                'operand2': (int(self.multiplication_range_widget.min_edit2.text()) if self.multiplication_range_widget.min_edit2.text().isdigit() else 2, 
                           int(self.multiplication_range_widget.max_edit2.text()) if self.multiplication_range_widget.max_edit2.text().isdigit() else 100)
            }

        if self.dynamic_checkbox.isChecked():
            settings['dynamic'] = True
        else:
            settings['dynamic'] = False

        return settings



