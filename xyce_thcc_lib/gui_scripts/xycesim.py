# Built-in #
import traceback, sys, os, re, pathlib, json
from subprocess import Popen, PIPE
from io import StringIO
import pathlib

if not __name__ == "__main__":
    from .temp_log_plot import PlotWindow

from tse_to_xyce.tse2tpt_base_converter import tse2tpt
import importlib
import tse_to_xyce

# PyQt #
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd

# Show tracebacks #
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook


# Function definitions #
def available_variables(csv_file, cir_file):
    """ Uses the last line of the .cir file to determine available
        variables and changes the headers of the CSV accordingly. """

    try:
        # Get measurement new names
        data_path = os.path.join(os.path.dirname(cir_file), "data")
        meas_names_file_path = os.path.join(data_path, "measurement_names.json")
        with open(meas_names_file_path, "r") as f:
            measurement_names_dict = json.load(f)

        csv_io = StringIO()
        with open(csv_file) as f_csv:
            # Rename the first line (headers) according to the JSON file
            first_line = f_csv.readline()
            new_names = measurement_names_dict.get("new_names")
            old_names = measurement_names_dict.get("old_names")
            for idx, old_name in enumerate(old_names):
                first_line = first_line.replace(old_name, new_names[idx], 1)
            print(first_line)
            print(first_line, file=csv_io)
            # Save the rest of the lines to the text stream
            next_lines = f_csv.readlines()
            for line in next_lines:
                print(line, file=csv_io)

            csv_io.seek(0)  # Return to the first line
            table = pd.read_csv(csv_io)
            print(table)
            with open(cir_file) as f_cir:
                # Drops empty columns
                new_tab = table.dropna(axis=1)
                # Rename TIME to Time (mandatory for the Signal Analyzer)
                new_tab = new_tab.rename(columns={"TIME": "Time"})
                new_tab = new_tab.rename(columns={"FREQ": "Time"})
                try:
                    new_tab.to_csv(csv_file, index=False)
                except ValueError:
                    # Length mismatch
                    pass
                return True
    except FileNotFoundError:
        return False


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

    def __init__(self, mdl, json_file_path, sim_params_dict, xyce_simulator_path):
        super().__init__()
        self.mdl = mdl
        # Set up the user interface generated with Qt Designer.
        self.setupUi(self)
        self.setModal(False)
        self.closed_window.connect(self.on_close_window)
        self.xyce_file_path = ""
        self.xyce_simulator_path = xyce_simulator_path

        self.textBrowser.append('Preparing the JSON file for conversion...')
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

        if self.convert_JSON_file():
            self.simulate()

    def closeEvent(self, event):
        self.closed_window.emit()
        QtWidgets.QWidget.closeEvent(self, event)

    def convert_JSON_file(self):
        try:
            # Converts the JSON file to a Xyce .cir file
            import tse_to_xyce.conversion.convert as conv
            # importlib.reload(conv)

            [conv_successful, msg] = tse2tpt.start_conversion(self.json_file_path, tse_to_xyce, self.sim_params_dict)

            # The Xyce file path is set by substituting the file extension
            if conv_successful:
                name_stem = pathlib.Path(self.json_file_path).stem
                self.xyce_file_path = str(pathlib.Path(self.json_file_path).parent.joinpath("xyce",
                                                                                            f"{name_stem}_master.cir"))
                self.textBrowser.append(f'{msg}')
            else:
                self.textBrowser.append(f"<body><h2 style='color:red;'>Simulation aborted.</h2></body>{msg}<br>")
            return conv_successful

        except Exception as e:
            self.textBrowser.append('''<body><h2 style='color:red;'>
                                            Error when trying to convert the
                                             circuit to Xyce syntax.</h2>
                                             </body>''')
            self.textBrowser.append(f'Debug information:<br>{type(e).__name__}: {e}')
            print(e.with_traceback(e))
            return False

    def test_xyce_file(self):
        # Binary encoding needed to send the commands
        commands = f'''{str(self.xyce_simulator_path)} -syntax "{self.xyce_file_path}"'''  # .encode('utf-8')
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
                                            invalid.</h2></body>''')
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
        if self.keep_printing:
            # if the end of Xyce output was detected
            if "XyceSim>More" in currenttext:
                self.keep_printing = False
                self.textBrowser.append('\n'.join(currenttext.split('\n')[1:-1]))
            else:
                # Append the new text available from the process output
                self.textBrowser.append(currenttext)

    def proc_finished(self):

        if self.process.exitCode() == 0:
            if not "Xyce Abort" in self.textBrowser.toPlainText():
                self.plot_data_path = "xyce_out.csv" if self.sim_params_dict[
                                                            "analysis_type"] == "Transient" else "xyce_f_out.csv"

                csv_ok = available_variables(self.plot_data_path,
                                             self.xyce_file_path)
                if csv_ok:
                    self.textBrowser.append("""<body>
                        <h2 style='color:green;'>Simulation finished successfully.</h2>
                        </body>""")
                    if any(err_str in self.textBrowser.toPlainText() for err_str in
                           ["step too small", "Maximum number of local error test failures"]):
                        self.textBrowser.append("""<body>
                            <h2 style='color:red;'>Simulation aborted due to convergence errors.</h2>
                            </body>""")
                    self.plot_data()
                else:
                    self.textBrowser.append("""<body>
                        <h2 style='color:red;'>There was a problem with measurement data.</h2>
                        </body>""")
            else:
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>Simulation ended with errors.</h2>
                    </body>""")
                self.textBrowser.append("""Please make sure the "xyce" command is being recognized in a command prompt
window, and that Typhoon HIL Control Center was restarted after adding Xyce to the system PATH.""")
        # When Qt kills a process, this is the returned exitCode
        # Runs when the Abort button is clicked
        elif self.process.exitCode() == 62097:
            self.plot_data_path = "xyce_out.csv"
            csv_ok = available_variables(self.plot_data_path,
                                         self.xyce_file_path)
            if csv_ok:
                self.textBrowser.append("""<body>
                    <h2 style='color:orange;'>Simulation aborted by the user.</h2>
                    </body>""")
            else:
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>There was a problem with measurement data.</h2>
                    </body>""")
        elif self.process.exitCode() == 1:
            if "step too small" in self.textBrowser.toPlainText():
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>Simulation aborted due to convergence errors.</h2>
                    </body>""")
                self.plot_data_path = "xyce_out.csv"
                csv_ok = available_variables(self.plot_data_path,
                                             self.xyce_file_path)
                if csv_ok:
                    self.plot_data()
                else:
                    self.textBrowser.append("""<body>
                        <h2 style='color:red;'>There was a problem with measurement data.</h2>
                        </body>""")
            else:
                self.textBrowser.append("""<body>
                    <h2 style='color:red;'>Simulation ended with errors.</h2>
                    </body>""")
                if "Duplicate device" in self.textBrowser.toPlainText():
                    self.textBrowser.append("""Subsystem syntax is not completely supported at this moment.<br>
                                            Please make sure that components in subsystems have different
                                            names than those on upper levels.""")
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
        self.params_path = os.path.dirname(os.path.abspath(self.xyce_file_path)) + "/xyce_params.t"
        # Write the parameters to a file
        if self.sim_params_dict['analysis_type'] == "Transient":
            with open(self.params_path, "w") as f:
                f.writelines([f"t_step = {self.sim_params_dict['max_ts']}\n",
                              f"total_time = {self.sim_params_dict['sim_time']}\n"
                              f"decimation = {float(self.sim_params_dict['max_ts'])}\n"])
        # Xyce simulation command
        os.chdir(os.path.dirname(self.xyce_file_path))
        #command = f'cmd /c pushd "{os.path.abspath(self.xyce_file_path)}" & xyce -prf "{self.params_path}" "{self.xyce_file_path}"\n'
        # Start the Xyce process
        command = f'"{str(self.xyce_simulator_path)}" "{self.xyce_file_path}"\n'
        # self.mdl.info(command)
        self.process.start(command)

    def abort_sim(self):
        self.process.kill()

    def plot_data(self):
        self.textBrowser.append("""<body>
            <h2 style='color:green;'>Opening the Signal Analyzer tool...</h2>
            </body>""")
        # Starts windows command prompt in the THCC drive, otherwise the typhoon_hil.cmd
        # batch can result in errors.

        model_name = pathlib.Path(self.json_file_path).stem
        cfg_file = pathlib.Path(self.json_file_path).parent.parent.joinpath(f"{model_name}_plot_cfg.json")
        add_config_file = f'--config_file="{str(cfg_file)}"' if cfg_file.is_file() else ""

        if self.sim_params_dict['analysis_type'] == "Transient":
            filename = "xyce_out"
            try:
                thcc_folder = os.environ["TYPHOONPATH"]
                process_string = f'cmd /c pushd "{thcc_folder[:2]}" & typhoon_hil sa --data_file="{os.getcwd()}\\{filename}.csv" {add_config_file} '
                self.plotprocess.startDetached(process_string)
            except KeyError:
                self.plotprocess.startDetached(
                    f'cmd /c pushd "C:" & typhoon_hil sa --data_file "{os.getcwd()}\\{filename}.csv" {add_config_file} ')
        else:
            filename = "xyce_f_out"
            # Use the temporary log-plot solution
            PlotWindow.plot_instances.append(PlotWindow(f"{os.getcwd()}\\{filename}.csv"))
            # Show this new instance
            PlotWindow.plot_instances[-1].show()

if __name__ == "__main__":
    from temp_log_plot import PlotWindow

    app = QApplication(sys.argv)
    sim_parameters = {
        'timeint_abstol': '1e-6',
        'timeint_reltol': '1e-2',
        'timeint_method': '7',
        'nonlinear_maxstep': '20',
        'nonlinear_abstol': '1e-6',
        'nonlinear_reltol': '1e-2',
        'nonlinear_solver': '0',
    }
    sim_parameters.update({'analysis_type': 'Transient', 'max_ts': '5e-9', 'sim_time': '0.2ms', "voltage_limiting": True})
    # sim_parameters.update({
    #     'analysis_type': 'AC small-signal',
    #     'start_f': '1',
    #     'end_f': '1000',
    #     'num_points': '10000'
    # })
    mainwindow = XyceOutput(None,
        r"D:\Dropbox\Typhoon HIL\Repository\xyce-typhoon-hil-interface\examples\logic_ports Target files\logic_ports.json",
        # r"D:\Dropbox\Typhoon HIL\Ideas\TSE2Xyce\Toronto Uni\buck_control Target files\buck_control.json",
        sim_parameters, xyce_simulator_path="xyce")
    mainwindow.show()
    sys.exit(app.exec_())
