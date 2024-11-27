import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from functools import lru_cache
from datetime import datetime, timedelta

@dataclass
class Employee:
    id: int
    name: str
    break_type: int
    skills: List[str]
    
class SchedulerError(Exception):
    """Base exception for scheduler errors"""
    pass

class InvalidEmployeeData(SchedulerError):
    """Raised when employee data is invalid"""
    pass

from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass

class SchedulerError(Exception):
    """Base exception for scheduler errors"""
    pass

class InvalidEmployeeData(SchedulerError):
    """Raised when employee data is invalid"""
    pass

@dataclass
class Employee:
    id: int
    name: str
    break_type: int
    skills: List[str]

class Scheduler:
    """
    Handles employee scheduling and shift management.
    
    Attributes:
        employees (List[Employee]): List of all employees
        shifts (Dict[str, List[str]]): Mapping of shifts to required roles
    """
    def __init__(self):
        self.employee_data = None
        self.schedule = None
        self.tasks = []

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

    def load_employee_data(self, file_path):
        self.employee_data = pd.read_csv(file_path)
        self.validate_employee_data()
        self.tasks = [col for col in self.employee_data.columns 
                     if col not in ['ID', 'Name', 'PreferredDayOff1', 
                                  'PreferredDayOff2', 'PreferredDayOff3', 
                                  'BreakType', 'Status', 'SkillRating', 
                                  'PreferredTask']]
        return self.tasks

    def generate_schedule(self, params):
        if self.employee_data is None:
            raise ValueError("Employee data not loaded.")

        try:
            # Initialize schedule DataFrame
            schedule_columns = ['Day', 'Shift', 'EmployeeID', 'EmployeeName', 'Role', 'StartTime', 'EndTime', 'Break']
            schedule = pd.DataFrame(columns=schedule_columns)

            # Get parameters
            total_hours = params['total_hours_per_week']
            work_days = params['work_days_per_week']
            opening_time = datetime.strptime(params['opening_time'], '%H:%M').time()
            closing_time = datetime.strptime(params['closing_time'], '%H:%M').time()

            # Define shifts
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            shifts = ['Morning', 'Afternoon']

            # Copy employee data to track hours
            employees = self.employee_data.copy()
            employees['RemainingHours'] = total_hours

            # Generate schedule for each day and shift
            for day in days[:work_days]:
                for shift in shifts:
                    # Set shift times
                    if shift == 'Morning':
                        start_time = opening_time
                        end_time = datetime.strptime('13:00', '%H:%M').time()
                    else:
                        start_time = datetime.strptime('13:00', '%H:%M').time()
                        end_time = closing_time

                    # For each task (Delivery, Vault, Register, Reception)
                    for task in self.tasks:
                        # Get available employees for this task
                        available = employees[
                            (employees[task] == True) & 
                            (employees['RemainingHours'] >= 4) &  # Minimum 4-hour shift
                            (~employees[f'PreferredDayOff{1}'].isin([day])) &
                            (~employees[f'PreferredDayOff{2}'].isin([day])) &
                            (~employees[f'PreferredDayOff{3}'].isin([day]))
                        ]

                        if not available.empty:
                            # Select employee (prioritize those with higher remaining hours)
                            employee = available.sort_values('RemainingHours', ascending=False).iloc[0]
                            
                            # Add to schedule
                            schedule = pd.concat([schedule, pd.DataFrame([{
                                'Day': day,
                                'Shift': shift,
                                'EmployeeID': employee['ID'],
                                'EmployeeName': employee['Name'],
                                'Role': task,
                                'StartTime': start_time.strftime('%H:%M'),
                                'EndTime': end_time.strftime('%H:%M'),
                                'Break': (datetime.combine(datetime.today(), start_time) + 
                                        timedelta(hours=2)).time().strftime('%H:%M')
                            }])], ignore_index=True)

                            # Update employee's remaining hours
                            shift_length = 4  # 4-hour shifts
                            employees.loc[employees['ID'] == employee['ID'], 'RemainingHours'] -= shift_length

            return schedule

        except Exception as e:
            print(f"Error generating schedule: {str(e)}")
            return None

    def save_schedule_to_excel(self, schedule, file_path):
        if schedule is None:
            raise ValueError("No schedule to export")
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'
        schedule.to_excel(file_path, index=False)

    def validate_employees(self) -> None:
        try:
            if self.employee_data['ID'].duplicated().any():
                raise InvalidEmployeeData(
                    "Duplicate employee IDs found. Please ensure each ID is unique."
                )
            # ... other validations ...
        except KeyError as e:
            raise InvalidEmployeeData(f"Missing required column: {e}")

    @lru_cache(maxsize=128)
    def get_available_employees(self, shift_time: datetime, role: str) -> List[Employee]:
        """Cache results of employee availability checks"""
        return [
            emp for emp in self.employees 
            if self.is_available(emp, shift_time) and role in emp.skills
        ]
