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
    def __init__(self):
        super().__init__()
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