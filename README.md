# Employee Scheduler

A Python-based employee scheduling application that helps managers create and manage work schedules efficiently.

## Features

- Load employee data from CSV files
- Generate schedules based on:
  - Employee availability
  - Preferred days off
  - Break types
  - Skills and roles
- Export schedules to Excel
- GUI interface for easy interaction

## Requirements

- Python 3.8+
- PyQt5
- pandas
- numpy
- openpyxl

## Installation 


## Usage

1. Start the application:
python main.py


2. Use the GUI to:
   - Upload employee data (CSV format)
   - Set scheduling parameters:
     - Total hours per week
     - Work days per week
     - Opening/closing times
   - Generate schedules
   - Export to Excel

## Data Format

The employee CSV file should include the following columns:
- ID (unique identifier)
- Name
- Skills columns (boolean):
  - Delivery
  - Vault
  - Register
  - Reception
- PreferredDayOff1
- PreferredDayOff2
- PreferredDayOff3
- BreakType (1 or 2)
- Status
- SkillRating (1-3)
- PreferredTask

Example CSV format:
ID,Name,Delivery,Vault,Register,Reception,PreferredDayOff1,PreferredDayOff2,PreferredDayOff3,BreakType,Status,SkillRating,PreferredTask
1,John Doe,True,True,True,True,Monday,Tuesday,Friday,1,1,3,Delivery


## Break Types

- Type 1: One 45-minute break and one 15-minute break
- Type 2: One 30-minute break and two 15-minute breaks

## Project Structure
employee_scheduler/
├── main.py # Application entry point
├── gui.py # GUI implementation
├── scheduler.py # Core scheduling logic
├── constants.py # Configuration constants
├── logger.py # Logging setup
├── requirements.txt # Project dependencies
├── data/ # Data directory
│ └── employees.csv
└── tests/ # Test files
└── test_scheduler.py


## Development

To run tests:
bash
pytest


## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Authors

- capawawa

## Acknowledgments

- PyQt5 for the GUI framework
- pandas for data handling
- numpy for numerical operations