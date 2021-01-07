import os
from functools import partial

import pandas as pd
from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from UI import Ui_APTMainWindow
import common
import numpy as np
# Functions defined in the common class
show_message = common.show_message


def plot_hist(df_apt, bins, xlim_left, xlim_right, save=True):
    bins_save = bins
    num_bins = int((1 / bins) * np.max(df_apt["MN_Ratio"]))
    freq, bins = np.histogram(df_apt["MN_Ratio"], bins=num_bins)

    df_apt_hist = pd.DataFrame(list(zip(bins[:-1], bins[:-1], freq)),
                               columns=['bin_lower', 'bin_upper', 'freq'])

    subset_df_apt_hist = df_apt_hist[df_apt_hist["bin_lower"] > float(xlim_left)]
    subset_df_apt_hist = subset_df_apt_hist[subset_df_apt_hist["bin_lower"] < float(xlim_right)]

    plt.figure(figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
    plt.title('APT Spectrum')
    plt.xlabel('MN_Ratio')
    plt.ylabel('Counts')
    plt.bar(subset_df_apt_hist.bin_lower, subset_df_apt_hist.freq,
            width=subset_df_apt_hist.bin_upper - subset_df_apt_hist.bin_lower, ec="k", align="edge")
    if save is True:
        plt.savefig("Spectrum_" + str(xlim_left) + "_" + str(xlim_right) + ".png")

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


class MainWindow(Ui_APTMainWindow.Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("APT Analyzer - Version 1.0")

        # Self Variables
        self.mat_file = 0

        # Context Menu and double clicks for Main Menu, List widget and Tabs
        self.actionOpenMatFile.triggered.connect(self.input_file)

    # This is to show the Folder browser dialog and assign the mat file location to input variable
    def input_file(self):
        # file = self.openFileNameDialog()
        file = QFileDialog.getOpenFileName(self, 'Select Matlab File"',
                                           os.getcwd(), "Mat files (*.mat)")
        try:
            self.mat_file = file[0]
            print(self.mat_file)
        except:
            pass
