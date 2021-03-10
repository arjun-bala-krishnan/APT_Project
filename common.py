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


def cuboid_data(center, size):
    """
       Reference: https://stackoverflow.com/questions/30715083/python-plotting-a-wireframe-3d-cuboid
       Create a data array for cuboid plotting.


       ============= ================================================
       Argument      Description
       ============= ================================================
       center        center of the cuboid, triple
       size          size of the cuboid, triple, (x_length,y_width,z_height)
       :type size: tuple, numpy.array, list
       :param size: size of the cuboid, triple, (x_length,y_width,z_height)
       :type center: tuple, numpy.array, list
       :param center: center of the cuboid, triple, (x,y,z)


      """

    # suppose axis direction: x: to left; y: to inside; z: to upper
    # get the (left, outside, bottom) point
    o = [a - b / 2 for a, b in zip(center, size)]
    # get the length, width, and height
    l, w, h = size
    x = [[o[0], o[0] + l, o[0] + l, o[0], o[0]],  # x coordinate of points in bottom surface
         [o[0], o[0] + l, o[0] + l, o[0], o[0]],  # x coordinate of points in upper surface
         [o[0], o[0] + l, o[0] + l, o[0], o[0]],  # x coordinate of points in outside surface
         [o[0], o[0] + l, o[0] + l, o[0], o[0]]]  # x coordinate of points in inside surface
    y = [[o[1], o[1], o[1] + w, o[1] + w, o[1]],  # y coordinate of points in bottom surface
         [o[1], o[1], o[1] + w, o[1] + w, o[1]],  # y coordinate of points in upper surface
         [o[1], o[1], o[1], o[1], o[1]],  # y coordinate of points in outside surface
         [o[1] + w, o[1] + w, o[1] + w, o[1] + w, o[1] + w]]  # y coordinate of points in inside surface
    z = [[o[2], o[2], o[2], o[2], o[2]],  # z coordinate of points in bottom surface
         [o[2] + h, o[2] + h, o[2] + h, o[2] + h, o[2] + h],  # z coordinate of points in upper surface
         [o[2], o[2], o[2] + h, o[2] + h, o[2]],  # z coordinate of points in outside surface
         [o[2], o[2], o[2] + h, o[2] + h, o[2]]]  # z coordinate of points in inside surface

    return x, y, z


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

# The following codes are not required yet, can be added in future if found to be needed
# The class that supports 3D plot by adding zoom function with mouse scroll.
# reference: https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
# Does not inherit any UI files
# class Zoom:
#     def __init__(self):
#         self.cur_xlim = None
#         self.cur_ylim = None
#
#     def zoom_factory(self, ax, base_scale=2.):
#         def zoom(event):
#             cur_xlim = ax.get_xlim()
#             cur_ylim = ax.get_ylim()
#
#             xdata = event.xdata  # get event x location
#             ydata = event.ydata  # get event y location
#
#             if event.button == 'up':
#                 # deal with zoom in
#                 scale_factor = 1 / base_scale
#             elif event.button == 'down':
#                 # deal with zoom out
#                 scale_factor = base_scale
#             else:
#                 # deal with something that should never happen
#                 scale_factor = 1
#                 print(event.button)
#
#             new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
#             new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
#
#             relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
#             rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
#
#             ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
#             ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
#             ax.figure.canvas.draw()
#
#         fig = ax.get_figure()  # get the figure of interest
#         fig.canvas.mpl_connect('scroll_event', zoom)
#
#         return zoom


# 3D Plot Window for APT dataset, opens a new Window with pan and zoom
# Does not inherit any UI files
# class Plot3D(QWidget):
#     def __init__(self, xs, ys, zs, ION, parent=None):
#         super(Plot3D, self).__init__(parent)
#         self.fig = Figure()
#         self.canvas = FigureCanvas(self.fig)
#         self.axes = self.fig.add_subplot(111, projection='3d')
#         self.toolbar = NavigationToolbar(self.canvas, self)
#
#         self.setLayout(QVBoxLayout())
#         self.layout().addWidget(self.toolbar)
#         self.layout().addWidget(self.canvas)
#
#         self.axes.scatter(xs, ys, zs, c='blue', s=30, label=ION, marker='.')
#         self.axes.legend()
#
#         self.axes.set_xlabel('X Axis')
#         self.axes.set_ylabel('Y Axis')
#         self.axes.set_zlabel('Z Axis')
#
#         zp = Zoom()
#         scale = 1.1
#         zp.zoom_factory(self.axes, base_scale=scale)
#         self.fig.tight_layout()