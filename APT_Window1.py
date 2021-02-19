import ast
import csv
import os
import re
import sys
import math
from typing import Dict, Any

import numpy as np
import pandas as pd
from IPython.display import display
from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QVBoxLayout, QTableWidgetItem, \
    QHeaderView, QTabWidget, QWidget, QListWidget, QLineEdit, QPushButton, QInputDialog, QLabel, QDialogButtonBox, \
    QMenuBar
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from natsort import index_natsorted, order_by_index
from silx.gui.widgets.PeriodicTable import PeriodicTable

import common
from UI import Ui_APTMainWindow, Ui_InputElementTable, Ui_PeriodicTable

# Functions defined in the common class
show_message = common.show_message

# maximum number of ions can be specified here
max_ions = 10
# The dictionary of ions for global use and update. Each ion will be one element_dict.
element_dict = {'ion': [], 'num': [], 'mass': [], 'charge': []}
cutoff_dict = {'peak_MNRatio': float, 'peak_tolerance': float, 'cutoff_bin': float, 'cutoff_height': int,
               'cutoff_width': int}
# list of element_dict corresponding to row number
element_dict_array: Dict[int, dict] = {}
# list of cutoff values corresponding to row number
cutoff_dict_array: Dict[int, dict] = {}


# The following class is used to visualize the dataframe inside the main window. The column size could be readjusted.
# Does not inherit any UI files
class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        if order == 0:
            self._dataframe = self._dataframe.reindex(index=order_by_index(self._dataframe.index, index_natsorted(
                eval('self._dataframe.%s' % (list(self._dataframe.columns)[column])))))
        else:
            self._dataframe = self._dataframe.reindex(index=order_by_index(self._dataframe.index, reversed(
                index_natsorted(eval('self._dataframe.%s' % (list(self._dataframe.columns)[column]))))))

        self._dataframe.reset_index(inplace=True, drop=True)
        self.setDataFrame(self._dataframe)
        self.layoutChanged.emit()


# The following class is used to plot histogram. Does not inherit any UI files
class HistogramWindow(QDialog):
    def __init__(self, subset_df_apt_hist, parent=None):
        super(HistogramWindow, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()
        self.subset_df_apt_hist = subset_df_apt_hist

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvasQTAgg(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot()

    def plot(self):
        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.title.set_text('APT Spectrum')
        ax.set_xlabel('MN_Ratio')
        ax.set_ylabel('Counts')
        ax.bar(self.subset_df_apt_hist.bin_lower, self.subset_df_apt_hist.freq,
               width=self.subset_df_apt_hist.bin_upper - self.subset_df_apt_hist.bin_lower, ec="k", align="edge")

        # refresh canvas
        self.canvas.draw()


class NumberAndMass(QDialog):
    def __init__(self, parent=None):
        super(NumberAndMass, self).__init__(parent)

        mainLayout = QVBoxLayout()
        self.lineedit, self.lineedit2 = QLineEdit(), QLineEdit()
        self.label, self.label2 = QLabel(), QLabel()
        self.btns = QDialogButtonBox()
        self.btns.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.label.setText("Enter No: of atoms (default 1)")
        self.label2.setText("Enter Atomic Mass (default as filled)")
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.lineedit)
        mainLayout.addWidget(self.label2)
        mainLayout.addWidget(self.lineedit2)
        mainLayout.addWidget(self.btns)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)
        self.setLayout(mainLayout)


