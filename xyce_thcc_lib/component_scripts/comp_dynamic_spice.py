from PyQt5.QtWidgets import QWidget, QFileDialog, QDialog, QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys, csv, io, re, pathlib

from xyce_thcc_lib.extra.spice_syntax_conv import spice_to_xyce

def fix_spice_syntax(mdl, item_handle, file):
    new_filepath = spice_to_xyce(file)
    mdl.set_property_value(mdl.prop(item_handle, "model_path"), new_filepath)
    return new_filepath

def get_tse_model_and_relative_path(mdl, item_handle, file):
    abs_path = pathlib.Path(file)
    # mdl.info(str(abs_path))
    model_folder = pathlib.Path(mdl.get_model_file_path()).parent
    relative_path = abs_path.relative_to(model_folder)
    # mdl.info(str(model_path.parent.joinpath(relative_path)))
    return model_folder, relative_path

class FileDialog(QWidget):
    def __init__(self, mdl, item_handle):
        super().__init__()
        self.title = 'Choose Library File'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.mdl = mdl
        self.item_handle = item_handle
        self.comp_handle = mdl.get_sub_level_handle(item_handle)
        self.models_pin_info = {}

    def parse_file(self, mdl, item_handle):
        choose_file = QFileDialog()

        file, _ = choose_file.getOpenFileName(self, 'Choose Library File', '.', 'SPICE Library files (*.lib)')

        if file:
            self.parse_models(mdl, item_handle, file)
            return True
        else:
            return False

    def parse_models(self, mdl, item_handle, file):
        subcircuit_model_list = []
        # Find subcircuit-based models
        sub_based = re.compile(r"^\.SUBCKT\s+(\S+)\s+([^\n]+)\s+(?:PARAMS)?",
                               flags=re.I)

        fix_syntax = mdl.get_property_disp_value(mdl.prop(item_handle, "fix_syntax"))
        if fix_syntax:
            file = fix_spice_syntax(mdl, item_handle, file)

        # Try to find a relative path
        try:
            tse_model_path, relative_path = get_tse_model_and_relative_path(mdl, item_handle, file)
        except ValueError:
            relative_path = ""

        with io.open(file) as lib:
            in_sub_flag = False
            for line in lib:
                if not in_sub_flag:
                    sub_match = re.match(sub_based, line)
                    if sub_match:
                        # Enables when at least one match is found
                        mdl.enable_property(mdl.prop(item_handle, "configure_positions"))
                        mod_name = sub_match.group(1)
                        subcircuit_model_list.append(mod_name)
                        pin_list = sub_match.group(2).split()
                        self.models_pin_info.update({mod_name: pin_list})
                        in_sub_flag = True
                else:
                    # Detect end of the subcircuit and update flag
                    if re.match(r".[Ee][Nn][Dd][Ss]", line):
                        in_sub_flag = False

            if subcircuit_model_list:
                mdl.set_property_combo_values(mdl.prop(item_handle, "model_name"), subcircuit_model_list)
                mdl.set_property_value(mdl.prop(item_handle, "model_path"), str(file))
                mdl.set_property_value(mdl.prop(item_handle, "relative_model_path"), str(relative_path))
                mdl.set_property_disp_value(mdl.prop(item_handle, "model_name"), subcircuit_model_list[0])
                mdl.set_property_value(mdl.prop(item_handle, "loaded_lib"), str(file))
                mdl.set_property_disp_value(mdl.prop(item_handle, "loaded_lib"), str(file))
            else:
                mdl.set_property_disp_value(mdl.prop(item_handle, "loaded_lib"), "No subcircuit in file.")



def load_and_parse_file(mdl, item_handle):
    ex = FileDialog(mdl, item_handle)
    return ex.parse_file(mdl, item_handle)


