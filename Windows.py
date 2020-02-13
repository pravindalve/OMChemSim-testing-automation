from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWebEngineWidgets
import os


class Table(QtWidgets.QTableWidget):

    def __init__(self, file_list, csv_list):
        super().__init__()
        self.file_list = file_list
        self.csv_list = csv_list
        self.setColumnCount(2)
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 300)
        if self.file_list is None:
            self.setRowCount(10)
        elif len(self.file_list) < 10:
            self.setRowCount(10)
        else:
            self.setRowCount(len(self.file_list))

        if self.file_list is not None and self.csv_list is not None:
            self.update_table()



    def return_file_list(self):
        lis = []
        for i in range(self.rowCount()):
            if self.item(i, 0) is not None:
                lis.append(self.item(i, 0).text())

        return lis

    def return_csv_list(self):
        lis = []
        for i in range(self.rowCount()):
            if self.item(i, 1) is not None:
                lis.append(self.item(i, 1).text())

        return lis

    def update_table(self):
        for i in range(len(self.file_list)):
            self.setItem(i, 0, QtWidgets.QTableWidgetItem(self.file_list[i]))
            self.setItem(i, 1, QtWidgets.QTableWidgetItem(self.csv_list[i]))


class HomeWindow(QtWidgets.QWidget):

    def __init__(self, file_list, csv_list):
        super(HomeWindow, self).__init__()
        self.table = Table(file_list, csv_list)
        self.table.setHorizontalHeaderLabels(("File Name;Expected Result .csv File").split(";"))

        self.addRowButton = QtWidgets.QPushButton()
        self.addRowButton.setIcon(QtGui.QIcon("Images/add.png"))
        self.deleteRowButton = QtWidgets.QPushButton()
        self.deleteRowButton.setIcon(QtGui.QIcon("Images/remove.png"))

        self.addRowButton.clicked.connect(lambda: self.table.insertRow(self.table.rowCount()))
        self.deleteRowButton.clicked.connect(lambda: self.table.removeRow(self.table.rowCount() - 1))

        self.buttonBox = QtWidgets.QWidget()
        buttonBoxLayout = QtWidgets.QVBoxLayout()
        buttonBoxLayout.addWidget(self.addRowButton)
        buttonBoxLayout.addWidget(self.deleteRowButton)
        self.buttonBox.setLayout(buttonBoxLayout)

        homeWindowLayout = QtWidgets.QHBoxLayout()
        homeWindowLayout.addWidget(self.buttonBox)
        homeWindowLayout.addWidget(self.table)
        self.setLayout(homeWindowLayout)


class ReportWindow(QtWebEngineWidgets.QWebEngineView):

        def __init__(self):
            super().__init__()
            self.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)

        def load_report(self, url):
            self.load(QtCore.QUrl(url))


class SettingsWindow(QtWidgets.QWidget):
    OK_signal = QtCore.pyqtSignal()

    def __init__(self, working_dir, simulator_path):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 600, 100)
        self.working_dir = working_dir
        self.simulator_path = simulator_path

        self.working_dir_box = QtWidgets.QLineEdit()
        self.working_dir_box.setText(self.working_dir)
        self.working_dir_box.textChanged.connect(self.update_working_dir)

        self.simulator_path_box = QtWidgets.QLineEdit()
        self.simulator_path_box.setText(self.simulator_path)
        self.simulator_path_box.textChanged.connect(self.update_simulator_path)

        self.OK_button = QtWidgets.QPushButton("OK")
        self.OK_button.clicked.connect(self.OK)

        self.Cancel_button = QtWidgets.QPushButton("Cancel")
        self.Cancel_button.clicked.connect(self.Cancel)




        flo = QtWidgets.QFormLayout()
        flo.addRow('Working Directory', self.working_dir_box)
        flo.addRow('Simulator Path', self.simulator_path_box)

        flo.addRow(self.OK_button, self.Cancel_button)

        self.setLayout(flo)


    def OK(self):
        self.OK_signal.emit()
        self.update_working_dir()
        self.update_simulator_path()
        self.close()
        print(self.OK_signal.emit())
        print(self.working_dir)
        print(self.simulator_path)

    def Cancel(self):
        self.close()

    def update_working_dir(self):
        self.working_dir = self.clean_path(self.working_dir_box.text())

    def update_simulator_path(self):
        self.simulator_path = self.clean_path(self.simulator_path_box.text())

    @staticmethod
    def clean_path(path):
        while '\\' in path:
            path = path.replace('\\', '/')
        return path
