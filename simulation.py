import os
import subprocess
from subprocess import PIPE
from shutil import copy
import glob
import csv


class Simulation:
    def __init__(self, name, omc_path, simulator_path, file_name, comp_csv, sim_dir, res_dir):
        self.name = name
        self.omc_path = omc_path
        self.simulator_path = simulator_path
        self.file_name = file_name
        self.comp_csv = comp_csv
        self.sim_dir = sim_dir
        self.my_res_dir = res_dir
        self.result_csv = None
        self.process = None
        self.my_sim_dir = self.create_my_sim_dir()
        self.my_mos = self.create_mos()
        self.report = self.prepare_report()

    def create_my_sim_dir(self):
        m = os.path.join(self.sim_dir, self.name)
        while "\\" in m:
            m = m.replace('\\', '/')
        os.mkdir(m)
        return m

    def create_mos(self):
        my_mos = os.path.join(self.my_sim_dir, (self.name + '.mos'))
        with open(my_mos, "w") as mos_file:
            mos_file.write('cd("' + self.my_sim_dir + '");\n')
            mos_file.write('loadModel(Modelica);\n')
            mos_file.write('loadFile("' + self.simulator_path + '");\n')
            mos_file.write('simulate(' + self.file_name + ', outputFormat="csv", stopTime=1.0, numberOfIntervals=1);\n')
        return my_mos

    def run_simulation(self):
        print(self.file_name + " is running...")
        self.process = subprocess.Popen([self.omc_path, '-s', self.my_mos], stdout=PIPE, stderr=PIPE)
        # self.process.wait()
        output, err = self.process.communicate()
        print(output, err)
        res_csv = glob.glob(self.my_sim_dir + '/*.csv')
        print(self.my_sim_dir + '/*.csv')
        print(res_csv)
        for file in res_csv:
            copy(file, self.my_res_dir)
            self.result_csv = self.my_res_dir + '/' + self.file_name + '_res.csv'
        print(self.result_csv)
        self.report = self.prepare_report()


    def compare_csv(self):
        report_lines = []
        if self.result_csv is None:
            report_lines.append(self.file_name + ' is not simulated!!!\n')
        else:
            with open(self.result_csv, 'r') as result_file:
                with open(self.comp_csv, 'r') as comp_file:
                    result = list(csv.reader(result_file))
                    compare = list(csv.reader(comp_file))
                    ok_count = 0
                    for res_var in result[0]:
                        for comp_var in compare[0]:
                            if res_var == comp_var:
                                a = float(result[1][result[0].index(res_var)])
                                b = float(compare[1][compare[0].index(comp_var)])
                                if (a - b) != 0:
                                    try:
                                        report_lines.append(str((abs(a - b) / a) * 100) + '% error for ' + res_var + '\n')
                                        print(str((abs(a - b) / a) * 100) + '% error for ' + res_var)
                                    except ZeroDivisionError:
                                        report_lines.append(str(abs(a - b)) + ' difference coming for ' + res_var + '\n')

                                else:
                                    ok_count += 1
                                    print(res_var + " is matching perfectly")

                    if ok_count == len(compare[0]):
                        report_lines.append('All variables matched perfectly :)')
        return report_lines

    def prepare_report(self):
        report_dir = self.my_sim_dir + '/report.txt'
        lines = self.compare_csv()
        with open(report_dir, 'w') as report:
            for line in lines:
                report.write(line)
        return report_dir