def parse_models_loadfile(mdl, item_handle, models_pin_info):
    file = mdl.get_property_value(mdl.prop(item_handle, "model_path"))
    if not file == "-":

        # Check if there is a relative path
        relative_path = mdl.get_property_value(mdl.prop(item_handle, "relative_model_path"))
        if relative_path:
            model_folder = pathlib.Path(mdl.get_model_file_path()).parent
            file = str(model_folder.joinpath(file))
            mdl.info(f"IS RELATIVE: {file=}")
        # model_folder = pathlib.Path(mdl.get_model_file_path()).parent
        # if model_folder.joinpath(file).is_file():
        #     file = str(model_folder.joinpath(file))

        selected_model = mdl.get_property_value(mdl.prop(item_handle, "selected_model"))

        try:
            subcircuit_model_list = []
            # Find subcircuit-based models
            sub_based = re.compile(r"\.SUBCKT\s+(\S+)\s+([^\n]+)(?= PARAMS:)",
                                   flags=re.I)  # With PARAMS
            sub_based_2 = re.compile(r"\.SUBCKT\s+(\S+)\s+([^\n]+\n)",
                                     flags=re.I)  # Without PARAMS
            with io.open(file) as lib:
                in_sub_flag = False
                for line in lib:
                    if not in_sub_flag:
                        sub_match = re.match(sub_based, line)
                        if not sub_match:
                            sub_match = re.match(sub_based_2, line)
                        if sub_match:
                            # Enables when at least one match is found
                            mdl.enable_property(mdl.prop(item_handle, "configure_positions"))
                            mod_name = sub_match.group(1)
                            subcircuit_model_list.append(mod_name)
                            pin_list = sub_match.group(2).split()
                            models_pin_info.update({mod_name: pin_list})
                            in_sub_flag = True
                    else:
                        # Detect end of the subcircuit and update flag
                        if re.match(r".[Ee][Nn][Dd][Ss]", line):
                            in_sub_flag = False

        except FileNotFoundError:
            mdl.disable_property(mdl.prop(item_handle, "configure_positions"))

        mdl.set_property_combo_values(mdl.prop(item_handle, "model_name"), subcircuit_model_list)

        if selected_model in subcircuit_model_list:
            mdl.set_property_value(mdl.prop(item_handle, "pin_order"), ",".join(models_pin_info[selected_model]))


def update_component(mdl, item_handle, positions, models_pin_info):
    model_name_prop = mdl.prop(item_handle, "model_name")
    selected_model = mdl.get_property_value(model_name_prop)
    component = item_handle

    items = mdl.get_items(item_handle)
    # container_handle passes Category when opening library.
    # This deletes all components inside the category
    for it in items:
        # Connections have no type attribute. Conns are deleted indirectly.
        try:
            # Deal with junctions first
            if "Junction" in mdl.get_fqn(it):
                mdl.delete_item(it)
            mdl.delete_item(it)
        except:
            pass

    if not selected_model == "None":
        mdl.set_property_value(mdl.prop(item_handle, "selected_model"), selected_model)
        parse_models_loadfile(mdl, item_handle, models_pin_info)
        terminals = mdl.get_property_value(mdl.prop(item_handle, "pin_order")).split(",")
        x0 = 8192
        y0 = 8192
        offset = -1000
        count = 0
        #### Terminals creation
        for idx, term in enumerate(terminals):
            term_position = "left"
            # First time:
            positions.append(term_position)
            if idx == 0:
                first_port = mdl.create_port(
                    name=term,
                    parent=component,
                    terminal_position=(term_position, "auto"),
                    position=(x0 - 300, y0 + offset)
                )
                # Maintain pin position when file is saved
                pin_pos = mdl.get_property_value(mdl.prop(item_handle, "pin_positions")).split(",")
                pin_idxs = mdl.get_property_value(mdl.prop(item_handle, "pin_idx")).split(",")
                if not pin_pos == ["-"]:
                    mdl.set_port_properties(first_port, terminal_position=(pin_pos[idx], int(pin_idxs[idx])))
                before_junc = mdl.create_junction(
                    parent=component,
                    position=(x0 - 200, y0 + offset)
                )
                mdl.create_connection(first_port, before_junc)
            else:
                port = mdl.create_port(
                    name=term,
                    parent=component,
                    terminal_position=(term_position, "auto"),
                    rotation="down",
                    position=(x0, y0 + offset)
                )
                # Maintain pin position when file is saved
                pin_pos = mdl.get_property_value(mdl.prop(item_handle, "pin_positions")).split(",")
                pin_idxs = mdl.get_property_value(mdl.prop(item_handle, "pin_idx")).split(",")
                if not pin_pos == ["-"]:
                    mdl.set_port_properties(port, terminal_position=(pin_pos[idx], int(pin_idxs[idx])))
                short = mdl.create_component(
                    "core/Resistor",
                    parent=component,
                    position=(x0 - 100, y0 + offset)
                )
                junc = mdl.create_junction(
                    parent=component,
                    position=(x0 - 200, y0 + offset)
                )
                mdl.create_connection(port, mdl.term(short, "n_node"))
                mdl.create_connection(before_junc, junc)
                mdl.create_connection(junc, mdl.term(short, "p_node"))
                before_junc = junc
                offset += 75
            count += 1


