import matplotlib.pyplot as plt
import pandas as pd
from IPython.core.display import display, HTML
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from scipy.io import loadmat


def superscript(n):
    return "".join(["⁰¹²³⁴⁵⁶⁷⁸⁹"[ord(c) - ord('0')] for c in str(n)])

def subscript(n):
    return "".join(["₀₁₂₃₄₅₆₇₈₉"[ord(c) - ord('0')] for c in str(n)])

def read_data(data_matfile):
    """
    Reads the MATLAB data containing 4 fields viz., X, Y, Z and MN_Ratio
    :param data_matfile: path to a .mat file
    :return: pandas.DataFrame
    """
    tb = loadmat(data_matfile)
    pos = tb['pos']
    df_apt = pd.DataFrame(list(zip(pos[:, 0], pos[:, 1], pos[:, 2], pos[:, 3])),
                          columns=['X', 'Y', 'Z', 'MN_Ratio'])
    return df_apt


def view_image(image):
    """
    Visualize the image such as png graphs
    :param image: The image read in almost any format
    :return: Bobe
    """
    fig = plt.figure(figsize=(18, 16), dpi=80, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(image, cmap=plt.cm.gray)
    plt.axis("off")
    plt.show()


def print_dataframe_full(df):
    """
    Displays the whole dataframe regardless of the size
    :param df: pandas.DataFrame
    :return: None
    """
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        display(df)


def display_side_by_side(dfs: list, captions: list):
    """
    Display tables side by side to save vertical space
    Input:
        dfs: list of pandas.DataFrame
        captions: list of table captions
    Note:
        Do not use the complete dataframe in the following function, use head or tail for the display
    """
    output = ""
    combined = dict(zip(captions, dfs))
    for caption, df in combined.items():
        output += df.style.set_table_attributes("style='display:inline'").set_caption(caption)._repr_html_()
        output += "\xa0\xa0\xa0"
    display(HTML(output))


def show_message(message, btn1=False, btn1_name="Button1", btn1_fun=lambda: None,
                 btn2=False, btn2_name="Button2", btn2_fun=lambda: None,
                 btn3=False, btn3_name="Button3", btn3_fun=lambda: None):  # Default layout has an OK Button

    global show_message_btn1
    global show_message_btn2
    global show_message_btn3

    show_message_btn1 = False
    show_message_btn2 = False
    show_message_btn3 = False

    msg_box = QMessageBox()
    msg_box.raise_()
    msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)

    msg_box.setText(message)

    if btn1:
        btn1 = msg_box.addButton(btn1_name, QMessageBox.YesRole)
        btn1.clicked.connect(btn1_fun)

    if btn2:
        btn2 = msg_box.addButton(btn2_name, QMessageBox.NoRole)
        btn2.clicked.connect(btn2_fun)

    if btn3:
        btn3 = msg_box.addButton(btn3_name, QMessageBox.RejectRole)
        btn3.clicked.connect(btn3_fun)

    msg_box.exec_()
