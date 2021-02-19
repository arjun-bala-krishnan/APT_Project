import atexit
import numpy as np
import sys
import pandas as pd
import APT_Window1
from silx.gui.widgets.PeriodicTable import PeriodicTable

from PyQt5.QtWidgets import QApplication, QMessageBox, QTabWidget

import common


def catch_exceptions(t, val, tb):
    QMessageBox.critical(None,
                         "An exception was raised",
                         "Exception type: {}".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions

try:
    with open("counterfile") as infile:
        _count = int(infile.read())
except FileNotFoundError:
    _count = 0


def incrcounter(n):
    global _count
    _count = _count + n


def savecounter():
    with open("counterfile", "w") as outfile:
        outfile.write("%d" % _count)


atexit.register(savecounter)

# The manager of windows and what happens when Next and Back button are pressed
class Manager:

    def __init__(self):
        self.first = APT_Window1.MainWindow()
        self.first.show()


# Start of main
def main():
    desired_width = 320
    pd.set_option('display.width', desired_width)
    np.set_printoptions(linewidth=desired_width)
    pd.set_option('display.max_columns', 10)

    app = QApplication(sys.argv)
    manager = Manager()

    app.exec_()


if __name__ == '__main__': main()
