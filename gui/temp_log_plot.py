from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
import matplotlib
import matplotlib.figure
import sys
import pandas as pd
import re
import traceback
import math

# Show tracebacks #
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1000, 600)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mdiArea = QtWidgets.QMdiArea(Form)
        self.mdiArea.setObjectName("mdiArea")
        self.gridLayout_2.addWidget(self.mdiArea, 0, 0, 1, 1)
        self.pushButton_hide_show = QtWidgets.QPushButton(Form)
        self.pushButton_hide_show.setMaximumSize(QtCore.QSize(20, 40))
        self.pushButton_hide_show.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pushButton_hide_show.setObjectName("pushButton_hide_show")
        self.gridLayout_2.addWidget(self.pushButton_hide_show, 0, 1, 1, 1)
        self.options_widget = QtWidgets.QWidget(Form)
        self.options_widget.setMaximumSize(QtCore.QSize(136, 16777215))
        self.options_widget.setObjectName("widget")

        self.pushButton_add = QtWidgets.QPushButton(self.options_widget)
        self.pushButton_add.setMaximumSize(QtCore.QSize(118, 23))
        self.pushButton_add.setObjectName("pushButton_add")


        self.label_add = QtWidgets.QLabel()
        self.label_add.setAlignment(QtCore.Qt.AlignCenter)
        self.label_add.setObjectName("label_add")

        self.comboBox_add = QtWidgets.QComboBox()
        self.comboBox_add.setMaximumSize(QtCore.QSize(118, 20))
        self.comboBox_add.setObjectName("comboBox_add")

        self.comboBox_remove = QtWidgets.QComboBox()
        self.comboBox_remove.setMaximumSize(QtCore.QSize(118, 20))
        self.comboBox_remove.setObjectName("comboBox_remove")

        self.label_remove = QtWidgets.QLabel()
        self.label_remove.setAlignment(QtCore.Qt.AlignCenter)
        self.label_remove.setObjectName("label_remove")

        self.pushButton_remove = QtWidgets.QPushButton()
        self.pushButton_remove.setMaximumSize(QtCore.QSize(118, 23))
        self.pushButton_remove.setObjectName("pushButton_remove")

        self.gridLayout_2.addWidget(self.options_widget, 0, 2, 1, 1)
        self.gridLayout_2.setColumnMinimumWidth(1, 0)
        self.gridLayout_2.setRowMinimumHeight(1, 0)

        spacerItem1 = QtWidgets.QSpacerItem(115, 58, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout = QtWidgets.QGridLayout(self.options_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.label_add, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.comboBox_add, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.pushButton_add, 3, 1, 1, 1)
        self.gridLayout.addItem(spacerItem1, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.label_remove, 6, 1, 1, 1)
        self.gridLayout.addWidget(self.comboBox_remove, 7, 1, 1, 1)
        self.gridLayout.addWidget(self.pushButton_remove, 8, 1, 1, 1)
        self.gridLayout.addItem(spacerItem1, 9, 1, 1, 1)


        self.retranslateUi(Form)
        self.pushButton_add.clicked.connect(Form.add_to_plot)
        self.pushButton_hide_show.clicked.connect(Form.hide_show_options)
        self.pushButton_remove.clicked.connect(Form.remove_from_plot)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Log-plot tool (temporary)"))
        self.pushButton_hide_show.setText(_translate("Form", ">"))
        self.pushButton_add.setText(_translate("Form", "Add"))
        self.pushButton_remove.setText(_translate("Form", "Remove"))
        self.label_add.setText(_translate("Form", "Add a measurement"))
        self.label_remove.setText(_translate("Form", "Remove a measurement"))

class Ui_MatplotlibWindow(QtWidgets.QMainWindow):
    ''' Widget used for the maplotlib plots. '''
    def __init__(self, csvpath, av_vars):
        # plotlist is the list of variables to be plotted.
        super().__init__()
        self.av_vars = av_vars
        self.plotlist = list(self.av_vars)
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.csvpath = csvpath

        # Get the device standard window color
        rgba = self.main_widget.palette().color(QtGui.QPalette.Window).getRgb()
        rgba = tuple(a/255 for a in rgba)

        # Add widgets from the matplotlib backend
        self.figure = matplotlib.figure.Figure(tight_layout=True)
        self.figure.set_facecolor(rgba)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setStyleSheet('QToolBar{spacing:5px;}')
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)

        # Set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        self.main_widget.setLayout(layout)

        # Initializes with a single point plotted at 0,0
        self.drawing_mag = self.figure.add_subplot(211, xscale="log")
        self.drawing_phase = self.figure.add_subplot(212, sharex=self.drawing_mag, xscale="log")
        first_instance_mag = self.drawing_mag.plot()
        first_instance_phase = self.drawing_phase.plot()
        self.mag_legend = set()
        self.phase_legend = set()

        # Create a dictionary of curve instances
        self.ax_instances_mag = {0: first_instance_mag}
        self.ax_instances_phase = {1: first_instance_phase}
        self.drawing_mag.grid(which="both")
        self.drawing_phase.grid(which="both")

        # Set plot display properties
        with open(self.csvpath) as f:
            table = pd.read_csv(f)
            # X axis
            self.drawing_mag.set_xlim(min(table["Time"][1:]), max(table["Time"][1:]))
            self.drawing_phase.set_xlim(min(table["Time"][1:]), max(table["Time"][1:]))
            self.drawing_phase.set_xlabel("f (Hz)")
            # Y axis
            self.drawing_mag.set_ylabel("Magnitude (dB)")
            self.drawing_phase.set_ylabel("Phase (°)")

    # Add or remove the curves contained in add_var or remove_var.
    def update_plot(self, add_var, remove_var):
        # Read data from the CSV file
        with open(self.csvpath) as f:
            table = pd.read_csv(f)
            # Add an instance corresponding to add_var
            if add_var and add_var not in self.ax_instances_mag:

                for idx in range(int(len(self.av_vars.get(add_var))/2)):
                    mag = self.av_vars.get(add_var)[2*idx]
                    phase = self.av_vars.get(add_var)[2*idx+1]

                    new_ax, = self.drawing_mag.plot(table["Time"][1:], [20*math.log10(v) if not v == 0 else -1000 for v in table[mag][1:]])
                    # Update the ax_instances dict to include this new instance
                    self.ax_instances_mag.update({mag: new_ax})
                    self.mag_legend.add(self.av_vars.get(add_var)[2*idx])

                    new_ax, = self.drawing_phase.plot(table["Time"][1:], table[phase][1:])
                    # Update the ax_instances dict to include this new instance
                    self.ax_instances_phase.update({phase: new_ax})
                    self.phase_legend.add(self.av_vars.get(add_var)[2*idx+1])

            if remove_var:
                self.ax_instances_mag.get(self.av_vars.get(remove_var)[0]).remove()
                self.ax_instances_phase.get(self.av_vars.get(remove_var)[1]).remove()

                self.mag_legend.remove(self.av_vars.get(remove_var)[0])
                self.phase_legend.remove(self.av_vars.get(remove_var)[1])

            # Update legends
            self.drawing_mag.legend(self.mag_legend, loc='upper right')
            self.drawing_phase.legend(self.phase_legend, loc='upper right')

            self.canvas.draw()

