import atexit
import os
import sys
import APT_Window1

from IPython.core.display import display
from PyQt5.QtWidgets import QApplication, QMessageBox

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


def main():
    app = QApplication(sys.argv)
    manager = Manager()
    app.exec_()

    curr_dir = os.getcwd()
    data_matfile = os.path.join(curr_dir, "Input", "totaldata2.mat")
    df_apt = common.read_data(data_matfile)
    display(df_apt)


if __name__ == '__main__': main()
