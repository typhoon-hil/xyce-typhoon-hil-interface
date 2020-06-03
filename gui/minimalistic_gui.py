# cd "D:\Dropbox\Typhoon HIL\Repository\XyceSim"
# cd "C:\users\marcos\dropbox\Typhoon HIL\Repository\XyceSim"
# cd "D:\Dropbox\Typhoon HIL\Repository\XyceSim\schematic_converter\model_libs\Qt"
# pyuic5 -o main_gui.py main_gui.ui
# pyuic5 -o plotscreen_gui.py plotscreen_gui.ui
# pyuic5 -o dynamic_spice_component.py dynamic_spice_component.ui

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

    with open(csv_file) as f_csv:
        table = pd.read_csv(f_csv)
        with open(cir_file) as f_cir:
            # Original table header may include extra commas due to
            # differential voltage measurements V(v+,v-)
            new_tab =  table.dropna(axis=1) # Drops empty columns
            # Sets the new header
            last_line = f_cir.readlines()[-1].replace('\n','')
            cols = ['Time']
            cols.extend(last_line.split(",")[1:])
            new_tab.columns = cols
            new_tab.to_csv(csv_file, index=False)
            #new_tab.to_hdf(csv_file.split('.')[0]+'.h5', 'data', mode='w', format='table')


        return list(new_tab)[1:] # Doesn't return the *TIME column


# Widget definition
class Ui_XyceOutput(object):
    def setupUi(self, XyceOutput):
        XyceOutput.setObjectName("XyceOutput")
        XyceOutput.resize(619, 613)
        XyceOutput.setMinimumSize(QtCore.QSize(575, 586))
        XyceOutput.setLayoutDirection(QtCore.Qt.LeftToRight)
        XyceOutput.setModal(False)
        self.gridLayout = QtWidgets.QGridLayout(XyceOutput)
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser = QtWidgets.QTextBrowser(XyceOutput)
        self.textBrowser.setMinimumSize(QtCore.QSize(351, 291))
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 1)

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
        self.closed_window.connect(self.on_close_window)

        self.textBrowser.append('Loading the Xyce .cir file...')
        # QProcess used later to run Xyce and display output inside the window
        self.process = QtCore.QProcess(self)
        self.plotprocess = QtCore.QProcess(self)
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
            tse2xyce.tse2xyce(self.json_file_path)
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
                #self.textBrowser.verticalScrollBar.setValue(maximum())
            else:
                # Append the new text available from the process output
                self.textBrowser.append(currenttext)


    def proc_finished(self):
        # Reset Start Simulation button when Xyce has finished or was canceled
        if self.process.exitCode() == 0:
            self.plot_data_path = "xyce_out.csv"
            available_variables(self.plot_data_path,
                                self.xyce_file_path)
            if not "Xyce Abort" in self.textBrowser.toPlainText():
                self.textBrowser.append("""<body>
                    <h2 style='color:green;'>Simulation finished successfully.<br>
                    Opening the Signal Analyzer tool...</h2>
                    </body>""")
                if "too small on" in self.textBrowser.toPlainText():
                    self.textBrowser.append("""<body>
                        <h2 style='color:red;'>Simulation ended with errors.</h2>
                        </body>""")
                self.plot_data()
            else:
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>Simulation ended with errors.</h2>
                    </body>""")
        else:
            self.textBrowser.append("""<body>
                <h2 style='color:red;'>Simulation ended with errors.</h2>
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
        with open(self.params_path,"w") as f:
            f.writelines([  f"t_step = {self.sim_params_dict['max_ts']}\n",
                            f"total_time = {self.sim_params_dict['sim_time']}\n"
                            f"decimation = {float(self.sim_params_dict['max_ts'])}\n"])
        # Xyce simulation command
        command = f'xyce -prf "{self.params_path}" "{self.xyce_file_path}"\n'
        print(command)
        # Start the process by entering the Cygwin environment
        self.process.start('cmd')

        # Xyce simulation command
        self.process.write((command+"quit").encode('utf-8'))
        # Close the write channel and send the written lines
        self.process.closeWriteChannel()
        #self.pushButton_start_sim.setText("Stop Simulation")


    def plot_data(self):

        command = f'typhoon_hil.cmd sa --data_file "{os.getcwd()}\\xyce_out.csv"'
        self.plotprocess.startDetached(command)


if __name__ == "__main__":
    print(sys.version)
    app = QApplication(sys.argv)
    sim_params = {'max_ts':'1e-9','sim_time':'0.4ms'}
    mainwindow = XyceOutput(r"C:\Dropbox\Typhoon HIL\Ideas\TSE2Xyce\Toronto Uni\dual_active_bridge Target files\dual_active_bridge.json", sim_params)
    mainwindow.show()
    sys.exit(app.exec_())
