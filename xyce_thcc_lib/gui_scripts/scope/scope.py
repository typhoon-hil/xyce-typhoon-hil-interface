from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMenu
import sys
import traceback
import pathlib
import json

# Show tracebacks #
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook

class ViewportListWidget(QtWidgets.QListWidget):

    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        self.config_dict = {}

    def avoid_duplicates(self, incoming_measurement):
        measurement_already_in_list = False
        for idx in range(self.count()):
            if self.item(idx).text() == incoming_measurement:
                measurement_already_in_list = True

        return measurement_already_in_list

    def mousePressEvent(self, e):
        for vp in self.parent.findChildren(ViewportListWidget):
            if not vp == self:
                vp.clearSelection()
        if self.itemAt(e.pos()) == None:  # Clicking on empty space
            self.clearSelection()
        super().mousePressEvent(e)

    def dragMoveEvent(self, event):
        if event.source() == self:
            event.mimeData().setText(event.source().item(self.currentRow()).text())
            event.mimeData().setData("config", json.dumps(self.config_dict).encode('utf-8'))

    def dropEvent(self, event):
        incoming_measurement = event.mimeData().text()
        keyboard_mod = QApplication.keyboardModifiers()
        if not incoming_measurement == "":
            if type(event.source()) == type(self): # Moved between viewports
                config = json.loads(str(event.mimeData().data("config"), encoding='utf-8'))
            else:
                config = {incoming_measurement: {'color': self.new_color(), 'linetype': 'solid'}}
            is_duplicate = self.avoid_duplicates(incoming_measurement)
            if not is_duplicate:
                self.config_dict.update(config)
                self.addItem(incoming_measurement)
                if keyboard_mod and keyboard_mod == QtCore.Qt.ControlModifier:
                    pass
                else:
                    if type(event.source()) == type(self) and not event.source() == self:
                        for idx in range(event.source().count()):
                            if event.source().item(idx).text() == incoming_measurement:
                                event.source().takeItem(idx)
                                event.source().clearSelection()
                                break

    def new_color(self):
        colors = [
                    "#FF0000",  # red
                    "#0000FF",  # blue
                    "#A349A4",  # purple
                    "#FF7F40",  # orange
                    "#00FF00",  # green
                    "#FFFF00",  # yellow
                    "#000000",  # black
                    "#7F7F7F"   # grey
                  ]
        for color in colors:
            repeated_color = False
            for measurement in self.config_dict:
                if self.config_dict.get(measurement).get("color").upper() == color.upper():
                    repeated_color = True
            if not repeated_color:
                return color