class PeriodicTableCustom(Ui_PeriodicTable.Ui_Form, QDialog):
    def __init__(self, parent=None):
        super(PeriodicTableCustom, self).__init__(parent)
        self.setupUi(self)

        self.ptable = PeriodicTable(self.widget, selectable=False)
        self.ptable.sigElementClicked.connect(self.click_table)

        # inputDialog is used to get no: of atoms
        self.inputDialog = NumberAndMass()
        self.inputDialog.setWindowTitle('Input')
        # self.inputDialog.setLabelText('Enter No: of atoms (default 1)')
        self.lineEdit.setText("0")
        self.curr_row = None

        self.inputDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.pushButton_2.clicked.connect(self.delete)
        self.pushButton_5.clicked.connect(self.save)
        self.pushButton_5.clicked.connect(self.close)

    def delete(self):
        text = ""
        if len(element_dict['ion']) > 0:
            del element_dict['ion'][-1]
            del element_dict['num'][-1]
            for i in range(len(element_dict['ion'])):
                text = text + str(element_dict['ion'][i]) + common.subscript(str(element_dict['num'][i]))
        self.lineEdit_3.setText(text)

    def save(self):
        self.accept()
        return self.lineEdit.text()

    def click_table(self, item):
        self.showdialogTOP()
        self.inputDialog.lineedit2.setText(str(item.mass))
        self.inputDialog.lineedit.setText(str(1))
        ok = self.inputDialog.exec_()

        elem_num = self.inputDialog.lineedit.text()
        elem_mass = self.inputDialog.lineedit2.text()

        if ok:
            if len(element_dict['ion']) == 0:
                self.lineEdit_3.setText("")

            element_dict['ion'].append(str(item.symbol))
            element_dict['num'].append(elem_num)
            element_dict['mass'].append(elem_mass)
            text = ""
            for i in range(len(element_dict['ion'])):
                text = text + str(element_dict['ion'][i]) + common.subscript(str(element_dict['num'][i]))

            self.lineEdit_3.setText(text)
            element_dict_array[str(self.curr_row)] = dict()
            element_dict_array[str(self.curr_row)]['ion'] = element_dict['ion']
            element_dict_array[str(self.curr_row)]['num'] = element_dict['num']
            element_dict_array[str(self.curr_row)]['mass'] = element_dict['mass']
            element_dict_array[str(self.curr_row)]['charge'] = element_dict['charge']

    # The following makes sure the input dialogue to enter no: of atoms stays on top and on cursor location
    def showdialogTOP(self):
        self.inputDialog.move(QCursor.pos())
        self.inputDialog.show()
        self.inputDialog.raise_()


