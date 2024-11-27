import sys
from PyQt5.QtWidgets import QApplication
from scheduler import Scheduler
from gui import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scheduler = Scheduler()
    mainWindow = MainWindow(scheduler)
    mainWindow.show()
    sys.exit(app.exec_())