class MeasurementsListWidget(QtWidgets.QListWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.clicked_item = None

    def dragMoveEvent(self, e):
        if not e.source() == self:
            e.ignore()
        else:
            e.mimeData().setText(self.item(self.currentRow()).text())

    def dropEvent(self, event):
        pass

class Ui_Scope(object):
    def setupUi(self, Scope):
        self.base_path = pathlib.Path(__file__).parent
        self.colors_path = self.base_path.joinpath("colors")
        self.linetypes_path = self.base_path.joinpath("linetypes")
        Scope.setObjectName("Scope")
        Scope.resize(640, 410)
        Scope.setMinimumSize(QtCore.QSize(640, 410))
        Scope.setMaximumSize(QtCore.QSize(640, 410))

        self.box_available = QtWidgets.QGroupBox(Scope)
        self.box_available.setGeometry(QtCore.QRect(10, 80, 311, 320))
        self.box_available.setAlignment(QtCore.Qt.AlignCenter)
        self.box_available.setObjectName("box_available")

        self.list_voltages = MeasurementsListWidget(self.box_available)
        self.list_voltages.setGeometry(QtCore.QRect(10, 40, 91, 231))
        self.list_voltages.setMouseTracking(True)
        self.list_voltages.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.list_voltages.setToolTip("")
        self.list_voltages.setDragEnabled(True)
        self.list_voltages.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.list_voltages.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.list_voltages.setObjectName("list_voltages")

        self.label_voltages = QtWidgets.QLabel(self.box_available)
        self.label_voltages.setGeometry(QtCore.QRect(30, 22, 50, 16))
        self.label_voltages.setAlignment(QtCore.Qt.AlignCenter)
        self.label_voltages.setObjectName("label_voltages")

        self.label_voltages_3 = QtWidgets.QLabel(self.box_available)
        self.label_voltages_3.setGeometry(QtCore.QRect(230, 22, 50, 16))
        self.label_voltages_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_voltages_3.setObjectName("label_voltages_3")
        self.label_voltages_2 = QtWidgets.QLabel(self.box_available)
        self.label_voltages_2.setGeometry(QtCore.QRect(130, 22, 50, 16))
        self.label_voltages_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_voltages_2.setObjectName("label_voltages_2")

        self.list_currents = MeasurementsListWidget(self.box_available)
        self.list_currents.setGeometry(QtCore.QRect(110, 40, 91, 231))
        self.list_currents.setDragEnabled(True)
        self.list_currents.setMouseTracking(True)
        self.list_currents.setObjectName("list_currents")
        self.list_currents.setAcceptDrops(True)
        self.list_currents.setMouseTracking(True)

        self.mode_transient = QtWidgets.QRadioButton("Transient analysis", self.box_available)
        self.mode_transient.setObjectName("mode_transient")
        self.mode_transient.setGeometry(QtCore.QRect(35, 285, 150, 23))

        self.mode_AC = QtWidgets.QRadioButton("AC analysis", self.box_available)
        self.mode_AC.setObjectName("mode_AC")
        self.mode_AC.setGeometry(QtCore.QRect(180, 285, 150, 23))

        self.list_powers = MeasurementsListWidget(self.box_available)
        self.list_powers.setGeometry(QtCore.QRect(210, 40, 91, 231))
        self.list_powers.setDragEnabled(True)
        self.list_powers.setObjectName("list_powers")
        self.list_powers.setAcceptDrops(True)

        self.groupBox = QtWidgets.QGroupBox(Scope)
        self.groupBox.setGeometry(QtCore.QRect(330, 80, 301, 291))
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setObjectName("groupBox")

        self.label_vp_3 = QtWidgets.QLabel(self.groupBox)
        self.label_vp_3.setGeometry(QtCore.QRect(50, 152, 61, 16))
        self.label_vp_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_vp_3.setObjectName("label_vp_3")

        self.label_vp_1 = QtWidgets.QLabel(self.groupBox)
        self.label_vp_1.setGeometry(QtCore.QRect(50, 22, 61, 16))
        self.label_vp_1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_vp_1.setObjectName("label_vp_1")

        self.viewports_font = QtGui.QFont()
        self.viewports_font.setWeight(75)

        self.viewport_3 = ViewportListWidget(self.groupBox)
        self.viewport_3.setGeometry(QtCore.QRect(20, 170, 121, 101))
        self.viewport_3.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.viewport_3.setAcceptDrops(True)
        self.viewport_3.setDragEnabled(True)
        self.viewport_3.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.viewport_3.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.viewport_3.setObjectName("viewport_3")
        self.viewport_3.setFont(self.viewports_font)

        self.viewport_1 = ViewportListWidget(self.groupBox)
        self.viewport_1.setGeometry(QtCore.QRect(20, 40, 121, 101))
        self.viewport_1.setMouseTracking(True)
        self.viewport_1.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.viewport_1.setAcceptDrops(True)
        self.viewport_1.setAutoFillBackground(False)
        self.viewport_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.viewport_1.setDragEnabled(True)
        self.viewport_1.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.viewport_1.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.viewport_1.setObjectName("viewport_1")
        self.viewport_1.setFont(self.viewports_font)

        self.label_vp_2 = QtWidgets.QLabel(self.groupBox)
        self.label_vp_2.setGeometry(QtCore.QRect(190, 22, 61, 16))
        self.label_vp_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_vp_2.setObjectName("label_vp_2")

        self.viewport_2 = ViewportListWidget(self.groupBox)
        self.viewport_2.setGeometry(QtCore.QRect(160, 40, 121, 101))
        self.viewport_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.viewport_2.setAcceptDrops(True)
        self.viewport_2.setDragEnabled(True)
        self.viewport_2.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.viewport_2.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.viewport_2.setObjectName("viewport_2")
        self.viewport_2.setFont(self.viewports_font)

        self.label_vp_4 = QtWidgets.QLabel(self.groupBox)
        self.label_vp_4.setGeometry(QtCore.QRect(190, 152, 61, 16))
        self.label_vp_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_vp_4.setObjectName("label_vp_4")

        self.viewport_4 = ViewportListWidget(self.groupBox)
        self.viewport_4.setGeometry(QtCore.QRect(160, 170, 121, 101))
        self.viewport_4.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.viewport_4.setAcceptDrops(True)
        self.viewport_4.setDragEnabled(True)
        self.viewport_4.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.viewport_4.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.viewport_4.setViewMode(QtWidgets.QListView.ListMode)
        self.viewport_4.setObjectName("viewport_4")
        self.viewport_4.setFont(self.viewports_font)

        self.frame = QtWidgets.QFrame(Scope)
        self.frame.setGeometry(QtCore.QRect(10, 5, 621, 70))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.label_desc_1 = QtWidgets.QLabel(self.frame)
        self.label_desc_1.setGeometry(QtCore.QRect(10, 5, 531, 16))
        self.label_desc_1.setObjectName("label_desc_1")

        self.label_desc_2 = QtWidgets.QLabel(self.frame)
        self.label_desc_2.setGeometry(QtCore.QRect(10, 25, 600, 16))
        self.label_desc_2.setObjectName("label_desc_2")

        self.label_desc_3 = QtWidgets.QLabel(self.frame)
        self.label_desc_3.setGeometry(QtCore.QRect(10, 45, 531, 16))
        self.label_desc_3.setObjectName("label_desc_3")

        self.save_button = QtWidgets.QPushButton(Scope)
        self.save_button.setGeometry(QtCore.QRect(385.5, 380, 91, 23))
        self.save_button.setObjectName("save_button")

        self.cancel_button = QtWidgets.QPushButton(Scope)
        self.cancel_button.setGeometry(QtCore.QRect(485.5, 380, 91, 23))
        self.cancel_button.setObjectName("cancel_button")

        self.actionSet_color = QtWidgets.QAction(Scope)
        self.actionSet_color.setObjectName("actionSet_color")

        self.actionRed = QtWidgets.QAction(Scope)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("red.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRed.setIcon(icon)
        self.actionRed.setObjectName("actionRed")

        self.actionBlue = QtWidgets.QAction(Scope)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("blue.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionBlue.setIcon(icon1)
        self.actionBlue.setObjectName("actionBlue")

        self.actionGreen = QtWidgets.QAction(Scope)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("green.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionGreen.setIcon(icon2)
        self.actionGreen.setObjectName("actionGreen")
        self.actionPurple = QtWidgets.QAction(Scope)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("purple.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPurple.setIcon(icon3)
        self.actionPurple.setObjectName("actionPurple")
        self.actionGrey = QtWidgets.QAction(Scope)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("grey.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGrey.setIcon(icon4)
        self.actionGrey.setObjectName("actionGrey")
        self.actionOrange = QtWidgets.QAction(Scope)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("orange.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOrange.setIcon(icon5)
        self.actionOrange.setObjectName("actionOrange")
        self.actionYellow = QtWidgets.QAction(Scope)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("yellow.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionYellow.setIcon(icon6)
        self.actionYellow.setObjectName("actionYellow")
        self.actionBlack = QtWidgets.QAction(Scope)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(str(self.colors_path.joinpath("black.png"))), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBlack.setIcon(icon7)
        self.actionBlack.setObjectName("actionBlack")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(str(self.linetypes_path.joinpath("solid.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionSolid = QtWidgets.QAction(Scope)
        self.actionSolid.setIcon(icon8)
        self.actionSolid.setObjectName("actionSolid")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(str(self.linetypes_path.joinpath("dashed.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDashed = QtWidgets.QAction(Scope)
        self.actionDashed.setIcon(icon9)
        self.actionDashed.setObjectName("actionDashed")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(str(self.linetypes_path.joinpath("dotted.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDotted = QtWidgets.QAction(Scope)
        self.actionDotted.setIcon(icon10)
        self.actionDotted.setObjectName("actionDotted")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(str(self.linetypes_path.joinpath("dash-dot.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDashDot = QtWidgets.QAction(Scope)
        self.actionDashDot.setIcon(icon11)
        self.actionDashDot.setObjectName("actionDashDot")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(str(self.linetypes_path.joinpath("dash-dot-dot.png"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDashDotDot = QtWidgets.QAction(Scope)
        self.actionDashDotDot.setIcon(icon12)
        self.actionDashDotDot.setObjectName("actionDashDotDot")
        self.retranslateUi(Scope)
        QtCore.QMetaObject.connectSlotsByName(Scope)

    def retranslateUi(self, Scope):
        _translate = QtCore.QCoreApplication.translate
        Scope.setWindowTitle(_translate("Scope", "Scope"))
        self.save_button.setText(_translate("Scope", "OK"))
        self.box_available.setTitle(_translate("Scope", "Available measurements"))
        self.label_voltages.setText(_translate("Scope", "Voltage"))
        self.label_voltages_3.setText(_translate("Scope", "Power"))
        self.label_voltages_2.setText(_translate("Scope", "Current"))
        self.groupBox.setTitle(_translate("Scope", "Display on the Signal Analyzer"))
        self.label_vp_3.setText(_translate("Scope", "Viewport 3"))
        self.label_vp_1.setText(_translate("Scope", "Viewport 1"))
        self.label_vp_2.setText(_translate("Scope", "Viewport 2"))
        self.label_vp_4.setText(_translate("Scope", "Viewport 4"))
        self.label_desc_1.setText(_translate("Scope",
                                             "Use the Scope to set up the Signal Analyzer before starting the simulation."))
        self.label_desc_2.setText(_translate("Scope", "Drag and drop a measurement into a viewport to add it. You can also move it between viewports (hold Ctrl to copy)."))
        self.label_desc_3.setText(
            _translate("Scope", "Right-click a measurement on a viewport to set its color and line type."))
        self.cancel_button.setText(_translate("Scope", "Cancel"))
        self.actionSet_color.setText(_translate("Scope", "Set color"))
        self.actionRed.setText(_translate("Scope", "Red"))
        self.actionBlue.setText(_translate("Scope", "Blue"))
        self.actionGreen.setText(_translate("Scope", "Green"))
        self.actionPurple.setText(_translate("Scope", "Purple"))
        self.actionGrey.setText(_translate("Scope", "Grey"))
        self.actionOrange.setText(_translate("Scope", "Orange"))
        self.actionYellow.setText(_translate("Scope", "Yellow"))
        self.actionBlack.setText(_translate("Scope", "Black"))
        self.actionSolid.setText(_translate("Scope", "Solid"))
        self.actionDotted.setText(_translate("Scope", "Dotted"))
        self.actionDashed.setText(_translate("Scope", "Dashed"))
        self.actionDashDot.setText(_translate("Scope", "Dash-dot"))
        self.actionDashDotDot.setText(_translate("Scope", "Dash-dot-dot"))

class Scope(QDialog, Ui_Scope):
    meas_colors = {"red": "#FF0000", "blue":"#0000FF", "green": "#00FF00",
                   "purple": "#A349A4", "orange": "#FF7F40",
                   "yellow": "#FFFF00", "black": "#000000", "grey": "#7F7F7F"}

    def __init__(self, available_measurements, plot_cfg_file, mode="transient"):
        super().__init__()
        self.setupUi(self)
        self.added_terminals = []
        self.available_measurements = available_measurements
        self.plot_cfg_file = plot_cfg_file
        self.current_plot_cfg = {}
        self.current_mode = mode

        # Used colors
        self.color_order = ["red", "blue", "green", "purple", "orange", "yellow", "black", "grey"]
        self.vp1_used_colors = []
        self.vp2_used_colors = []
        self.vp3_used_colors = []
        self.vp4_used_colors = []

        # Available measurements
        self.fill_av_measurements()

        # Connect menu signal
        self.viewport_1.customContextMenuRequested.connect(self.viewport_menu)
        self.viewport_2.customContextMenuRequested.connect(self.viewport_menu)
        self.viewport_3.customContextMenuRequested.connect(self.viewport_menu)
        self.viewport_4.customContextMenuRequested.connect(self.viewport_menu)

        # Mode radio buttons
        mode = "transient" # Signal Analyzer is not ready yet
        if mode == "transient":
            self.mode_transient.setChecked(True)
            self.mode_AC.setChecked(False)
            self.mode_AC.setDisabled(True) # Signal Analyzer is not ready yet
        elif mode == "ac":
            self.mode_transient.setChecked(False)
            self.mode_AC.setChecked(True)

        self.mode_transient.clicked.connect(self.toggle_mode)
        self.mode_AC.clicked.connect(self.toggle_mode)

        # Adding and removing items from the viewport widget
        self.viewport_1.model().rowsAboutToBeRemoved.connect(
            lambda model, row: self.row_removed(model, row, self.viewport_1))
        self.viewport_1.model().rowsInserted.connect(lambda model, row: self.row_added(model, row, self.viewport_1))
        self.viewport_2.model().rowsAboutToBeRemoved.connect(
            lambda model, row: self.row_removed(model, row, self.viewport_2))
        self.viewport_2.model().rowsInserted.connect(lambda model, row: self.row_added(model, row, self.viewport_2))
        self.viewport_3.model().rowsAboutToBeRemoved.connect(
            lambda model, row: self.row_removed(model, row, self.viewport_3))
        self.viewport_3.model().rowsInserted.connect(lambda model, row: self.row_added(model, row, self.viewport_3))
        self.viewport_4.model().rowsAboutToBeRemoved.connect(
            lambda model, row: self.row_removed(model, row, self.viewport_4))
        self.viewport_4.model().rowsInserted.connect(lambda model, row: self.row_added(model, row, self.viewport_4))

        # Connect double clicks
        self.viewport_1.itemDoubleClicked.connect(self.remove_from_viewport)
        self.viewport_2.itemDoubleClicked.connect(self.remove_from_viewport)
        self.viewport_3.itemDoubleClicked.connect(self.remove_from_viewport)
        self.viewport_4.itemDoubleClicked.connect(self.remove_from_viewport)

        # Connect save/cancel buttons
        self.save_button.clicked.connect(self.save_config)
        self.cancel_button.clicked.connect(self.reject)

        # Load plot configuration file
        self.load_config()

    def toggle_mode(self):
        if self.mode_transient.isChecked():
            self.current_mode = "transient"
        if self.mode_AC.isChecked():
            self.current_mode = "ac"

        # Signal Analyzer is not ready yet
        self.current_mode = "transient"

        self.clear_av_measurements()
        self.fill_av_measurements()
        for vp in [self.viewport_1, self.viewport_2, self.viewport_3, self.viewport_4]:
            for idx in range(vp.count()):
                self.mark_measurement_not_found(vp.item(idx))


    def clear_av_measurements(self):

        self.list_voltages.clear()
        self.list_currents.clear()
        self.list_powers.clear()

    def fill_av_measurements(self):

        voltages = self.available_measurements.get(self.current_mode).get("voltages")
        for v in voltages:
            self.list_voltages.addItem(v)
        currents = self.available_measurements.get(self.current_mode).get("currents")
        for v in currents:
            self.list_currents.addItem(v)
        powers = self.available_measurements.get(self.current_mode).get("powers")
        for v in powers:
            self.list_powers.addItem(v)

    def row_added(self, model, row, viewport, color="red", linetype="solid"):
        added_item = viewport.item(row).text()

        if viewport.config_dict:
            # Apply the color
            keep_color = QtGui.QColor()
            keep_color.setNamedColor(viewport.config_dict.get(added_item).get('color'))
            viewport.item(row).setForeground(keep_color)
            keep_linetype = viewport.config_dict.get(added_item).get('linetype')
            self.added_update_cfg_dict(viewport, added_item, keep_color.name(), keep_linetype)
        self.mark_measurement_not_found(viewport.item(row))

    def added_update_cfg_dict(self, viewport, added_item, hexcolor, linetype):
        # Update current plot cfg
        for n in range(1, 5):
            if viewport == getattr(self, "viewport_" + str(n)):
                item_exists = self.current_plot_cfg.get("signals").get(added_item)
                if item_exists:
                    # Viewports
                    curr_viewports = item_exists.get("viewports")
                    if not n in curr_viewports:
                        curr_viewports.append(n)
                    # Colors
                    curr_colors = item_exists.get("color")
                    curr_colors.update({str(n): hexcolor})
                    # Linetypes
                    curr_linetypes = item_exists.get("display")
                    curr_linetypes.update({str(n): linetype})
                    viewport.config_dict.update({added_item: {"color": hexcolor, "linetype": linetype}})
                else:
                    # Viewports
                    self.current_plot_cfg.get("signals").update(
                        {
                            added_item: {
                                        "viewports": [n],
                                        "type": "analog",
                                        "color": {
                                            str(n): hexcolor
                                        },
                                        "display": {
                                            str(n): "solid"
                                        }
                                        }
                        })
                    viewport.config_dict.update({added_item: {"color": hexcolor, "linetype": "solid"}})

    def change_color_std(self, viewport, row, next_color="#000000"):
        this_color = QtGui.QColor()
        this_color.setNamedColor(next_color)
        viewport.item(row).setForeground(this_color)

    def remove_from_viewport(self, clicked_item):
        viewport = clicked_item.listWidget()
        row = viewport.indexFromItem(clicked_item).row()
        viewport.takeItem(row)

    def row_removed(self, model, row, viewport):
        took_item = viewport.item(row).text()
        self.removed_update_cfg_dict(viewport, took_item)

    def removed_update_cfg_dict(self, viewport, took_item):
        for n in range(1, 5):
            if viewport == getattr(self, "viewport_" + str(n)):
                took_item_dict = self.current_plot_cfg.get("signals").get(took_item)
                viewport_list = took_item_dict.get("viewports")
                viewport_list.remove(n)
                color_dict = took_item_dict.get("color")
                color_dict.pop(str(n))
                linetype_dict = took_item_dict.get("display")
                linetype_dict.pop(str(n))
                viewport.config_dict.pop(took_item)

    def change_selected_color(self, clicked_item, hexcolor):
        this_color = QtGui.QColor()
        this_color.setNamedColor(hexcolor)
        clicked_item.setForeground(this_color)
        viewport = clicked_item.listWidget()
        # Update current plot cfg
        for n in range(1, 5):
            if viewport == getattr(self, "viewport_" + str(n)):
                color_dict = self.current_plot_cfg.get("signals").get(clicked_item.text()).get("color")
                color_dict.update({str(n): hexcolor})
                item_dict = viewport.config_dict.get(clicked_item.text())
                item_dict.update({"color": hexcolor})

    def change_selected_linetype(self, clicked_item, linetype):
        viewport = clicked_item.listWidget()
        # Update current plot cfg
        for n in range(1, 5):
            if viewport == getattr(self, "viewport_" + str(n)):
                linetype_dict = self.current_plot_cfg.get("signals").get(clicked_item.text()).get("display")
                linetype_dict.update({str(n): linetype})
                item_dict = viewport.config_dict.get(clicked_item.text())
                item_dict.update({"linetype": linetype})

    def mark_measurement_not_found(self, vp_meas):
        # Check if the measurement exists on the circuit
        all_measurements = []
        all_measurements.extend(self.available_measurements.get(self.current_mode).get("voltages"))
        all_measurements.extend(self.available_measurements.get(self.current_mode).get("currents"))
        all_measurements.extend(self.available_measurements.get(self.current_mode).get("powers"))
        bg_color = QtGui.QColor()
        fg_color = QtGui.QColor()
        if vp_meas.text() not in all_measurements:
            bg_color.setNamedColor("#BB0000")
            fg_color.setNamedColor("#FFFFFF")
        else:
            bg_color.setNamedColor("#FFFFFF")
            fg_color.setNamedColor(vp_meas.listWidget().config_dict.get(vp_meas.text()).get("color"))
        vp_meas.setBackground(bg_color)
        vp_meas.setForeground(fg_color)

    def viewport_menu(self, pos):
        clicked_viewport = self.sender()
        m = QMenu(clicked_viewport)
        # Color submenu
        color_submenu = QMenu(m)
        color_submenu.setTitle("Set color")
        m.addMenu(color_submenu)
        # Line submenu
        line_submenu = QMenu(m)
        line_submenu.setTitle("Line type")
        m.addMenu(line_submenu)

        # Main menu actions
        self.actionRemove = QtWidgets.QAction("Remove", self)
        m.addAction(self.actionRemove)

        action_dict = {
            self.actionRed: ["color", "#FF0000"],  # red
            self.actionGreen: ["color", "#00FF00"],  # green
            self.actionBlue: ["color", "#0000FF"],  # blue
            self.actionPurple: ["color", "#A349A4"],  # purple
            self.actionOrange: ["color", "#FF7F40"],  # orange
            self.actionYellow: ["color", "#FFFF00"],  # yellow
            self.actionBlack: ["color", "#000000"],  # black
            self.actionGrey: ["color", "#7F7F7F"],  # grey
            self.actionSolid: ["linetype", "solid"],
            self.actionDotted: ["linetype", "dotted"],
            self.actionDashed: ["linetype", "dashed"],
            self.actionDashDot: ["linetype", "dash-dot"],
            self.actionDashDotDot: ["linetype", "dash-dot-dot"],
            self.actionRemove: ["remove", ""]
        }

        for action in action_dict:
            if action_dict.get(action)[0] == "color":
                color_submenu.addAction(action)
            elif action_dict.get(action)[0] == "linetype":
                line_submenu.addAction(action)

        self.font = QtGui.QFont()

        clicked_item = clicked_viewport.itemAt(pos)

        if clicked_item:
            current_color = clicked_viewport.config_dict.get(clicked_item.text()).get("color").upper()
            current_linetype = clicked_viewport.config_dict.get(clicked_item.text()).get("linetype")

            for k, v in action_dict.items():
                if v[1] in [current_color, current_linetype]:
                    self.font.setWeight(85)
                else:
                    self.font.setWeight(40)
                k.setFont(self.font)

            pos = clicked_viewport.mapToGlobal(pos)
            m.move(pos)
            clicked_action = m.exec()

            if clicked_action:
                clicked_viewport.clearSelection()
                if action_dict.get(clicked_action)[0] == "color":
                    self.change_selected_color(clicked_item, action_dict.get(clicked_action)[1])
                elif action_dict.get(clicked_action)[0] == "linetype":
                    self.change_selected_linetype(clicked_item, action_dict.get(clicked_action)[1])
                elif action_dict.get(clicked_action)[0] == "remove":
                    self.remove_from_viewport(clicked_item)
            else:
                clicked_viewport.clearSelection()

    def save_config(self):
        try:
            with open(self.plot_cfg_file, 'w') as f:
                json.dump(self.current_plot_cfg, f, indent=4)
        except:
            raise Exception(f"Couldn't save the file {self.plot_cfg_file}")
        self.accept()
    def load_config(self):
        try:
            with open(self.plot_cfg_file, 'r') as f:
                plot_config_dict = json.load(f)
        except FileNotFoundError:
            self.current_plot_cfg = {"signals": {},
                                     "viewports":   {
                                                    "1":{"x_label": "time (s)"},
                                                    "2": {"x_label": "time (s)"},
                                                    "3": {"x_label": "time (s)"},
                                                    "4": {"x_label": "time (s)"}
                                                    }
                                     }
            return

        signals_dict = plot_config_dict.get("signals")
        self.current_plot_cfg = plot_config_dict

        for signal in signals_dict.keys():
            if signal:
                subplot_list = signals_dict.get(signal).get("viewports")
                colors = signals_dict.get(signal).get("color")
                linetypes = signals_dict.get(signal).get("display")
                for n in subplot_list:
                    # Get viewport handle
                    vp = getattr(self, "viewport_" + str(n))
                    vp.config_dict.update({signal: {'color':colors.get(str(n)), 'linetype':linetypes.get(str(n))}})
                    # Add item to list
                    vp.addItem(signal)
                    # Set the item color
                    self.change_selected_color(vp.item(vp.count()-1), colors.get(str(n)))
                    # Mark if the measurement is not found in the circuit
                    self.mark_measurement_not_found(vp.item(vp.count()-1))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = Scope(available_measurements={
                                                "transient": {"voltages": ["v1", "v2", "v3"],
                                                              "currents": ["i1"],
                                                              "powers": ["P1"]},
                                                "ac": {"voltages": ["VP(v1)", "VM(v1)", "VP(v2)", "VP(v2)"],
                                                              "currents": ["i1"],
                                                              "powers": []},
                                                },
                       plot_cfg_file="plot_cfg3.json", mode="transient")
    mainwindow.show()
    sys.exit(app.exec_())
