from shiboken2 import wrapInstance

import os
import maya.cmds as cm
# import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2 import QtWidgets, QtCore, QtGui
from maya.mel import eval


# import sys

class QHLine(QtWidgets.QFrame):

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)


class QVLine(QtWidgets.QFrame):

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)


class QHLineName(QtWidgets.QGridLayout):

    def __init__(self, name):
        super(QHLineName, self).__init__()
        name_lb = QtWidgets.QLabel(name)
        name_lb.setAlignment(QtCore.Qt.AlignCenter)
        name_lb.setStyleSheet("font: italic 9pt;" "color: azure;")
        self.addWidget(name_lb, 0, 0, 1, 1)
        self.addWidget(QHLine(), 0, 1, 1, 2)


class BakeTool(QtWidgets.QWidget):
    fbxVersions = {
        '2016': 'FBX201600',
        '2014': 'FBX201400',
        '2013': 'FBX201300',
        '2017': 'FBX201700',
        '2018': 'FBX201800',
        '2019': 'FBX201900'
    }

    def __init__(self):
        super(BakeTool, self).__init__()

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.control_name_lb = QtWidgets.QLabel("Control simulation:")
        self.control_name_le = QtWidgets.QLineEdit()
        self.control_name_btn = QtWidgets.QPushButton("Assign")

        self.start_frame_lb = QtWidgets.QLabel("Start frame simulation:")
        self.start_frame_le = QtWidgets.QLineEdit()
        self.start_frame_btn = QtWidgets.QPushButton("Set")

        self.bake_control_btn = QtWidgets.QPushButton("Bake")

    def create_layouts(self):
        information_layout = QtWidgets.QGridLayout()
        information_layout.addWidget(self.control_name_lb, 0, 0, 1, 1)
        information_layout.addWidget(self.control_name_le, 0, 1, 1, 2)
        information_layout.addWidget(self.control_name_btn, 0, 3, 1, 1)

        information_layout.addWidget(self.start_frame_lb, 1, 0, 1, 1)
        information_layout.addWidget(self.start_frame_le, 1, 1, 1, 2)
        information_layout.addWidget(self.start_frame_btn, 1, 3, 1, 1)

        bake_layout = QtWidgets.QHBoxLayout()
        bake_layout.addWidget(self.bake_control_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(information_layout)
        main_layout.addLayout(bake_layout)

    def create_connections(self):
        self.control_name_btn.clicked.connect(self.assign_control_button)
        self.start_frame_btn.clicked.connect(self.set_control_button)
        self.bake_control_btn.clicked.connect(self.bake_sim_to_control)

    def assign_control_button(self):
        control_name = ""
        list_selection = cm.ls(sl=True)
        if len(list_selection) != 1:
            om.MGlobal_displayError("You can only chose one control sim per time")
        else:
            control_name = list_selection[0]

        self.control_name_le.setText(control_name)

    def set_control_button(self):
        time_set = self.start_frame_le.text()
        nucleus_list = cm.ls(type="nucleus")
        for nu in nucleus_list:
            cm.setAttr(f"{nu}.startFrame", int(time_set))

    def bake_sim_to_control(self):
        list_control_bake = cm.ls(sl=True)

        control_sim_onoff = self.control_name_le.text()

        list_loc_bake = []
        list_constraint_bake = []

        if cm.getAttr(f"{control_sim_onoff}.Simulation") == 1:
            for control_bake in list_control_bake:
                loc = cm.spaceLocator(name=f"{control_bake}_loc")[0]
                list_loc_bake.append(loc)
                cont = cm.parentConstraint(control_bake, loc, mo=False)[0]
                list_constraint_bake.append(cont)

            min_time = cm.playbackOptions(q=True, min=True)
            max_time = cm.playbackOptions(q=True, max=True)
            cm.select(list_loc_bake)
            print(list_loc_bake)
            eval(
                'bakeResults -simulation true -t "{0}:{1}" -sampleBy 1 -oversamplingRate 1 '
                '-disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false '
                '-removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer '
                'false -minimizeRotation true -controlPoints false -shape false;'.format(
                    min_time, max_time))

            cm.delete(list_constraint_bake)

            cm.setAttr(f"{control_sim_onoff}.Simulation", 0)

            for loc_baked in list_loc_bake:
                control_name = loc_baked.replace("_loc", "")
                cm.parentConstraint(loc_baked, control_name, mo=False)

            cm.select(list_control_bake)
            eval(
                'bakeResults -simulation true -t "{0}:{1}" -sampleBy 1 -oversamplingRate 1 '
                '-disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false '
                '-removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer '
                'false -minimizeRotation true -controlPoints false -shape false;'.format(
                    min_time, max_time))

            cm.delete(list_loc_bake)
# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit,PyMethodOverriding
class MainWindow(QtWidgets.QDialog):
    WINDOW_TITLE = "Bake Sim"

    SCRIPTS_DIR = cm.internalVar(userScriptDir=True)
    ICON_DIR = os.path.join(SCRIPTS_DIR, 'Thi/Icon')

    dlg_instance = None

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = MainWindow()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()

        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    @classmethod
    def maya_main_window(cls):
        """

        Returns: The Maya main window widget as a Python object

        """
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        super(MainWindow, self).__init__(self.maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.geometry = None

        self.setMinimumSize(400, 150)
        self.create_widget()
        self.create_layouts()
        self.create_connections()

    def create_widget(self):
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.addWidget(BakeTool())

        self.close_btn = QtWidgets.QPushButton("Close")
        self.about_btn = QtWidgets.QPushButton("About")

    def create_layouts(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.about_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(self.content_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.close_btn.clicked.connect(self.close)

    def showEvent(self, e):
        super(MainWindow, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        super(MainWindow, self).closeEvent(e)

        self.geometry = self.saveGeometry()
