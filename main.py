import atexit
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
import window


# def catch_exceptions(t, val, tb):
#     QMessageBox.critical(None,
#                          "An exception was raised",
#                          "Exception type: {}".format(t))
#     old_hook(t, val, tb)
#
#
# old_hook = sys.excepthook
# sys.excepthook = catch_exceptions
#
# try:
#     with open("counterfile") as infile:
#         _count = int(infile.read())
# except FileNotFoundError:
#     _count = 0
#
#
# def incrcounter(n):
#     global _count
#     _count = _count + n
#
#
# def savecounter():
#     with open("counterfile", "w") as outfile:
#         outfile.write("%d" % _count)
#
#
# atexit.register(savecounter)

def main():
    app = QApplication(sys.argv)
    windowAPT = window.MainWindow()
    windowAPT.show()
    app.exec_()


if __name__ == '__main__':
    main()
