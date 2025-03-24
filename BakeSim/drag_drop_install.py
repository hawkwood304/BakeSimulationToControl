import urllib, os
import maya.cmds as cm
from maya.mel import eval
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def onMayaDroppedPythonFile(obj):
    directory = os.path.dirname(__file__)
    # maya_convert_directory = (os.path.join(str(directory))).replace(os.sep, '/')
    icon_directory = os.path.join(directory, "icons")

    name = "BakeSim"
    tooltip = "Bake simulation to control"
    imageName = "images.png"
    command = """from BakeSim import BakeSimToControl as BS
import importlib
importlib.reload(BS)
BS.MainWindow().show()
    """
    gShelfTopLevel = eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
    currentShelf = cm.tabLayout(gShelfTopLevel, q=True, st=True)
    path = (os.path.join(str(icon_directory), str(imageName))).replace(os.sep, '/')
    cm.shelfButton(parent=currentShelf, i=path, c=command, label=name, annotation=tooltip)
