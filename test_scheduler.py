import pytest
from datetime import datetime
from scheduler import (
    Scheduler, 
    Employee, 
    SchedulerError, 
    InvalidEmployeeData
)

def test_employee_validation():
    with pytest.raises(InvalidEmployeeData):
        employees = [
            Employee(id=1, name="John", break_type=1, skills=["Cashier"]),
            Employee(id=1, name="Jane", break_type=1, skills=["Manager"])
        ]
        Scheduler(employees)

def test_schedule_generation():
    employees = [
        Employee(id=1, name="John", break_type=1, skills=["Cashier"]),
        Employee(id=2, name="Jane", break_type=2, skills=["Manager"])
    ]
    scheduler = Scheduler(employees)
    schedule = scheduler.generate_schedule()
    assert len(schedule) > 0 