# The following class adds function to existing (inherited) UI for input elements. It is connected to periodic Table
class InputElementTable(Ui_InputElementTable.Ui_Form, QDialog):
    def __init__(self, parent=None):
        super(InputElementTable, self).__init__(parent)
        self.setupUi(self)

        self.tableWidget.setRowCount(max_ions)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Ion"))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("peak_MNRatio(Da)"))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem("MNRatio_tolerance(Da)"))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem("cutoff_bin"))
        self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem("cutoff_height"))
        self.tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem("cutoff_width"))
        self.PeriodicTableCustom = None
        self.row = 0
        self.col = 0
        self.item = None
        self.cell_clicked = False
        self.buttonBox.accepted.connect(self.submitclose)
        self.buttonBox.rejected.connect(self.reject)

        self.setMinimumSize(500, 500)
        self.setGeometry(QtCore.QRect(417, 220, 666, 653))

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.tableWidget.cellDoubleClicked.connect(self.cell_was_clicked)
        self.pushButton_2.clicked.connect(self.export_table)
        self.pushButton.clicked.connect(self.import_table)
        viewport = self.tableWidget.viewport()
        viewport.installEventFilter(self)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;csv Files (*.csv)", options=options)
        if fileName:
            return fileName + '.csv'

    def export_table(self):
        csv_file, extension = QFileDialog.getSaveFileName(
            self, 'Save File', '.', filter=self.tr("csv file (*.csv)"))
        csv_columns = ['ion', 'num', 'mass', 'charge', 'peak_MNRatio', 'peak_tolerance',
                       'cutoff_bin', 'cutoff_height', 'cutoff_width']

        self.submit()
        list_of_dict = []
        list1 = list(element_dict_array.keys())
        list1 = [int(i) for i in list1]
        list2 = list(cutoff_dict_array.keys())
        list2 = [int(i) for i in list2]
        if min(list1) <= min(list2):
            for key1 in element_dict_array:
                x = element_dict_array[key1]
                if int(key1) in list2:
                    y = cutoff_dict_array[key1]
                else:
                    y = {}
                z = {**x, **y}
                list_of_dict.append(z)

            for key2 in cutoff_dict_array:
                if int(key2) not in list1:
                    x = {}
                    y = cutoff_dict_array[key2]
                    z = {**x, **y}
                    list_of_dict.append(z)
        else:
            for key2 in cutoff_dict_array:
                y = cutoff_dict_array[key2]
                if int(key2) in list1:
                    x = element_dict_array[key2]
                else:
                    x = {}
                z = {**x, **y}
                list_of_dict.append(z)

            for key1 in element_dict_array:
                if int(key1) not in list2:
                    x = element_dict_array[key1]
                    y = {}
                    z = {**x, **y}
                    list_of_dict.append(z)

        try:
            with open(csv_file, 'w', newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()

                for row in list_of_dict:
                    writer.writerow(row)

        except IOError:
            common.show_message("I/O error")

    def import_table(self):
        csv_file = None
        csv_file, extension = QFileDialog.getOpenFileName(
            self, 'Save File', '.', filter=self.tr("csv file (*.csv)"))

        for value in element_dict.values():
            del value[:]
        for value in cutoff_dict.values():
            del value

        element_dict_array.clear()
        cutoff_dict_array.clear()

        if csv_file:
            try:
                with open(csv_file, "r") as fileInput:
                    for row_num, row in enumerate(csv.reader(fileInput)):
                        if row_num > 0:
                            r = row_num - 1
                            if row[0] != '':
                                element_dict_array[str(r)] = dict()
                                element_dict_array[str(r)]['ion'] = ast.literal_eval(row[0])
                                element_dict_array[str(r)]['num'] = ast.literal_eval(row[1])
                                element_dict_array[str(r)]['mass'] = ast.literal_eval(row[2])
                                element_dict_array[str(r)]['charge'] = ast.literal_eval(row[3])

                            cutoff_dict_array[str(r)] = dict()
                            cutoff_dict_array[str(r)]['peak_MNRatio'] = (row[4])
                            cutoff_dict_array[str(r)]['peak_tolerance'] = (row[5])
                            cutoff_dict_array[str(r)]['cutoff_bin'] = (row[6])
                            cutoff_dict_array[str(r)]['cutoff_height'] = (row[7])
                            cutoff_dict_array[str(r)]['cutoff_width'] = (row[8])

            except IOError:
                common.show_message("I/O error")

        self.refresh_table()

    def refresh_table(self):
        if len(element_dict_array) != 0:
            for key in element_dict_array:
                row = int(key)
                value = ''
                for ii in range(len(element_dict_array[key]['ion'])):
                    value = value + element_dict_array[key]['ion'][ii] + common.subscript(
                        element_dict_array[key]['num'][ii])
                    if ii == len(element_dict_array[key]['ion']) - 1:
                        value = value + '(' + element_dict_array[key]['charge'][0] + ')'

                item_ion = QTableWidgetItem()
                item_ion.setText(value)
                self.tableWidget.setItem(row, 0, item_ion)

        if len(cutoff_dict_array) != 0:
            for key in cutoff_dict_array:
                row = int(key)
                peak_MNRatio = cutoff_dict_array[key]['peak_MNRatio']
                peak_tolerance = cutoff_dict_array[key]['peak_tolerance']
                cutoff_bin = cutoff_dict_array[key]['cutoff_bin']
                cutoff_height = cutoff_dict_array[key]['cutoff_height']
                cutoff_width = cutoff_dict_array[key]['cutoff_width']
                if peak_MNRatio:
                    item_peak = QTableWidgetItem()
                    item_peak.setText(str(peak_MNRatio))
                    self.tableWidget.setItem(row, 1, item_peak)
                if peak_tolerance:
                    item_peak = QTableWidgetItem()
                    item_peak.setText(str(peak_tolerance))
                    self.tableWidget.setItem(row, 2, item_peak)
                if cutoff_bin:
                    item_cutoff_bin = QTableWidgetItem()
                    item_cutoff_bin.setText(str(cutoff_bin))
                    self.tableWidget.setItem(row, 3, item_cutoff_bin)
                if cutoff_height:
                    item_cutoff_height = QTableWidgetItem()
                    item_cutoff_height.setText(str(cutoff_height))
                    self.tableWidget.setItem(row, 4, item_cutoff_height)
                if cutoff_width:
                    item_cutoff_width = QTableWidgetItem()
                    item_cutoff_width.setText(str(cutoff_width))
                    self.tableWidget.setItem(row, 5, item_cutoff_width)

    def showEvent(self, event):
        super(InputElementTable, self).showEvent(event)
        self.refresh_table()

    def submit(self):
        key = None
        for r in range(max_ions):
            for c in range(1, 6):
                if c == 1:
                    key = 'peak_MNRatio'
                if c == 2:
                    key = 'peak_tolerance'
                if c == 3:
                    key = 'cutoff_bin'
                if c == 4:
                    key = 'cutoff_height'
                if c == 5:
                    key = 'cutoff_width'

                if self.tableWidget.item(r, c):
                    cutoff_dict[key] = self.tableWidget.item(r, c).text()
                else:
                    cutoff_dict[key] = None

            cutoff_dict_array[str(r)] = dict()
            cutoff_dict_array[str(r)]['peak_MNRatio'] = cutoff_dict['peak_MNRatio']
            cutoff_dict_array[str(r)]['peak_tolerance'] = cutoff_dict['peak_tolerance']
            cutoff_dict_array[str(r)]['cutoff_bin'] = cutoff_dict['cutoff_bin']
            cutoff_dict_array[str(r)]['cutoff_height'] = cutoff_dict['cutoff_height']
            cutoff_dict_array[str(r)]['cutoff_width'] = cutoff_dict['cutoff_width']

    def submitclose(self):
        self.submit()
        self.accept()
        self.close()

    def cell_was_clicked(self, row, column):
        self.cell_clicked = True
        self.row = row
        self.col = column
        self.item = self.tableWidget.itemAt(row, column)

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.MouseButtonDblClick:
            for key in element_dict:
                element_dict[key] = []

            headertext = self.tableWidget.horizontalHeaderItem(self.col).text()
            if headertext == 'Ion' and self.cell_clicked:
                self.PeriodicTableCustom = PeriodicTableCustom()
                if self.tableWidget.item(self.row, 0):
                    already_ion = self.tableWidget.item(self.row, 0).text()
                    if already_ion:
                        self.PeriodicTableCustom.lineEdit_3.setText(already_ion)

                self.PeriodicTableCustom.curr_row = self.row
                if self.PeriodicTableCustom.exec() == 1:
                    element_dict['charge'].append(self.PeriodicTableCustom.save())
                    text = ''
                    for i in range(len(element_dict['ion'])):
                        text = text + str(element_dict['ion'][i]) + common.subscript(str(element_dict['num'][i]))
                    if text:
                        charge = str(element_dict['charge'][0])
                        # head = charge.rstrip('0123456789')
                        # tail = charge[len(head):]
                        charge = '(' + charge + ')'
                        text = text + charge
                    item = QTableWidgetItem()
                    item.setText(text)
                    self.tableWidget.setItem(self.row, self.col, item)

        return super(InputElementTable, self).eventFilter(source, event)


class MainWindow(Ui_APTMainWindow.Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("APT Analyzer - Version 1.0")

        # Self Variables
        self.mat_file = None
        self.model = None
        self.plot_window = None
        self.input_table = None
        self.df_apt = None
        self.df_el = None
        self.df_apt_final = None
        self.completed = 0

        # Context Menu and double clicks for Main Menu, List widget and Tabs
        self.actionOpenMatFile.triggered.connect(self.input_file)
        self.actionExit.triggered.connect(sys.exit)
        self.tableView.horizontalHeader().setStretchLastSection(True)


        self.progressBar.setValue(self.completed)
        self.start_button_status()

        self.pushButton.clicked.connect(self.view_pandas)  # Update source location
        self.pushButton_2.clicked.connect(self.plot_hist)  # Plot Histogram
        self.pushButton_3.clicked.connect(self.input_elements)  # Input elements table
        self.pushButton_4.clicked.connect(self.start_binning)  # Make the dataframe from two dict and map elements here
        self.pushButton_7.clicked.connect(self.view_df_el)  # View the df elements here
        self.pushButton_8.clicked.connect(self.view_df_apt_final) # # View the whole df apt after binning here
        self.pushButton_5.clicked.connect(self.export_hdf)  # Save the final df_apt as HDF file for further analysis





    def start_button_status(self):
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_7.setEnabled(False)
        self.pushButton_8.setEnabled(False)
        self.pushButton_5.setEnabled(False)


    def export_hdf(self):
        file = QFileDialog.getSaveFileName(self, 'Select Matlab File"',
                                           os.getcwd(), "HDF files (*.h5)")
        float_columns = ['X', 'Y', 'Z', 'MN_Ratio', 'peak_MNRatio', 'peak_max_cutoff_width']
        int_columns = ['peak_no', 'XYZ_total_count']

        self.df_apt_final.loc[:, float_columns] = self.df_apt_final[float_columns].applymap(float)
        self.df_apt_final.loc[:, int_columns] = self.df_apt_final[int_columns].applymap(int)

        self.df_apt_final.to_hdf(file[0], key='df_apt_final', mode='w')

    # This is to show the Folder browser dialog and assign the mat file location to input variable
    def input_file(self):
        # file = self.openFileNameDialog()
        file = QFileDialog.getOpenFileName(self, 'Select Matlab File"',
                                           os.getcwd(), "Mat files (*.mat)")
        try:
            self.mat_file = file[0]
            print(self.mat_file)
            self.df_apt = common.read_data(self.mat_file)
            self.start_button_status()
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_4.setEnabled(True)

        except:
            self.pushButton.setEnabled(False)
            self.pushButton_4.setEnabled(False)

    def view_pandas(self):
        self.df_apt = common.read_data(self.mat_file)
        self.model = DataFrameModel(self.df_apt.head())
        self.tableView.setModel(self.model)
        for i in range(self.df_apt.shape[1]):
            self.tableView.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def view_df_apt_final(self):
        self.model = DataFrameModel(self.df_apt_final.head())
        self.tableView.setModel(self.model)
        for i in range(self.df_apt_final.shape[1]):
            self.tableView.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def view_df_el(self):
        self.model = DataFrameModel(self.df_el)
        self.tableView.setModel(self.model)
        for i in range(self.df_el.shape[1]):
            self.tableView.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def plot_hist(self):
        if self.lineEdit.text() == "":
            xlim_left = None
        else:
            string_xlim_left = self.lineEdit.text()
            xlim_left = re.sub("\D", "", string_xlim_left)
            xlim_left = float(string_xlim_left)

        if self.lineEdit_2.text() == "":
            xlim_right = None
        else:
            string_xlim_right = self.lineEdit_2.text()
            xlim_right = re.sub("\D", "", string_xlim_right)
            xlim_right = float(string_xlim_right)

        if self.lineEdit_3.text() == "":
            bins = None
        else:
            string_bins = self.lineEdit_3.text()
            bins = re.sub("\D", "", string_bins)
            bins = float(string_bins)

        if xlim_left is None or xlim_right is None or bins is None:
            show_message("No Parameters for Histogram")

        elif bins > 1:
            show_message("Enter a valid bin size (0 - 1)")

        else:
            num_bins = int((1 / bins) * np.max(self.df_apt["MN_Ratio"]))
            _freq, _bins = np.histogram(self.df_apt["MN_Ratio"], bins=num_bins)
            df_apt_hist = pd.DataFrame(list(zip(_bins[:-1], _bins[:-1], _freq)),
                                       columns=['bin_lower', 'bin_upper', 'freq'])

            subset_df_apt_hist = df_apt_hist[df_apt_hist["bin_lower"] > float(xlim_left)]
            subset_df_apt_hist = subset_df_apt_hist[subset_df_apt_hist["bin_lower"] < float(xlim_right)]

            self.plot_window = HistogramWindow(subset_df_apt_hist)
            self.plot_window.show()

    def input_elements(self):
        self.input_table = InputElementTable()
        if self.input_table.exec() == 1:
            pass

    def start_binning(self):
        list_of_dict = []
        self.completed = 0
        self.progressBar.setValue(self.completed)

        for key1 in element_dict_array:
            for key2 in cutoff_dict_array:
                if key2 == key1:
                    x = element_dict_array[key1]
                    y = cutoff_dict_array[key2]
                    z = {**x, **y}
                    list_of_dict.append(z)

        self.df_el = pd.DataFrame(list_of_dict)
        if self.df_el.empty:
            common.show_message("Enter the Elements Table..")
        if not self.df_el.empty:
            none_values = self.df_el.isnull().values.sum()
            if none_values > 0:
                common.show_message("Input elements and complete the table to start binning..")
            else:
                cutoff_bins = [float(i) for i in self.df_el['cutoff_bin'].values]
                peak_MNRatio = [float(i) for i in self.df_el['peak_MNRatio'].values]
                peak_tolerance = [float(i) for i in self.df_el['peak_tolerance'].values]
                cutoff_height = [int(i) for i in self.df_el['cutoff_height'].values]
                cutoff_width = [int(i) for i in self.df_el['cutoff_width'].values]

                class_iter = 0
                peak_no_max = 0
                dict_sub_df = {}
                dict_sub_df_hist = {}
                dict_sub_df_merged = {}

                while class_iter < self.df_el.shape[0]:
                    self.completed = (class_iter/ self.df_el.shape[0]) * 100.0
                    self.progressBar.setValue(self.completed)
                    reciprocal_bins = 1 / cutoff_bins[class_iter]
                    MNRatio_start = float(peak_MNRatio[class_iter] - peak_tolerance[class_iter] / 2.0)
                    MNRatio_end = float(peak_MNRatio[class_iter] + peak_tolerance[class_iter] / 2.0)
                    dict_sub_df[class_iter] = self.df_apt[self.df_apt["MN_Ratio"].between(MNRatio_start, MNRatio_end)]
                    num_bins = int(reciprocal_bins * (MNRatio_end - MNRatio_start))
                    bin_intervels = np.linspace(MNRatio_start, MNRatio_end, num_bins)
                    freq, bins = np.histogram(dict_sub_df[class_iter]["MN_Ratio"], bins=bin_intervels)

                    def truncate(f, n):
                        return math.floor(f * 10 ** n) / 10 ** n

                    for ib in range(len(bins)):
                        bins[ib] = truncate(bins[ib], np.log10(reciprocal_bins))

                    bin_intervels[-1] = bin_intervels[-1] + cutoff_bins[class_iter]

                    # freq will become peaks if it satisfy the given height and width conditions
                    dict_sub_df_hist[class_iter] = pd.DataFrame(list(zip(bins[:-1],
                                                                         bins[:-1] +
                                                                         cutoff_bins[class_iter],
                                                                         freq)),
                                                                columns=['bin_lower', 'bin_upper', 'freq'])

                    dict_sub_df_hist[class_iter]['Range_Cutoff_H_Value'] = cutoff_height[class_iter]
                    dict_sub_df_hist[class_iter]['Range_Cutoff_W_Value'] = cutoff_width[class_iter]

                    def check_cutoff_height(row):
                        if row['freq'] > row['Range_Cutoff_H_Value']:
                            return True
                        return False

                    dict_sub_df_hist[class_iter]['cutoff_height_status'] = dict_sub_df_hist[class_iter].apply(
                        lambda row: check_cutoff_height(row), axis=1)
                    dict_sub_df_hist[class_iter]['subgroup'] = \
                        (dict_sub_df_hist[class_iter]['cutoff_height_status'] !=
                         dict_sub_df_hist[class_iter]['cutoff_height_status'].shift(1)).cumsum()
                    dict_sub_df_hist[class_iter]['subgroup_freq'] = dict_sub_df_hist[class_iter].groupby('subgroup')[
                        'subgroup'].transform('count')

                    def check_cutoff_width(row):
                        if row['subgroup_freq'] > row['Range_Cutoff_W_Value'] and row['cutoff_height_status'] is True:
                            return True
                        return False

                    dict_sub_df_hist[class_iter]['cutoff_height_width_status'] = dict_sub_df_hist[class_iter].apply(
                        lambda row: check_cutoff_width(row), axis=1)
                    peak_cutoff_status = dict_sub_df_hist[class_iter]['cutoff_height_width_status'].tolist()

                    if class_iter == 0:
                        peak_no_iter = 0
                        peak_no_max = 0
                        peak_cutoff_status[0] = False
                    else:
                        peak_cutoff_status[0] = False
                        for class_idx in range(class_iter):
                            peak_no_max_idx = dict_sub_df_hist[class_idx]['peak_no'].max()
                            peak_no_max = max(peak_no_max, peak_no_max_idx)

                        peak_no_iter = peak_no_max

                    peak = np.zeros(len(peak_cutoff_status), dtype=np.int64)
                    for j in range(len(peak_cutoff_status)):
                        if peak_cutoff_status[j] is False:
                            peak[j] = 0
                        if peak_cutoff_status[j] is True:
                            if j > 0 and peak_cutoff_status[j - 1] is False:
                                peak_no_iter = peak_no_iter + 1
                            peak[j] = int(peak_no_iter)

                    dict_sub_df_hist[class_iter]['peak_no'] = peak
                    MN_Ratio = dict_sub_df[class_iter].MN_Ratio.values
                    bin_lower = dict_sub_df_hist[class_iter].bin_lower.values
                    bin_upper = dict_sub_df_hist[class_iter].bin_upper.values
                    ii, jj = np.where((MN_Ratio[:, None] >= bin_lower) & (MN_Ratio[:, None] <= bin_upper))
                    dict_sub_df_merged[class_iter] = pd.DataFrame(
                        np.column_stack([dict_sub_df[class_iter].values[ii], dict_sub_df_hist[class_iter].values[jj]]),
                        columns=dict_sub_df[class_iter].columns.append(dict_sub_df_hist[class_iter].columns))

                    class_iter = class_iter + 1

                df_apt_merged = pd.concat(dict_sub_df_merged.values(), ignore_index=True)

                max_peak_no = df_apt_merged['peak_no'].max() + 1
                dict_peak_min_max_count = dict()

                if max_peak_no > 1:
                    for peak_id in range(1, max_peak_no):
                        temp_df_apt = df_apt_merged[df_apt_merged["peak_no"] == peak_id]
                        max_cutoff_width = temp_df_apt.subgroup_freq.mode()[0]
                        peak_total_count = temp_df_apt.shape[0]
                        dict_peak_min_max_count[peak_id] = peak_id, temp_df_apt['MN_Ratio'].min(), \
                                                           temp_df_apt['MN_Ratio'].max(), max_cutoff_width, \
                                                           peak_total_count

                    def check_val_in_dict(peak_input, dict_peak_min_max_count):
                        non_peaks = 0
                        for key in dict_peak_min_max_count.keys():
                            if dict_peak_min_max_count[key][1] < peak_input < dict_peak_min_max_count[key][2]:
                                return pd.Series([int(dict_peak_min_max_count[key][0]),
                                                  dict_peak_min_max_count[key][3], dict_peak_min_max_count[key][4]])
                        return pd.Series([float('nan'), dict_peak_min_max_count[non_peaks][3], 0])

                    self.df_el[['peak_id', 'peak_max_cutoff_width', 'XYZ_total_count']] = self.df_el[
                        'peak_MNRatio'].apply(
                        lambda x: check_val_in_dict(float(x), dict_peak_min_max_count))

                    self.df_apt_final = pd.merge(df_apt_merged, self.df_el, how='left', left_on='peak_no',
                                                 right_on='peak_id')
                    self.df_apt_final = self.df_apt_final.dropna(subset=['ion'])
                    self.df_apt_final = self.df_apt_final.drop(
                        columns=['bin_lower', 'bin_upper', 'freq', 'Range_Cutoff_H_Value',
                                 'Range_Cutoff_W_Value', 'subgroup', 'subgroup_freq',
                                 'cutoff_height_status', 'cutoff_height_width_status',
                                 'peak_tolerance', 'cutoff_bin', 'cutoff_height',
                                 'cutoff_width', 'peak_id'])

                df_peak_min_max_count = pd.DataFrame(columns=['peak_id', 'min_MN', 'max_MN', 'peak_max_cutoff_width'])
                for key in dict_peak_min_max_count.keys():
                    df_peak_min_max_count = df_peak_min_max_count.append(
                        pd.Series({'peak_id': dict_peak_min_max_count[key][0],
                                   'min_MN': dict_peak_min_max_count[key][1],
                                   'max_MN': dict_peak_min_max_count[key][2],
                                   'peak_max_cutoff_width': dict_peak_min_max_count[key][3]}),
                        ignore_index=True)

                self.df_apt_final = self.df_apt_final.sort_values(by=['MN_Ratio'], ignore_index=True)

                def change_ion_name(row):
                    ion_array = row['ion']
                    text = ''
                    for ii in range(len(ion_array)):
                        text = text + ion_array[ii] + common.subscript(row['num'][ii])
                        if ii == len(ion_array) - 1:
                            text = text + '(' + row['charge'][0] + ')'
                    return text

                self.df_el['Ion'] = self.df_el.apply(lambda row: change_ion_name(row), axis=1)
                self.df_el = self.df_el.drop(columns=['ion', 'num', 'charge', 'peak_MNRatio', 'peak_tolerance',
                                                      'cutoff_bin', 'cutoff_height', 'cutoff_width'])
                cols = ['Ion', 'mass', 'peak_id', 'peak_max_cutoff_width', 'XYZ_total_count']
                self.df_el = self.df_el[cols]

                self.completed = 100
                self.progressBar.setValue(self.completed)

                self.pushButton_7.setEnabled(True)
                self.pushButton_8.setEnabled(True)
                self.pushButton_5.setEnabled(True)


