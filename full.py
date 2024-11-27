import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QFileDialog, QSpinBox, 
                             QTimeEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QColor

class Scheduler:
    def __init__(self):
        self.employee_data = None
        self.schedule = None
        self.tasks = []

    def load_employee_data(self, file_path):
        self.employee_data = pd.read_csv(file_path)
        self.validate_employee_data()
        self.tasks = [col for col in self.employee_data.columns if col not in ['ID', 'Name', 'PreferredDayOff1', 'PreferredDayOff2', 'PreferredDayOff3', 'BreakType', 'Status', 'SkillRating', 'PreferredTask']]
        return self.tasks

    def validate_employee_data(self):
        if self.employee_data['ID'].duplicated().any():
            raise ValueError("Duplicate Employee IDs found.")
        if self.employee_data.isnull().any().any():
            raise ValueError("Missing values in employee data.")
        for col in self.tasks:
            self.employee_data[col] = self.employee_data[col].astype(bool)
        valid_breaks = {1, 2}
        if not set(self.employee_data['BreakType']).issubset(valid_breaks):
            raise ValueError("Invalid break type found in employee data.")

    def generate_schedule(self, params):
        if self.employee_data is None:
            raise ValueError("Employee data not loaded.")

        employees = self.employee_data.copy()
        employees['TotalHours'] = params['total_hours_per_week']
        employees['DailyHours'] = params['total_hours_per_week'] / params['work_days_per_week']

        schedule_columns = ['Date', 'Shift', 'EmployeeID', 'EmployeeName', 'Role', 'StartTime', 'EndTime', 'Break1', 'Break2', 'Break3']
        schedule = pd.DataFrame(columns=schedule_columns)

        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        shifts = ['Morning', 'Evening']

        start_date = datetime.now().date()
        for day in range(params['schedule_duration']):
            current_date = start_date + timedelta(days=day)
            day_of_week = days_of_week[current_date.weekday()]

            for shift in shifts:
                shift_start = self.time_to_datetime(current_date, params['opening_time']) if shift == 'Morning' else self.time_to_datetime(current_date, params['opening_time']) + timedelta(hours=5)
                shift_end = self.time_to_datetime(current_date, params['closing_time']) if shift == 'Evening' else self.time_to_datetime(current_date, params['closing_time']) - timedelta(hours=5)

                available_employees = self.get_available_employees(employees, day_of_week)

                for role in self.tasks:
                    count = params[f'{role.lower()}_per_shift']
                    eligible_employees = available_employees[available_employees[role]]
                    assigned_employees = self.assign_employees(eligible_employees, count, role)

                    for _, employee in assigned_employees.iterrows():
                        breaks = self.assign_breaks(employee['BreakType'], shift_start, shift_end, params)
                        schedule = schedule.append({
                            'Date': current_date,
                            'Shift': shift,
                            'EmployeeID': employee['ID'],
                            'EmployeeName': employee['Name'],
                            'Role': role,
                            'StartTime': shift_start.time().strftime("%H:%M"),
                            'EndTime': shift_end.time().strftime("%H:%M"),
                            'Break1': breaks[0],
                            'Break2': breaks[1] if len(breaks) > 1 else None,
                            'Break3': breaks[2] if len(breaks) > 2 else None
                        }, ignore_index=True)

                        employees.loc[employees['ID'] == employee['ID'], 'TotalHours'] -= employee['DailyHours']

        self.schedule = schedule
        return schedule

    def time_to_datetime(self, date, time):
        return datetime.combine(date, time)

    def get_available_employees(self, employees, day):
        return employees[(employees['TotalHours'] > 0) & 
                         (~employees['PreferredDayOff1'].isin([day])) & 
                         (~employees['PreferredDayOff2'].isin([day])) & 
                         (~employees['PreferredDayOff3'].isin([day]))]

    def assign_employees(self, eligible_employees, count, role):
        preferred_employees = eligible_employees[eligible_employees['PreferredTask'] == role]
        preferred_employees = preferred_employees.sort_values('SkillRating', ascending=False)
        other_employees = eligible_employees[eligible_employees['PreferredTask'] != role]
        other_employees = other_employees.sort_values('SkillRating', ascending=False)
        
        assigned = preferred_employees.head(count)
        if len(assigned) < count:
            assigned = pd.concat([assigned, other_employees.head(count - len(assigned))])
        
        return assigned.sample(frac=1)  # Shuffle to add some randomness

    def assign_breaks(self, break_type, shift_start, shift_end, params):
        break_start = shift_start + timedelta(minutes=params['morning_break_start'])
        break_end = shift_end - timedelta(minutes=params['evening_break_end'])
        available_break_time = int((break_end - break_start).total_seconds() / 60)

        if break_type == 1:  # One 45-minute break and one 15-minute break
            break1 = break_start + timedelta(minutes=15 * np.random.randint(0, (available_break_time - 60) // 15))
            break2 = break1 + timedelta(minutes=60)
            return [break1.strftime("%H:%M"), break2.strftime("%H:%M")]
        elif break_type == 2:  # One 30-minute and two 15-minute breaks
            break1 = break_start + timedelta(minutes=15 * np.random.randint(0, (available_break_time - 60) // 15))
            break2 = break1 + timedelta(minutes=30)
            break3 = break2 + timedelta(minutes=30)
            return [break1.strftime("%H:%M"), break2.strftime("%H:%M"), break3.strftime("%H:%M")]

    def export_to_excel(self, file_path):
        if self.schedule is None:
            raise ValueError("Schedule has not been generated yet.")
        self.schedule.to_excel(file_path, index=False)
        print(f"Schedule exported to {file_path}")

class SchedulerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scheduler = Scheduler()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Employee Scheduler')
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # File loading section
        self.init_file_section(scroll_layout)

        # Parameters section
        self.init_param_section(scroll_layout)

        # Task-specific inputs
        self.task_layout = QVBoxLayout()
        scroll_layout.addLayout(self.task_layout)

        # Generate and Export buttons
        self.init_buttons(scroll_layout)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Schedule display
        self.schedule_table = QTableWidget()
        main_layout.addWidget(self.schedule_table)

    def init_file_section(self, layout):
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        file_button = QPushButton('Load CSV')
        file_button.clicked.connect(self.load_csv)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(file_button)
        layout.addLayout(file_layout)

    def init_param_section(self, layout):
        param_layout = QVBoxLayout()
        param_layout.addWidget(QLabel('Scheduling Parameters:'))

        self.params = {}

        def add_param_row(name, default_value, param_type='int'):
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(f"{name}:"))
            if param_type == 'int':
                self.params[name] = QSpinBox()
                self.params[name].setRange(0, 1000)
                self.params[name].setValue(default_value)
            elif param_type == 'time':
                self.params[name] = QTimeEdit()
                self.params[name].setTime(QTime.fromString(default_value, "HH:mm"))
            row_layout.addWidget(self.params[name])
            param_layout.addLayout(row_layout)

        add_param_row('Total Hours Per Week', 40)
        add_param_row('Work Days Per Week', 5)
        add_param_row('Opening Time', "09:00", 'time')
        add_param_row('Closing Time', "22:00", 'time')
        add_param_row('Schedule Duration (days)', 90)
        add_param_row('Morning Break Start (minutes after opening)', 45)
        add_param_row('Evening Break End (minutes before closing)', 45)

        layout.addLayout(param_layout)

    def init_buttons(self, layout):
        button_layout = QHBoxLayout()
        generate_button = QPushButton('Generate Schedule')
        generate_button.clicked.connect(self.generate_schedule)
        export_button = QPushButton('Export to Excel')
        export_button.clicked.connect(self.export_schedule)
        button_layout.addWidget(generate_button)
        button_layout.addWidget(export_button)
        layout.addLayout(button_layout)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_path_edit.setText(file_path)
            try:
                tasks = self.scheduler.load_employee_data(file_path)
                self.update_task_inputs(tasks)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading CSV: {str(e)}")

    def update_task_inputs(self, tasks):
        for i in reversed(range(self.task_layout.count())): 
            self.task_layout.itemAt(i).widget().setParent(None)

        for task in tasks:
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(f"{task} Per Shift:"))
            self.params[f'{task.lower()}_per_shift'] = QSpinBox()
            self.params[f'{task.lower()}_per_shift'].setRange(0, 100)
            self.params[f'{task.lower()}_per_shift'].setValue(1)
            row_layout.addWidget(self.params[f'{task.lower()}_per_shift'])
            self.task_layout.addLayout(row_layout)

    def generate_schedule(self):
        if self.scheduler.employee_data is None:
            QMessageBox.warning(self, "Warning", "Please load employee data first.")
            return

        try:
            params = {
                'total_hours_per_week': self.params['Total Hours Per Week'].value(),
                'work_days_per_week': self.params['Work Days Per Week'].value(),
                'opening_time': self.params['Opening Time'].time().toPyTime(),
                'closing_time': self.params['Closing Time'].time().toPyTime(),
                'schedule_duration': self.params['Schedule Duration (days)'].value(),
                'morning_break_start': self.params['Morning Break Start (minutes after opening)'].value(),
                'evening_break_end': self.params['Evening Break End (minutes before closing)'].value(),
            }
            
            for task in self.scheduler.tasks:
                params[f'{task.lower()}_per_shift'] = self.params[f'{task.lower()}_per_shift'].value()

            schedule = self.scheduler.generate_schedule(params)
            self.display_schedule(schedule)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating schedule: {str(e)}")

    def display_schedule(self, schedule):
        self.schedule_table.setColumnCount(len(schedule.columns))
        self.schedule_table.setHorizontalHeaderLabels(schedule.columns)
        self.schedule_table.setRowCount(len(schedule))

        for row in range(len(schedule)):
            for col in range(len(schedule.columns)):
                item = QTableWidgetItem(str(schedule.iloc[row, col]))
                self.schedule_table.setItem(row, col, item)

                if schedule.iloc[row]['Shift'] == 'Morning':
                    item.setBackground(QColor(173, 216, 230))
                else:
                    item.setBackground(QColor(255, 228, 196))

        self.schedule_table.resizeColumnsToContents()
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def export_schedule(self):
        if self.scheduler.schedule is None:
            QMessageBox.warning(self, "Warning", "Please generate a schedule first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                self.scheduler.export_to_excel(file_path)
                QMessageBox.information(self, "Success", f"Schedule exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exporting schedule: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SchedulerGUI()
    ex.show()
    sys.exit(app.exec_())
