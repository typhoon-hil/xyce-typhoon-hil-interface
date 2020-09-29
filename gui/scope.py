from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMenu
import sys, traceback

# Show tracebacks #
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook


class ViewportListWidget(QtWidgets.QListWidget):

    def __init__(self, parent):
        super().__init__(parent)

    def avoid_duplicates(self, incoming_measurement):
        measurement_already_in_list = False
        for idx in range(self.count()):
            if self.item(idx).text() == incoming_measurement:
                measurement_already_in_list = True
        if not measurement_already_in_list:
            self.addItem(incoming_measurement)

        return measurement_already_in_list

    def dragMoveEvent(self, event):
        if event.source() == self:
            event.mimeData().setText(event.source().item(self.currentRow()).text())

    def dropEvent(self, event):
        incoming_measurement = event.mimeData().text()
        is_duplicate = self.avoid_duplicates(incoming_measurement)
        if type(event.source()) == ViewportListWidget and not event.source() == self:
            for idx in range(event.source().count()):
                if event.source().item(idx).text() == incoming_measurement and not is_duplicate:
                    event.source().takeItem(idx)
                    break

class MeasurementsListWidget(QtWidgets.QListWidget):

    def __init__(self, parent):
        super().__init__(parent)

    def dragMoveEvent(self, e):
        if not e.source() == self:
            e.ignore()
        else:
            e.mimeData().setText(self.item(self.currentRow()).text())

