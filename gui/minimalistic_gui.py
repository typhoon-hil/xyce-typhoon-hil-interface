# Built-in #
import traceback, sys, os, re, io, time
from subprocess import Popen, PIPE
import subprocess
from functools import partial

# Add submodules folder to path
sys.path.append('gui')
sys.path.append('schematic_converter')

# My modules #
import tse2xyce

# PyQt #
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd
import numpy as np

# Show tracebacks #
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook

# Function definitions #
def available_variables(csv_file, cir_file):
    ''' Uses the last line of the .cir file to determine available
        variables and changes the headers of the CSV accordingly. '''

    try:
        with open(csv_file) as f_csv:
            table = pd.read_csv(f_csv)
            with open(cir_file) as f_cir:
                # Original table header may include extra commas due to
                # differential voltage measurements V(v+,v-)
                new_tab =  table.dropna(axis=1) # Drops empty columns
                for col in new_tab.columns:
                    if "Re(" in col:
                        print(col)
                # Sets the new header
                last_line = f_cir.readlines()[-1].replace('\n','')
                cols = ['Time']
                cols.extend(last_line.split(",")[1:])
                try:
                    new_tab.columns = cols
                    new_tab.to_csv(csv_file, index=False)
                except ValueError:
                    print(error)
                    # Length mismatch
                    pass
    except FileNotFoundError:
        print("error")
        pass


# Widget definition
class Ui_XyceOutput(object):
    def setupUi(self, XyceOutput):
        XyceOutput.setObjectName("XyceOutput")
        XyceOutput.resize(600, 600)
        XyceOutput.setMinimumSize(QtCore.QSize(400, 400))
        XyceOutput.setLayoutDirection(QtCore.Qt.LeftToRight)
        XyceOutput.setModal(False)
        self.gridLayout = QtWidgets.QGridLayout(XyceOutput)
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser = QtWidgets.QTextBrowser(XyceOutput)
        self.textBrowser.setMinimumSize(QtCore.QSize(350, 350))
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 3)
        self.abortButton = QtWidgets.QPushButton('Abort', XyceOutput)
        self.abortButton.setToolTip('Abort the simulation.')
        self.gridLayout.addWidget(self.abortButton, 1, 2, 1, 1)

        self.retranslateUi(XyceOutput)
        QtCore.QMetaObject.connectSlotsByName(XyceOutput)

    def retranslateUi(self, XyceOutput):
        _translate = QtCore.QCoreApplication.translate
        XyceOutput.setWindowTitle(_translate("XyceOutput", "Xyce output"))


