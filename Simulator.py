import os
import glob
import subprocess
from subprocess import PIPE
import distutils.spawn as spawn
from simulation import Simulation
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyQt5 import QtCore


class Simulator(QtCore.QThread):

    def __init__(self, name, omc_path, working_dir, simulator_path, sim_files, comp_csv_files):
        super().__init__()
        self.name = name
        self.omc_path = omc_path
        self.working_dir = os.path.join(working_dir, name)
        self.simulator_path = simulator_path
        self.sim_files = sim_files
        self.comp_csv_files = comp_csv_files
        self.sim_dir = os.path.join(self.working_dir,'Simulation_Files')
        self.res_dir = os.path.join(self.working_dir,'Result_Files')
        self.report_dir = os.path.join(self.working_dir, 'Report')
        self.prepare_working_dir()
        self.sims = self.create_simulations()

    def run(self):
        self.run_simulation()

    def prepare_working_dir(self):
        self.clear_dir(self.working_dir)
        os.mkdir(self.sim_dir)
        os.mkdir(self.res_dir)
        os.mkdir(self.report_dir)

    def create_simulations(self):
        sims = []
        print(self.omc_path, self.omc_path, self.simulator_path, self.sim_files,
              self.comp_csv_files, self.sim_dir, self.res_dir)
        for i in range(len(self.sim_files)):
            if self.sim_files is not None:
                obj = Simulation(str(i), self.omc_path, self.simulator_path, self.sim_files[i],
                             self.comp_csv_files[i], self.sim_dir, self.res_dir)
                sims.append(obj)
        return sims

    @staticmethod
    def clear_dir(path):
        folders = glob.glob(os.path.join(path, '*'))
        for f in folders:
            shutil.rmtree(f)

    @staticmethod
    def write_title(c, y, title):
        c.setFont('Helvetica-Bold', 12)
        if y <= 100:
            y = 750
            c.showPage()
            c.setFont('Helvetica-Bold', 12)
        c.drawString(30, y, title)
        return y - 30

    @staticmethod
    def write_text(c, y, text_file):
        c.setFont('Helvetica', 12)

        with open(text_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                if y <= 0:
                    y = 750
                    c.showPage()
                    c.setFont('Helvetica', 12)
                c.drawString(50, y, line)
                y -= 30
        y -= 30
        return y

    def generate_report(self):
        c = canvas.Canvas(self.report_dir + '/Report.pdf', pagesize=letter)
        width, height = letter
        c.setFont('Helvetica-Bold', 30)
        c.drawCentredString(width/2, 730, "Test Report")
        c.line(20, 700, 592, 700)
        y = 670
        for sim in self.sims:
            y = self.write_title(c, y, sim.file_name)
            y = self.write_text(c, y, sim.report)
        c.save()

    def run_simulation(self):
        #initialization
        # sim_files = ["Simulator.Test.msTP", "Simulator.Test.msPH", "Simulator.Test.heater1.heat"]
        # comp_csv_files = ["C:/Users/FOSSEE/Desktop/working_dir/Temp/python/comp_csv/Simulator.Test.msTP_res.csv",
        #                   "C:/Users/FOSSEE/Desktop/working_dir/Temp/python/comp_csv/Simulator.Test.msTP_res.csv",
        #                   "C:/Users/FOSSEE/Desktop/working_dir/Temp/python/comp_csv/Simulator.Test.heater1.heat_res.csv"]
        # working_dir = "C:/Users/FOSSEE/Desktop/working_dir/Temp/python/tempfiles"
        # simulator_path = "C:/Users/FOSSEE/Documents/GitHub/OMChemSim/Simulator/package.mo"

        #making simulation environment

        print(self.sims)
        for sim in self.sims:
            sim.run_simulation()
        print("Test run is completed!!!")
        self.generate_report()

