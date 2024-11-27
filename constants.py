from enum import Enum

class BreakType(Enum):
    SHORT = 1
    LONG = 2

class SchedulerConfig:
    MIN_SHIFT_LENGTH = 4  # hours
    MAX_SHIFT_LENGTH = 12 # hours
    MIN_BREAK_LENGTH = 30 # minutes
    MAX_EMPLOYEES_PER_SHIFT = 10
    REQUIRED_ROLES = ['Cashier', 'Manager', 'Stock'] 