import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QSpinBox, QTextEdit, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class SchedulerWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler

    def run(self):
        try:
            # Update progress periodically
            self.progress.emit(25)
            result = self.scheduler.generate_schedule()
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler
        self.schedule = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Employee Scheduler')
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Upload button
        self.uploadButton = QPushButton('Upload Employee Data', self)
        self.uploadButton.clicked.connect(self.upload_employee_data)
        layout.addWidget(self.uploadButton)

        # Input fields
        # Total Hours
        layout.addWidget(QLabel("Total Hours Per Week:"))
        self.totalHoursInput = QSpinBox(self)
        self.totalHoursInput.setRange(1, 168)  # Max hours in a week
        self.totalHoursInput.setValue(40)  # Default value
        layout.addWidget(self.totalHoursInput)

        # Work Days
        layout.addWidget(QLabel("Work Days Per Week:"))
        self.workDaysInput = QSpinBox(self)
        self.workDaysInput.setRange(1, 7)
        self.workDaysInput.setValue(5)  # Default value
        layout.addWidget(self.workDaysInput)

        # Opening Time
        layout.addWidget(QLabel("Opening Time (HH:MM):"))
        self.openingTimeInput = QLineEdit(self)
        self.openingTimeInput.setText("09:00")  # Default value
        layout.addWidget(self.openingTimeInput)

        # Closing Time
        layout.addWidget(QLabel("Closing Time (HH:MM):"))
        self.closingTimeInput = QLineEdit(self)
        self.closingTimeInput.setText("17:00")  # Default value
        layout.addWidget(self.closingTimeInput)

        # Generate Schedule button
        self.generateButton = QPushButton('Generate Schedule', self)
        self.generateButton.clicked.connect(self.generate_schedule)
        layout.addWidget(self.generateButton)

        # Export button
        self.exportButton = QPushButton('Export Schedule', self)
        self.exportButton.clicked.connect(self.export_schedule)
        layout.addWidget(self.exportButton)

        # Schedule display area
        self.scheduleDisplay = QTextEdit(self)
        self.scheduleDisplay.setReadOnly(True)
        layout.addWidget(self.scheduleDisplay)

    def upload_employee_data(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Employee Data", "", "CSV Files (*.csv)")
        if fileName:
            self.scheduler.load_employee_data(fileName)

    def generate_schedule(self):
        try:
            # Create params dictionary
            params = {
                'total_hours_per_week': int(self.totalHoursInput.text()),
                'work_days_per_week': int(self.workDaysInput.text()),
                'opening_time': self.openingTimeInput.text(),
                'closing_time': self.closingTimeInput.text()
            }
            
            # Generate schedule with parameters dictionary
            self.schedule = self.scheduler.generate_schedule(params)
            
            # Display schedule in the text area
            if self.schedule is not None:
                self.scheduleDisplay.setText(str(self.schedule))
            else:
                self.scheduleDisplay.setText("Failed to generate schedule")
            
        except Exception as e:
            self.scheduleDisplay.setText(f"Error generating schedule: {str(e)}")

    def on_schedule_complete(self, schedule):
        self.scheduleDisplay.setPlainText(schedule.to_string())
        print(schedule)
        self.progress_bar.hide()

    def show_error(self, error):
        print(f"Error: {error}")
        self.progress_bar.hide()

    def export_schedule(self):
        if self.schedule is None:
            self.scheduleDisplay.setText("Please generate a schedule first")
            return
            
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Export Schedule",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if fileName:
            try:
                self.scheduler.save_schedule_to_excel(self.schedule, fileName)
                self.scheduleDisplay.setText(f"Schedule exported to {fileName}")
            except Exception as e:
                self.scheduleDisplay.setText(f"Error exporting schedule: {str(e)}")