# Terminal position configuration window
class Ui_TerminalPositions(object):
    def setupUi(self, TerminalPositions):
        TerminalPositions.setObjectName("TerminalPositions")
        TerminalPositions.resize(380, 427)
        TerminalPositions.setMinimumSize(QtCore.QSize(380, 427))
        TerminalPositions.setMaximumSize(QtCore.QSize(380, 427))
        self.buttonBox = QtWidgets.QDialogButtonBox(TerminalPositions)
        self.buttonBox.setGeometry(QtCore.QRect(110, 390, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText('OK')
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtWidgets.QGroupBox(TerminalPositions)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 361, 111))
        self.groupBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(44, 60, 141, 22))
        self.comboBox.setObjectName("comboBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(50, 40, 131, 20))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.widget = QtWidgets.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(240, 20, 81, 91))
        self.widget.setMinimumSize(QtCore.QSize(81, 91))
        self.widget.setMaximumSize(QtCore.QSize(81, 91))
        self.widget.setObjectName("widget")
        self.pushButton_left = QtWidgets.QPushButton(self.widget)
        self.pushButton_left.setGeometry(QtCore.QRect(10, 40, 21, 21))
        self.pushButton_left.setObjectName("pushButton_left")
        self.pushButton_down = QtWidgets.QPushButton(self.widget)
        self.pushButton_down.setGeometry(QtCore.QRect(30, 60, 21, 21))
        self.pushButton_down.setObjectName("pushButton_down")
        self.pushButton_up = QtWidgets.QPushButton(self.widget)
        self.pushButton_up.setGeometry(QtCore.QRect(30, 20, 21, 21))
        self.pushButton_up.setObjectName("pushButton_up")
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setGeometry(QtCore.QRect(10, 0, 61, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_cur_pos = QtWidgets.QLabel(self.widget)
        self.label_cur_pos.setGeometry(QtCore.QRect(30, 40, 21, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_cur_pos.setFont(font)
        self.label_cur_pos.setText("")
        self.label_cur_pos.setAlignment(QtCore.Qt.AlignCenter)
        self.label_cur_pos.setObjectName("label_cur_pos")
        self.pushButton_right = QtWidgets.QPushButton(self.widget)
        self.pushButton_right.setGeometry(QtCore.QRect(50, 40, 21, 21))
        self.pushButton_right.setObjectName("pushButton_right")
        self.groupBox_2 = QtWidgets.QGroupBox(TerminalPositions)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 130, 361, 261))
        self.groupBox_2.setObjectName("groupBox_2")
        self.listWidget_up = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget_up.setGeometry(QtCore.QRect(130, 30, 100, 90))
        self.listWidget_up.setObjectName("listWidget_up")
        self.listWidget_right = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget_right.setGeometry(QtCore.QRect(240, 90, 100, 90))
        self.listWidget_right.setObjectName("listWidget_right")
        self.listWidget_down = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget_down.setGeometry(QtCore.QRect(130, 140, 100, 90))
        self.listWidget_down.setObjectName("listWidget_down")
        self.listWidget_left = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget_left.setGeometry(QtCore.QRect(20, 90, 100, 90))
        self.listWidget_left.setObjectName("listWidget_left")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(255, 220, 71, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_missing_terms = QtWidgets.QLabel(self.groupBox_2)
        self.label_missing_terms.setGeometry(QtCore.QRect(10, 240, 191, 20))
        self.label_missing_terms.setAlignment(QtCore.Qt.AlignCenter)
        self.label_missing_terms.setObjectName("label_missing_terms")
        self.toolButton_idx_up = QtWidgets.QToolButton(self.groupBox_2)
        self.toolButton_idx_up.setGeometry(QtCore.QRect(330, 210, 21, 21))
        self.toolButton_idx_up.setText("")
        self.toolButton_idx_up.setObjectName("toolButton_idx_up")
        self.toolButton_idx_down = QtWidgets.QToolButton(self.groupBox_2)
        self.toolButton_idx_down.setGeometry(QtCore.QRect(330, 230, 21, 21))
        self.toolButton_idx_down.setText("")
        self.toolButton_idx_down.setObjectName("toolButton_idx_down")

        self.retranslateUi(TerminalPositions)
        self.buttonBox.accepted.connect(TerminalPositions.accept)
        self.buttonBox.rejected.connect(TerminalPositions.reject)
        QtCore.QMetaObject.connectSlotsByName(TerminalPositions)

    def retranslateUi(self, TerminalPositions):
        _translate = QtCore.QCoreApplication.translate
        TerminalPositions.setWindowTitle(_translate("TerminalPositions", "Terminal positions configuration"))
        self.groupBox.setTitle(_translate("TerminalPositions", "Configure positions for model"))
        self.label.setText(_translate("TerminalPositions", "Terminal"))
        self.pushButton_left.setText(_translate("TerminalPositions", "L"))
        self.pushButton_down.setText(_translate("TerminalPositions", "D"))
        self.pushButton_up.setText(_translate("TerminalPositions", "U"))
        self.label_3.setText(_translate("TerminalPositions", "Position"))
        self.pushButton_right.setText(_translate("TerminalPositions", "R"))
        self.groupBox_2.setTitle(_translate("TerminalPositions", "New positions"))
        self.label_2.setText(_translate("TerminalPositions", "Change index"))
        self.label_missing_terms.setText(_translate("TerminalPositions", "Some terminals are not yet configured"))


class TerminalPositionsDialog(QDialog, Ui_TerminalPositions):
    def __init__(self, mdl):
        super().__init__()
        self.mdl = mdl
        self.setupUi(self)
        self.added_terminals = []

        # Some extra configs
        self.toolButton_idx_up.setArrowType(QtCore.Qt.UpArrow)
        self.toolButton_idx_down.setArrowType(QtCore.Qt.DownArrow)
        self.label_missing_terms.setStyleSheet("color: red")

        # Must configure everything before OK is available
        self.buttonBox.buttons()[0].setEnabled(False)

        # Connect button functions
        self.pushButton_left.clicked.connect(self.add_to_list_left)
        self.pushButton_right.clicked.connect(self.add_to_list_right)
        self.pushButton_up.clicked.connect(self.add_to_list_up)
        self.pushButton_down.clicked.connect(self.add_to_list_down)
        self.toolButton_idx_up.clicked.connect(self.index_up)
        self.toolButton_idx_down.clicked.connect(self.index_down)

        # Connect QListWidget clicks
        self.listWidget_up.itemClicked.connect(self.clicked_on_list_up)
        self.listWidget_down.itemClicked.connect(self.clicked_on_list_down)
        self.listWidget_left.itemClicked.connect(self.clicked_on_list_left)
        self.listWidget_right.itemClicked.connect(self.clicked_on_list_right)

    def test_ok_available(self, inlist):
        if len(self.added_terminals) == self.comboBox.count():
            self.buttonBox.buttons()[0].setEnabled(True)
            self.label_missing_terms.setText("")
        # For faster adding of Terminals
        if not inlist:
            i = 1
            while i < self.comboBox.count():
                if not self.comboBox.currentText() in self.added_terminals:
                    break
                else:
                    self.comboBox.setCurrentIndex(i)
                i = i + 1

    def add_to_combo(self, terminals):
        self.comboBox.addItems(terminals)

    def display_selected_model(self, model):
        self.groupBox.setTitle("Configure positions for model " + model)

    def get_lists(self):
        rg_left = range(self.listWidget_left.count())
        left_list = [str(self.listWidget_left.item(i).text()) for i in rg_left]

        rg_right = range(self.listWidget_right.count())
        right_list = [str(self.listWidget_right.item(i).text()) for i in rg_right]

        rg_up = range(self.listWidget_up.count())
        up_list = [str(self.listWidget_up.item(i).text()) for i in rg_up]

        rg_down = range(self.listWidget_down.count())
        down_list = [str(self.listWidget_down.item(i).text()) for i in rg_down]

        return {"left": left_list, "right": right_list,
                "top": up_list, "bottom": down_list}

    def return_dict(self):
        return self.get_lists()

    def in_list_check(self):

        terminal = self.comboBox.currentText()
        lists = self.get_lists()
        inlist = False

        for pos in lists:
            if terminal in lists[pos]:
                inlist = True
                # Cannot duplicate
                if pos == "left":
                    item = self.listWidget_left.findItems(terminal, QtCore.Qt.MatchExactly)[0]
                    row = self.listWidget_left.row(item)
                    self.listWidget_left.takeItem(row)
                elif pos == "right":
                    item = self.listWidget_right.findItems(terminal, QtCore.Qt.MatchExactly)[0]
                    row = self.listWidget_right.row(item)
                    self.listWidget_right.takeItem(row)
                elif pos == "top":
                    item = self.listWidget_up.findItems(terminal, QtCore.Qt.MatchExactly)[0]
                    row = self.listWidget_up.row(item)
                    self.listWidget_up.takeItem(row)
                elif pos == "bottom":
                    item = self.listWidget_down.findItems(terminal, QtCore.Qt.MatchExactly)[0]
                    row = self.listWidget_down.row(item)
                    self.listWidget_down.takeItem(row)

        return (terminal, inlist)

    def add_to_list_left(self, position):
        terminal, inlist = self.in_list_check()
        self.listWidget_left.addItem(terminal)
        if terminal not in self.added_terminals:
            self.added_terminals.append(terminal)
        self.test_ok_available(inlist)

    def add_to_list_right(self, position):
        terminal, inlist = self.in_list_check()
        self.listWidget_right.addItem(terminal)
        if terminal not in self.added_terminals:
            self.added_terminals.append(terminal)
        self.test_ok_available(inlist)

    def add_to_list_up(self, position):
        terminal, inlist = self.in_list_check()
        self.listWidget_up.addItem(terminal)
        if terminal not in self.added_terminals:
            self.added_terminals.append(terminal)
        self.test_ok_available(inlist)

    def add_to_list_down(self, position):
        terminal, inlist = self.in_list_check()
        self.listWidget_down.addItem(terminal)
        if terminal not in self.added_terminals:
            self.added_terminals.append(terminal)
        self.test_ok_available(inlist)

    def index_up(self):
        selected_term = self.comboBox.currentText()
        if self.listWidget_left.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_left
        elif self.listWidget_right.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_right
        elif self.listWidget_up.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_up
        elif self.listWidget_down.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_down
        currentRow = list_widget.currentRow()
        currentItem = list_widget.takeItem(currentRow)
        list_widget.insertItem(currentRow - 1, currentItem)
        if currentRow - 1 >= 0:
            list_widget.setCurrentRow(currentRow - 1)
        else:
            list_widget.setCurrentRow(0)

    def index_down(self):
        selected_term = self.comboBox.currentText()
        if self.listWidget_left.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_left
        elif self.listWidget_right.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_right
        elif self.listWidget_up.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_up
        elif self.listWidget_down.findItems(selected_term, QtCore.Qt.MatchExactly):
            list_widget = self.listWidget_down
        currentRow = list_widget.currentRow()
        currentItem = list_widget.takeItem(currentRow)
        list_widget.insertItem(currentRow + 1, currentItem)
        if currentRow + 1 < list_widget.count() - 1:
            list_widget.setCurrentRow(currentRow + 1)
        else:
            list_widget.setCurrentRow(list_widget.count() - 1)

    def clicked_on_list_left(self):
        row = self.listWidget_left.currentRow()
        term = self.listWidget_left.item(row).text()
        idx = self.comboBox.findText(term, QtCore.Qt.MatchExactly)
        self.comboBox.setCurrentIndex(idx)

    def clicked_on_list_right(self):
        row = self.listWidget_right.currentRow()
        term = self.listWidget_right.item(row).text()
        idx = self.comboBox.findText(term, QtCore.Qt.MatchExactly)
        self.comboBox.setCurrentIndex(idx)

    def clicked_on_list_up(self):
        row = self.listWidget_up.currentRow()
        term = self.listWidget_up.item(row).text()
        idx = self.comboBox.findText(term, QtCore.Qt.MatchExactly)
        self.comboBox.setCurrentIndex(idx)

    def clicked_on_list_down(self):
        row = self.listWidget_down.currentRow()
        term = self.listWidget_down.item(row).text()
        idx = self.comboBox.findText(term, QtCore.Qt.MatchExactly)
        self.comboBox.setCurrentIndex(idx)


class Ui_ViewNetlist(object):
    def setupUi(self, ViewNetlist):
        ViewNetlist.setObjectName("ViewNetlist")
        ViewNetlist.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(ViewNetlist)
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser_netlist = QtWidgets.QTextBrowser(ViewNetlist)
        self.textBrowser_netlist.setObjectName("textBrowser_netlist")
        self.gridLayout.addWidget(self.textBrowser_netlist, 0, 0, 2, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 384, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)

        self.retranslateUi(ViewNetlist)
        QtCore.QMetaObject.connectSlotsByName(ViewNetlist)

    def retranslateUi(self, ViewNetlist):
        _translate = QtCore.QCoreApplication.translate
        ViewNetlist.setWindowTitle(_translate("ViewNetlist", "View netlist"))


class NetlistWindow(QDialog, Ui_ViewNetlist):
    def __init__(self, mdl, item_handle):
        self.mdl = mdl
        self.item_handle = item_handle
        super().__init__()
        self.setupUi(self)

        self.show_netlist()

    def show_netlist(self):
        self.textBrowser_netlist.clear()
        selected_model = self.mdl.get_property_disp_value(self.mdl.prop(self.item_handle, "model_name"))
        self.textBrowser_netlist.append(f"""<body>
                                        <h3 style='color:black; margin: 2'>Showing netlist for model</h3>
                                        <h2 style='color:red; margin: 4'>{selected_model}</h2>
                                        </body>""")
        self.textBrowser_netlist.setCurrentFont(QtGui.QFont("Courier New"))
        for line in self.get_model_lines():
            self.textBrowser_netlist.append(line[:-1])
        curs = self.textBrowser_netlist.textCursor()
        self.textBrowser_netlist.moveCursor(QtGui.QTextCursor.Start)

    def get_model_lines(self):

        file = self.mdl.get_property_value(self.mdl.prop(self.item_handle, "model_path"))
        model_folder = pathlib.Path(self.mdl.get_model_file_path()).parent
        file = str(model_folder.joinpath(file))
        selected_model = self.mdl.get_property_disp_value(self.mdl.prop(self.item_handle, "model_name"))

        regex_model = re.compile(fr"^\.SUBCKT {selected_model} ", flags=re.I)
        model_lines = []

        try:
            with open(file) as lib:
                in_model_flag = False
                for line in lib:
                    if not in_model_flag:
                        mod_match = re.match(regex_model, line)
                        if mod_match:
                            model_lines.append(line)
                            in_model_flag = True
                    else:
                        # Detect end of the subcircuit and update flag
                        if re.match(r".[Ee][Nn][Dd][Ss]", line):
                            model_lines.append(line)
                            in_model_flag = False
                        else:
                            model_lines.append(line)

            return model_lines

        except FileNotFoundError:
            self.mdl.info("Model file not found")
            return ["Model file not found."]


def configuration_availability(mdl, item_handle):
    model_name_prop = mdl.prop(item_handle, "model_name")
    configure_prop = mdl.prop(item_handle, "configure_positions")
    disp = mdl.get_property_disp_value(model_name_prop)
    val = mdl.get_property_value(model_name_prop)
    if val == disp:
        configure_terminal_positions(mdl, item_handle)
    else:
        mdl.info("Please confirm of cancel the model change before configuring the terminal positions.")


def configure_terminal_positions(mdl, item_handle):
    pin_pos_dict = {}
    pin_pos_list = []
    pin_idx_list = []
    model_name_prop = mdl.prop(item_handle, "model_name")
    selected_model = mdl.get_property_value(model_name_prop)
    # Load pin information
    terminals = mdl.get_property_value(mdl.prop(item_handle, "pin_order")).split(",")
    conf = TerminalPositionsDialog(mdl)
    # List available terminals in the ComboBox
    conf.comboBox.addItems(terminals)
    # Display the model being edited
    conf.display_selected_model(str(selected_model))

    # Run the GUI and get the new terminal positons
    if conf.exec_():
        new_term_positions = conf.return_dict()

        # Update terminal positions

        # Get all port handles
        port_handles = []
        # component = mdl.get_item(name=mdl.get_fqn(item_handle).split(".")[0])
        # all_handles = mdl.get_items(component)
        all_handles = mdl.get_items(item_handle)

        for h in all_handles:
            try:
                if h.item_type == "port":
                    port_handles.append(h)
            except:
                pass

        # Go through every terminal of the new_term_positions dict and compare
        # to the each port name (in port_handles). If the name is the same, set
        # the port position as the key of the dict (up, down, left, right)

        for key in new_term_positions:
            for term_name in new_term_positions[key]:
                for ph in port_handles:
                    port_name = mdl.get_fqn(ph).split(".")[-1]
                    if term_name == port_name:
                        new_pos = (key, new_term_positions[key].index(term_name) + 1)
                        mdl.set_port_properties(ph, terminal_position=new_pos)
                        pin_pos_dict.update({term_name: (new_pos[0], str(new_pos[1]))})

        for term in terminals:
            pin_pos_list.append(pin_pos_dict[term][0])
            pin_idx_list.append(pin_pos_dict[term][1])

    mdl.set_property_value(mdl.prop(item_handle, "pin_positions"), ",".join(pin_pos_list))
    mdl.set_property_value(mdl.prop(item_handle, "pin_idx"), ",".join(pin_idx_list))


def view_netlist(mdl, item_handle):
    netlistwindow = NetlistWindow(mdl, item_handle)
    netlistwindow.exec_()