class Ui_Scope(object):
    def setupUi(self, Scope):
        Scope.setObjectName("Scope")
        Scope.resize(640, 410)
        Scope.setMinimumSize(QtCore.QSize(640, 410))
        Scope.setMaximumSize(QtCore.QSize(640, 410))
        self.plot_button = QtWidgets.QPushButton(Scope)
        self.plot_button.setGeometry(QtCore.QRect(230, 380, 91, 23))
        self.plot_button.setObjectName("plot_button")
        self.box_available = QtWidgets.QGroupBox(Scope)
        self.box_available.setGeometry(QtCore.QRect(10, 80, 311, 291))
        self.box_available.setAlignment(QtCore.Qt.AlignCenter)
        self.box_available.setObjectName("box_available")
        self.list_voltages = MeasurementsListWidget(self.box_available)
        self.list_voltages.setGeometry(QtCore.QRect(10, 40, 91, 231))
        self.list_voltages.setMouseTracking(True)
        self.list_voltages.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.list_voltages.setAcceptDrops(False)
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
        self.list_currents.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.list_currents.setObjectName("list_currents")
        self.list_powers = MeasurementsListWidget(self.box_available)
        self.list_powers.setGeometry(QtCore.QRect(210, 40, 91, 231))
        self.list_currents.setMouseTracking(True)
        self.list_powers.setDragEnabled(True)
        self.list_powers.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.list_powers.setObjectName("list_powers")
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
        self.label_desc_2.setGeometry(QtCore.QRect(10, 25, 531, 16))
        self.label_desc_2.setObjectName("label_desc_2")
        self.label_desc_3 = QtWidgets.QLabel(self.frame)
        self.label_desc_3.setGeometry(QtCore.QRect(10, 45, 531, 16))
        self.label_desc_3.setObjectName("label_desc_3")
        self.cancel_button = QtWidgets.QPushButton(Scope)
        self.cancel_button.setGeometry(QtCore.QRect(330, 380, 91, 23))
        self.cancel_button.setObjectName("cancel_button")
        self.actionSet_color = QtWidgets.QAction(Scope)
        self.actionSet_color.setObjectName("actionSet_color")
        self.actionRed = QtWidgets.QAction(Scope)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("colors/red.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionRed.setIcon(icon)
        self.actionRed.setObjectName("actionRed")
        self.actionBlue = QtWidgets.QAction(Scope)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("colors/blue.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionBlue.setIcon(icon1)
        self.actionBlue.setObjectName("actionBlue")
        self.actionGreen = QtWidgets.QAction(Scope)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("colors/green.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionGreen.setIcon(icon2)
        self.actionGreen.setObjectName("actionGreen")
        self.actionPurple = QtWidgets.QAction(Scope)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("colors/purple.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPurple.setIcon(icon3)
        self.actionPurple.setObjectName("actionPurple")
        self.actionGrey = QtWidgets.QAction(Scope)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("colors/grey.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGrey.setIcon(icon4)
        self.actionGrey.setObjectName("actionGrey")
        self.actionOrange = QtWidgets.QAction(Scope)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("colors/orange.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOrange.setIcon(icon5)
        self.actionOrange.setObjectName("actionOrange")
        self.actionYellow = QtWidgets.QAction(Scope)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("colors/yellow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionYellow.setIcon(icon6)
        self.actionYellow.setObjectName("actionYellow")
        self.actionBlack = QtWidgets.QAction(Scope)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("colors/black.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBlack.setIcon(icon7)
        self.actionBlack.setObjectName("actionBlack")
        self.actionRed = QtWidgets.QAction(Scope)

        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("linetypes/solid.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionSolid.setIcon(icon8)
        self.actionSolid.setObjectName("actionSolid")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("linetypes/dashed.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDashed.setIcon(icon9)
        self.actionDashed.setObjectName("actionDashed")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("linetypes/dotted.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDotted.setIcon(icon10)
        self.actionDotted.setObjectName("actionDotted")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("linetypes/dash-dot.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDashDot.setIcon(icon11)
        self.actionDashDot.setObjectName("actionDashDot")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("linetypes/dash-dot-dot.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionDashDotDot.setIcon(icon12)
        self.actionDashDotDot.setObjectName("actionDashDotDot")
        self.retranslateUi(Scope)
        QtCore.QMetaObject.connectSlotsByName(Scope)

    def retranslateUi(self, Scope):
        _translate = QtCore.QCoreApplication.translate
        Scope.setWindowTitle(_translate("Scope", "Scope"))
        self.plot_button.setText(_translate("Scope", "Save"))
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
                                             "Use the Scope to set up the displayed measurements on a Signal Analyzer tab before simulating."))
        self.label_desc_2.setText(_translate("Scope", "Drag and drop a measurement into a viewport to add it."))
        self.label_desc_3.setText(
            _translate("Scope", "You may right click a measurement on a viewport for extra options."))
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
    meas_colors = {"red": QtCore.Qt.red, "blue": QtCore.Qt.blue, "green": QtCore.Qt.green,
                   "purple": QtGui.QColor(163, 73, 164), "orange": QtGui.QColor(255, 128, 64),
                   "yellow": QtCore.Qt.yellow, "black": QtCore.Qt.black, "grey": QtGui.QColor(127, 127, 127)}

    def __init__(self, scope_config):
        super().__init__()
        self.setupUi(self)
        self.added_terminals = []
        self.scope_config = scope_config

        # Used colors
        self.color_order = ["red", "blue", "green", "purple", "orange", "yellow", "black", "grey"]
        self.vp1_used_colors = []
        self.vp2_used_colors = []
        self.vp3_used_colors = []
        self.vp4_used_colors = []

        # Available measurements
        self.av_voltages()
        self.av_currents()
        self.av_powers()

        # Connect menu signal
        self.viewport_1.customContextMenuRequested.connect(self.viewport_menu)
        self.viewport_1.model().rowsInserted.connect(self.dropped_item_vp1)
        self.viewport_2.customContextMenuRequested.connect(self.viewport_menu)
        self.viewport_2.model().rowsInserted.connect(self.dropped_item_vp2)
        self.viewport_3.customContextMenuRequested.connect(self.viewport_menu)
        self.viewport_3.model().rowsInserted.connect(self.dropped_item_vp3)
        self.viewport_4.customContextMenuRequested.connect(self.viewport_menu)
        self.viewport_4.model().rowsInserted.connect(self.dropped_item_vp4)

    def dropped_item_vp1(self, model, row):
        viewport = self.viewport_1
        next_color = "black"
        for color in self.color_order:
            if color not in self.vp1_used_colors:
                self.vp1_used_colors.append(color)
                next_color = color
                break
        self.change_color_std(viewport, row, next_color)

    def dropped_item_vp2(self, model, row):
        viewport = self.viewport_2
        next_color = "black"
        for color in self.color_order:
            if color not in self.vp2_used_colors:
                self.vp2_used_colors.append(color)
                next_color = color
                break
        self.change_color_std(viewport, row, next_color)

    def dropped_item_vp3(self, model, row):
        viewport = self.viewport_3
        next_color = "black"
        for color in self.color_order:
            if color not in self.vp3_used_colors:
                self.vp3_used_colors.append(color)
                next_color = color
                break
        self.change_color_std(viewport, row, next_color)

    def dropped_item_vp4(self, model, row):
        viewport = self.viewport_4
        next_color = "red"

        found_color = False
        if viewport.count() > 1:
            for color in self.color_order:
                if found_color:
                    break
                for idx in range(viewport.count()):
                    if not viewport.item(idx).foreground() == self.meas_colors[color]:
                        next_color = color
                        found_color = True
                        print(next_color)
                        break

        self.change_color_std(viewport, row, next_color)

    def change_color_std(self, viewport, row, next_color="black"):
        viewport.item(row).setForeground(self.meas_colors[next_color])

    def change_selected_color(self, clicked_item, color):
        clicked_item.setForeground(self.meas_colors[color])

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

        m.addAction("Remove")
        # Add color actions
        color_submenu.addAction(self.actionRed)
        color_submenu.addAction(self.actionBlue)
        color_submenu.addAction(self.actionGreen)
        color_submenu.addAction(self.actionPurple)
        color_submenu.addAction(self.actionOrange)
        color_submenu.addAction(self.actionYellow)
        color_submenu.addAction(self.actionBlack)
        color_submenu.addAction(self.actionGrey)

        clicked_item = clicked_viewport.itemAt(pos)
        if clicked_item:
            pos = clicked_viewport.mapToGlobal(pos)
            m.move(pos)
            clicked_action = m.exec()
            if clicked_action == self.actionRed:
                self.change_selected_color(clicked_item, "red")
            elif clicked_action == self.actionBlue:
                self.change_selected_color(clicked_item, "blue")
            elif clicked_action == self.actionGreen:
                self.change_selected_color(clicked_item, "green")
            elif clicked_action == self.actionPurple:
                self.change_selected_color(clicked_item, "purple")
            elif clicked_action == self.actionOrange:
                self.change_selected_color(clicked_item, "orange")
            elif clicked_action == self.actionYellow:
                self.change_selected_color(clicked_item, "yellow")
            elif clicked_action == self.actionBlack:
                self.change_selected_color(clicked_item, "black")
            elif clicked_action == self.actionGrey:
                self.change_selected_color(clicked_item, "grey")

    def av_voltages(self):
        voltages = self.scope_config.get("voltages")
        for v in voltages:
            self.list_voltages.addItem(v)

    def av_currents(self):
        currents = self.scope_config.get("currents")
        for v in currents:
            self.list_currents.addItem(v)

    def av_powers(self):
        powers = self.scope_config.get("powers")
        for v in powers:
            self.list_powers.addItem(v)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = Scope(scope_config={"voltages": ["v1", "v2", "v3"], "currents": ["i1"], "powers": ["P1"]})
    mainwindow.show()
    sys.exit(app.exec_())
