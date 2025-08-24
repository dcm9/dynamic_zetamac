import numpy as np
import csv
import os
import time
from datetime import datetime
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QApplication)
from PySide6.QtGui import QFont


# {'operations': {'addition': True, 'subtraction': True, 'multiplication': True, 'division': True},
#  'ranges': {'addition': {'operand1': (2, 100), 'operand2': (2, 100)},
#             'multiplication': {'operand1': (2, 12), 'operand2': (2, 12)}}}

class QuestionBase():
    def __init__(self, settings):
        self.operations = settings['operations']
        self.ranges = settings['ranges']

    def get_problem(self):
        # Generate a math problem based on the selected operations and ranges
        operation = np.random.choice(list(key for key in self.operations.keys() if self.operations[key]))

        if operation in self.ranges:
            range1 = self.ranges[operation]['operand1']
            range2 = self.ranges[operation]['operand2']
        else:
            if operation == 'subtraction':
                range1 = self.ranges['addition']['operand1']
                range2 = self.ranges['addition']['operand2']
            else:
                range1 = self.ranges['multiplication']['operand1']
                range2 = self.ranges['multiplication']['operand2']

        num1 = np.random.randint(range1[0], range1[1] + 1)
        num2 = np.random.randint(range2[0], range2[1] + 1)

        if operation == 'addition':
            problem = f"{num1} + {num2}"
        elif operation == 'subtraction':
            # Ensure positive result (whole number)
            if num1 < num2:
                num1, num2 = num2, num1
            problem = f"{num1} - {num2}"
        elif operation == 'multiplication':
            problem = f"{num1} * {num2}"
        elif operation == 'division':
            # Ensure no division by zero and integer result
            # Make num1 a multiple of num2 to guarantee whole number answer
            if num2 == 0:
                num2 = 1

            # Ensure min of two nums is the dividend
            dividend = min(num1, num2)
            divisor = dividend * max(num1, num2)
            problem = f"{divisor} / {dividend}"

        return problem

    def get_answer(self, problem):
        return eval(problem)

    def check_answer(self, problem, answer: int):
        correct_answer = self.get_answer(problem)
        return correct_answer == answer