class PlotWindow(QtWidgets.QWidget, Ui_Form):
    # List of PlotWindow class instances
    plot_instances = []
    # These values are updated by the Dialog class (proc_finished method)
    xyce_file_path = ""
    av_vars = []

    def __init__(self, plot_data_path):
        self.plot_data_path = plot_data_path
        super().__init__()
        self.setupUi(self)
        self.load_variables()
        self.plotlist = []
        # Variables not yet plotted
        self.notplotted = list(self.av_vars)
        # Variables already plotted
        self.plotted = []
        # Display the non-plotted variables in comboBox_add
        self.comboBox_add.addItems(self.notplotted)

        # Maximized frameless window inside the MDI area
        self.matplot = Ui_MatplotlibWindow(self.plot_data_path, self.av_vars)
        self.mdi_plot = self.mdiArea.addSubWindow(self.matplot)
        self.mdi_plot.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.matplot.showMaximized()

    # Rewriting the inherited closeEvent method to update the list of instances
    # def closeEvent(self, event):
    #     PlotWindow.plot_instances.remove(self)

    # pushButton_hide_show toggles options visibility to gain plot window area
    def hide_show_options(self):
        if self.pushButton_hide_show.text() == ">":
            self.options_widget.hide()
            self.pushButton_hide_show.setText("<")
        else:
            self.options_widget.show()
            self.pushButton_hide_show.setText(">")

    # Update the add/remove comboBoxes based on currently plotted variables
    def update_combos(self):
        self.comboBox_remove.clear()
        self.comboBox_remove.addItems(self.plotted)
        self.comboBox_add.clear()
        self.comboBox_add.addItems(self.notplotted)

    def add_to_plot(self):
        # plotvar is the variable selected in the comboBox
        plotvar = self.comboBox_add.currentText()
        if plotvar: # comboBox is not empty
            self.plotlist.append(plotvar)
            self.notplotted.remove(plotvar)
            self.plotted.append(plotvar)
            self.update_combos()
            self.matplot.update_plot(plotvar, None)

    def remove_from_plot(self):
        # plotvar is the variable selected in the comboBox
        plotvar = self.comboBox_remove.currentText()
        if plotvar: # comboBox is not empty
            self.plotlist.remove(plotvar)
            self.notplotted.append(plotvar)
            self.plotted.remove(plotvar)
            self.update_combos()
            self.matplot.update_plot(None, plotvar)

    def load_variables(self):

        variables = {}
        try:
            with open(self.plot_data_path) as f:
                table = pd.read_csv(f)
                all_cols = table.columns.to_list()[1:]
                for idx in range(0, len(all_cols), 2):
                    match = re.match("\w+\((\S+)\)", all_cols[idx])
                    if match:
                        entry_exists = variables.get(match.group(1))
                        if entry_exists:
                            variables.get(match.group(1)).extend([all_cols[idx], all_cols[idx + 1]])
                        else:
                            variables.update({match.group(1): [all_cols[idx], all_cols[idx + 1]]})
            self.av_vars = variables
        except:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = PlotWindow("xyce_f_out.csv")
    mainwindow.show()
    sys.exit(app.exec_())