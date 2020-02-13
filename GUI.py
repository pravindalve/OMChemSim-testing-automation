import sys
import os
import distutils.spawn as spawn
from PyQt5 import QtGui, QtWidgets, QtCore
from time import sleep
from Simulator import Simulator
from Windows import HomeWindow, ReportWindow, SettingsWindow
import json


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, file_path=None):
        super(MainWindow, self).__init__()
        self.file_path = file_path
        self.data = {'name': "untitled", 'working_dir': None, 'simulator_path': None, 'file_list': None, 'csv_list': None}
        self.load_file()
        self.omc_path = self.get_omc_path()
        self.setWindowTitle("Test Automation - " + self.data['name'])
        self.setWindowIcon(QtGui.QIcon("Images/logo.png"))
        self.setGeometry(200, 100, 600, 600)

        self.simulator = None
        close = QtWidgets.QAction("&Close", self)
        close.setStatusTip("Close the Application")
        close.setShortcut("Ctrl+Q")
        close.triggered.connect(self.close)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(close)
        file_menu.addAction(close)

        simulate = QtWidgets.QAction(QtGui.QIcon("Images/simulate.png"), "Simulate", self)
        simulate.triggered.connect(self.simulate)

        stop_simulation = QtWidgets.QAction(QtGui.QIcon("Images/stop.png"), "Stop", self)
        stop_simulation.triggered.connect(self.stop_simulation)

        open_report = QtWidgets.QAction(QtGui.QIcon("Images/report.png"), "Report", self)
        open_report.triggered.connect(self.set_report_screen)

        save = QtWidgets.QAction(QtGui.QIcon("Images/save.png"), "Save File", self)
        save.triggered.connect(self.save_file)
        save.setShortcut("Ctrl+S")

        settings = QtWidgets.QAction(QtGui.QIcon("Images/settings.png"), "Settings", self)
        settings.triggered.connect(self.show_settings_window)

        back_to_home = QtWidgets.QAction(QtGui.QIcon("Images/home.png"), "Home", self)
        back_to_home.triggered.connect(self.set_home_screen)

        self.home_toolbar = self.addToolBar('Toolbar')
        self.home_toolbar.hide()
        self.home_toolbar.addAction(simulate)
        self.home_toolbar.addAction(stop_simulation)
        self.home_toolbar.addAction(open_report)
        self.home_toolbar.addAction(save)
        self.home_toolbar.addAction(settings)

        self.report_toolbar = self.addToolBar('Report_Toolbar')
        self.report_toolbar.hide()
        self.report_toolbar.addAction(back_to_home)

        self.homeWindow = HomeWindow(self.data['file_list'], self.data['csv_list'])
        self.reportWindow = ReportWindow()
        self.settingWindow = SettingsWindow(self.data['working_dir'], self.data['simulator_path'])
        self.settingWindow.OK_signal.connect(self.update_settings)
        self.statusBar()

        self.central_widget = QtWidgets.QStackedWidget()
        self.central_widget.addWidget(self.homeWindow)
        self.central_widget.addWidget(self.reportWindow)

        self.central_widget.setCurrentWidget(self.homeWindow)

        self.setCentralWidget(self.central_widget)

        self.set_home_screen()
        # self.set_report_screen()




    def closeEvent(self, *args, **kwargs):
        choice = QtWidgets.QMessageBox.question(self, "Close", "Close Test Automation?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            args[0].accept()
        else:
            args[0].ignore()

    def load_file(self):
        if self.file_path is not None:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            self.data['name'] = os.path.basename(self.file_path[:-4])
            self.data['working_dir'] = data["working_dir"]
            self.data['simulator_path'] = data["simulator_path"]
            self.data['file_list'] = data["file_list"]
            self.data['csv_list'] = data["csv_list"]

    def save_file(self):
        self.data['file_list'] = self.homeWindow.table.return_file_list()
        self.data['csv_list'] = self.homeWindow.table.return_csv_list()
        if os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=2)

    def update_settings(self):
        self.data['working_dir'] = self.settingWindow.working_dir
        self.data['simulator_path'] = self.settingWindow.simulator_path

    def set_home_screen(self):
        self.report_toolbar.hide()
        self.home_toolbar.show()
        self.central_widget.setCurrentWidget(self.homeWindow)
        self.show()

    def set_report_screen(self):
        self.home_toolbar.hide()
        self.report_toolbar.show()
        self.central_widget.setCurrentWidget(self.reportWindow)
        self.reportWindow.load_report((self.data['working_dir'] + '/' + self.data['name'] + '/Report/Report.pdf'))
        self.show()

    def show_settings_window(self):
        self.settingWindow.show()

    @staticmethod
    def get_omc_path():
        try:
            omhome = os.environ.get('OPENMODELICAHOME')
            if omhome is None:
                omhome = os.path.split(os.path.split(os.path.realpath(spawn.find_executable("omc")))[0])[0]
            elif os.path.exists('/opt/local/bin/omc'):
                omhome = '/opt/local'
            return os.path.join(omhome, 'bin', 'omc')

        except BaseException:
            print("The OpenModelica compiler is missing in the System path please install it")
            raise

    def simulate(self):
        self.data['file_list'] = self.homeWindow.table.return_file_list()
        self.data['csv_list'] = self.homeWindow.table.return_csv_list()
        print(self.data['file_list'], self.data['csv_list'])
        sim_path = os.path.join(self.data['working_dir'], self.data['name'])
        if not os.path.exists(sim_path):
            os.mkdir(sim_path)
        # run_simulation(file_list, csv_list)
        self.simulator = Simulator(self.data['name'], self.omc_path, self.data['working_dir'], self.data['simulator_path'], self.data['file_list'], self.data['csv_list'])
        self.simulator.start()


    def stop_simulation(self):
        for sim in self.simulator.sims:
            if sim.process is not None:
                sim.process.terminate()
                sim.process = None
        self.simulator.exit()
        self.simulator = None
        print('Stopped!!!')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    GUI = MainWindow('testfile.tst')
    print(GUI.data)
    sys.exit(app.exec_())