class MathLoopWindow(QMainWindow):
    def __init__(self, settings, parent_window=None):
        super().__init__()
        self.settings = settings
        self.parent_window = parent_window
        self.question_base = QuestionBase(settings)
        self.score = 0
        self.total_questions = 0
        self.time_remaining = 120  # 120 seconds
        self.current_problem = ""
        
        # Statistics tracking variables
        self.problem_start_time = None
        self.attempts_for_current_problem = 0
        self.session_start_time = datetime.now()
        
        # Initialize CSV file for statistics
        self.setup_csv_logging()
        
        self.setup_ui()
        self.setup_timer()
        self.new_problem()
    
    def setup_csv_logging(self):
        """Initialize CSV file for logging statistics."""
        # Create data directory if it doesn't exist
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Create unique filename with timestamp
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        self.csv_filename = os.path.join(data_dir, f"math_practice_{timestamp}.csv")
        
        # Create CSV file with headers
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'session_timestamp',
                'problem',
                'duration_seconds',
                'attempts',
            ])
    
    def log_question_stats(self, problem, time_taken, attempts):
        """Log statistics for a question to CSV."""
        try:            
            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    problem,
                    round(time_taken, 3),
                    attempts,
                ])
        except Exception as e:
            print(f"Error logging to CSV: {e}")
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Math Practice - 120 Second Challenge")
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Timer and score display
        top_layout = QHBoxLayout()
        
        self.timer_label = QLabel(f"{self.time_remaining}")
        self.timer_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.timer_label.setStyleSheet("color: #2196F3; padding: 10px;")
        top_layout.addWidget(self.timer_label)
        
        top_layout.addStretch()
        
        self.score_label = QLabel("0")
        self.score_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.score_label.setStyleSheet("color: #4CAF50; padding: 10px;")
        top_layout.addWidget(self.score_label)
        
        layout.addLayout(top_layout)
        
        # Problem display
        self.problem_label = QLabel("")
        self.problem_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.problem_label.setAlignment(Qt.AlignCenter)
        self.problem_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 10px;
                padding: 30px;
                margin: 20px;
            }
        """)
        layout.addWidget(self.problem_label)
        
        # Answer input
        answer_layout = QHBoxLayout()
        
        answer_label = QLabel("Answer:")
        answer_label.setFont(QFont("Arial", 16))
        answer_layout.addWidget(answer_label)
        
        self.answer_input = QLineEdit()
        self.answer_input.setFont(QFont("Arial", 18))
        self.answer_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 18px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        self.answer_input.returnPressed.connect(self.submit_answer)
        answer_layout.addWidget(self.answer_input)
        
        layout.addLayout(answer_layout)
        
        # Feedback label
        self.feedback_label = QLabel("")
        self.feedback_label.setFont(QFont("Arial", 14))
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.feedback_label)
        
        # Results area (initially hidden)
        self.results_label = QLabel("")
        self.results_label.setFont(QFont("Arial", 16))
        self.results_label.setAlignment(Qt.AlignCenter)
        self.results_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 2px solid #2196F3;
                border-radius: 10px;
                padding: 20px;
                margin: 20px;
            }
        """)
        self.results_label.hide()
        layout.addWidget(self.results_label)
        
        # Button layout for restart and back to settings (initially hidden)
        self.button_layout = QHBoxLayout()
        
        self.restart_button = QPushButton("Start New Session")
        self.restart_button.setFont(QFont("Arial", 14))
        self.restart_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.restart_button.clicked.connect(self.restart_session)
        self.button_layout.addWidget(self.restart_button)
        
        self.back_button = QPushButton("Back to Settings")
        self.back_button.setFont(QFont("Arial", 14))
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.back_button.clicked.connect(self.back_to_settings)
        self.button_layout.addWidget(self.back_button)
        
        # Create a widget to hold the button layout and hide it initially
        self.button_widget = QWidget()
        self.button_widget.setLayout(self.button_layout)
        self.button_widget.hide()
        layout.addWidget(self.button_widget)
        
        layout.addStretch()
    
    def setup_timer(self):
        """Set up the countdown timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # Update every second
    
    def update_timer(self):
        """Update the timer display and check if time is up."""
        self.time_remaining -= 1
        self.timer_label.setText(f"{self.time_remaining}")
    
        if self.time_remaining <= 0:
            self.end_session()
    
    def new_problem(self):
        """Generate and display a new math problem."""
        self.current_problem = self.question_base.get_problem()
        self.problem_label.setText(self.current_problem)
        self.answer_input.clear()
        self.answer_input.setFocus()
        self.feedback_label.clear()
        
        # Start timing for this problem
        self.problem_start_time = time.time()
        self.attempts_for_current_problem = 0
    
    def submit_answer(self):
        """Check the submitted answer and update score."""
        if self.time_remaining <= 0:
            return
            
        try:
            user_answer = int(self.answer_input.text())
            self.attempts_for_current_problem += 1
            
            # Calculate time taken for this problem
            time_taken = time.time() - self.problem_start_time if self.problem_start_time else 0
            
            is_correct = self.question_base.check_answer(self.current_problem, user_answer)
            
            if is_correct:
                self.total_questions += 1
                self.score += 1
                
                # Log statistics to CSV
                self.log_question_stats(
                    self.current_problem,
                    round(time_taken, 3),
                    self.attempts_for_current_problem
                )
                
                self.update_score_display()
                
                self.new_problem()
                
        except ValueError:
            self.feedback_label.setText("Please enter a valid number")
            self.feedback_label.setStyleSheet("color: #ff9800; padding: 10px;")
    
    def update_score_display(self):
        """Update the score display."""
        accuracy = (self.score / self.total_questions * 100) if self.total_questions > 0 else 0
        self.score_label.setText(f"{self.score}")
    
    def end_session(self):
        """End the math session and show results."""
        self.timer.stop()
        
        # Hide input elements
        self.answer_input.hide()
        self.feedback_label.hide()
        self.problem_label.hide()
        
        # Show results
        accuracy = (self.score / self.total_questions * 100) if self.total_questions > 0 else 0
        results_text = f"""
        🎉 Session Complete! 🎉
        
        Final Score: {self.score} correct out of {self.total_questions} problems
        Accuracy: {accuracy:.1f}%
        
        Problems per minute: {self.total_questions / 2:.1f}
        """
        
        self.results_label.setText(results_text)
        self.results_label.show()
        self.button_widget.show()
    
    def restart_session(self):
        """Restart the math session."""
        self.score = 0
        self.total_questions = 0
        self.time_remaining = 120
        
        # Reset statistics tracking for new session
        self.session_start_time = datetime.now()
        self.problem_start_time = None
        self.attempts_for_current_problem = 0
        self.setup_csv_logging()  # Create new CSV file for new session
        
        # Show input elements
        self.answer_input.show()
        # self.submit_button.show()
        self.feedback_label.show()
        self.problem_label.show()
        
        # Hide results
        self.results_label.hide()
        self.button_widget.hide()
        
        # Reset displays
        self.timer_label.setText(f"{self.time_remaining}")
        self.timer_label.setStyleSheet("color: #2196F3; padding: 10px;")
        self.score_label.setText(f"{self.score}")

        # Start timer and new problem
        self.setup_timer()
        self.new_problem()

    def back_to_settings(self):
        self.close()
        if self.parent_window:
            self.parent_window.show()