class XyceOutput(QDialog, Ui_XyceOutput):

    closed_window = QtCore.pyqtSignal()

    def __init__(self, json_file_path, sim_params_dict):
        super().__init__()
        # Set up the user interface generated with Qt Designer.
        self.setupUi(self)
        self.setModal(False)
        self.closed_window.connect(self.on_close_window)

        self.textBrowser.append('Loading the Xyce .cir file...')
        # QProcess used later to run Xyce and display output inside the window
        self.process = QtCore.QProcess(self)
        self.plotprocess = QtCore.QProcess(self)
        # Abort button
        self.abortButton.clicked.connect(self.abort_sim)
        # QProcess emits 'readyRead' signal when there is readable data
        self.process.readyRead.connect(self.read_ready)
        self.process.finished.connect(self.proc_finished)
        # keep_printing is a flag for filtering the text window output
        self.keep_printing = False
        self.sim_params_dict = sim_params_dict
        self.json_file_path = json_file_path
        self.textBrowser.append('Path to file is ' + self.json_file_path)

        sys.path.append('schematic_converter')

        if self.convert_JSON_file():
            self.simulate()

    def closeEvent(self, event):
        self.closed_window.emit()
        QtWidgets.QWidget.closeEvent(self, event)

    def convert_JSON_file(self):
        try:
            # Converts the JSON file to a Xyce .cir file using tse2xyce.py
            tse2xyce.tse2xyce(self.json_file_path, self.sim_params_dict)
            # The Xyce file path is set by substituting the file extension
            self.xyce_file_path = re.sub(  r"\.json",r".cir",
                                                self.json_file_path)
            return True
        except:
            self.textBrowser.setPlainText('''<body><h2 style='color:red;'>
                                            Error when trying to convert the
                                             circuit to Xyce syntax.</h2>
                                             </body>''')
            return False

    def test_xyce_file(self):
        # Binary encoding needed to send the commands
        commands = f'''xyce -syntax "{self.xyce_file_path}"'''#.encode('utf-8')
        # Quickly tests the syntax with Xyce (-syntax)
        p = Popen(commands, stdin=PIPE, stdout=PIPE, shell=True)
        # Run the command line and read the output
        out, err = p.communicate("")

        try:
            out = out.decode('utf-8')
        except UnicodeDecodeError:
            out = out.decode('latin-1')
        # In case Xyce validates the syntax, display the part of the output
        # that includes topology information.
        b = re.match(r"([\S\s]*)(\*{5} Reading)([\S\s]*)(\*{5} Total Ela)",
                    out)
        if b == None:
            self.textBrowser.setPlainText('''<body><h2 style='color:red;'>
                                            The generated Xyce netlist file is
                                            invalid.</h2></body>'''"")
            self.textBrowser.append(out)

    # Writes the Xyce output to the text window
    def read_ready(self):
        # Supports two encondings as of now
        try:
            currenttext = str(self.process.readAllStandardOutput(), 'utf-8')
        except UnicodeDecodeError:
            currenttext = str(self.process.readAllStandardOutput(), 'iso8859-1')
        # Print only Xyce stdout
        if "Welcome to" in currenttext:
            self.keep_printing = True
        if self.keep_printing == True:
            # if the end of Xyce output was detected
            if ("XyceSim>More") in currenttext:
                self.keep_printing = False
                self.textBrowser.append('\n'.join(currenttext.split('\n')[1:-1]))
            else:
                # Append the new text available from the process output
                self.textBrowser.append(currenttext)


    def proc_finished(self):

        if self.process.exitCode() == 0:
            if not "Xyce Abort" in self.textBrowser.toPlainText():
                self.plot_data_path = "xyce_out.csv" if self.sim_params_dict["analysis_type"] == "Transient" else "xyce_f_out.csv"

                available_variables(self.plot_data_path,
                                    self.xyce_file_path)
                self.textBrowser.append("""<body>
                    <h2 style='color:green;'>Simulation finished successfully.</h2>
                    </body>""")
                if any(err_str in self.textBrowser.toPlainText() for err_str in ["step too small", "Maximum number of local error test failures"]):
                    self.textBrowser.append("""<body>
                        <h2 style='color:red;'>Simulation aborted due to convergence errors.</h2>
                        </body>""")
                self.plot_data()
            else:
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>Simulation ended with errors.</h2>
                    </body>""")
        # When Qt kills a process, this is the returned exitCode
        # Runs when the Abort button is clicked
        elif self.process.exitCode() == 62097:
            self.plot_data_path = "xyce_out.csv"
            available_variables(self.plot_data_path,
                                self.xyce_file_path)
            self.textBrowser.append("""<body>
                <h2 style='color:orange;'>Simulation aborted by the user.</h2>
                </body>""")
            self.plot_data()
        elif self.process.exitCode() == 1:
            if "step too small" in self.textBrowser.toPlainText():
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>Simulation aborted due to convergence errors.</h2>
                    </body>""")
                self.plot_data_path = "xyce_out.csv"
                available_variables(self.plot_data_path,
                                    self.xyce_file_path)
                self.plot_data()
            else:
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>Simulation ended with errors.</h2>
                    </body>""")
        else:
            self.textBrowser.append("""<body>
                <h2 style='color:red;'>The Xyce Simulator process was terminated.</h2>
                </body>""")

    def on_close_window(self):
        self.process.kill()

    def simulate(self):
        ''' Start the Xyce simulation. '''
        self.textBrowser.clear()

        # Simulation parameters (time step, total simulation time)
        # Currently simulates with fixed time step
        if "\\" in self.xyce_file_path:
            self.cir_folder = "/".join(self.xyce_file_path.split("\\")[0:-1])
        else:
            self.cir_folder = "/".join(self.xyce_file_path.split("/")[0:-1])
        self.params_path = self.cir_folder + "/xyce_params.t"
        # Write the parameters to a file
        if self.sim_params_dict['analysis_type'] == "Transient":
            with open(self.params_path,"w") as f:
                f.writelines([  f"t_step = {self.sim_params_dict['max_ts']}\n",
                                f"total_time = {self.sim_params_dict['sim_time']}\n"
                                f"decimation = {float(self.sim_params_dict['max_ts'])}\n"])
        # Xyce simulation command
        command = f'xyce -prf "{self.params_path}" "{self.xyce_file_path}"\n'
        # Start the Xyce process
        self.process.start(command)

    def abort_sim(self):
        self.process.kill()

    def plot_data(self):
        self.textBrowser.append("""<body>
            <h2 style='color:green;'>Opening the Signal Analyzer tool...</h2>
            </body>""")
        # Starts windows command prompt in the THCC drive, otherwise the typhoon_hil.cmd
        # batch can result in errors.
        filename = "xyce_out" if self.sim_params_dict['analysis_type'] == "Transient" else "xyce_f_out"
        try:
            thcc_folder = os.environ["TYPHOONPATH"]
            self.plotprocess.startDetached(f'cmd /c pushd "{thcc_folder[:2]}" & typhoon_hil sa --data_file "{os.getcwd()}\\{filename}.csv"')
        except KeyError:
            self.plotprocess.startDetached(f'cmd /c pushd "C:" & typhoon_hil sa --data_file "{os.getcwd()}\\{filename}.csv"')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sim_params = {'analysis_type':'Transient','max_ts':'1e-4','sim_time':'0.5ms'}
    # sim_params = {'analysis_type':'AC small-signal','start_f':'10','end_f':'100000', 'num_points':'1000'}
    mainwindow = XyceOutput(r"path_to.json", sim_params)
    mainwindow.show()
    sys.exit(app.exec_())
