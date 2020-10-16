from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv
import os
import shutil
import processing
from qgis.core import *
from qgis.analysis import *
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.utils import *
from glob import glob
import time

LAYER_NAME = '2012_2020_Wisconsin_Election_Data_with_2017_Wards'
layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
    if layerQ.name() == LAYER_NAME:
        layer=layerQ

fieldsToDelete = ["DGA", "GASM", "DIRGERRYBY", "DIRGERRYBY_1",
                  "CONDIST","DIRGERRY_1","GASMd","DGAd"]


for fieldToDelete in fieldsToDelete:
	layer.startEditing()
	try:
		fieldsList = [field.name() for field in layer.pendingFields()]
		layer.dataProvider().deleteAttributes([fieldsList.index(fieldToDelete)])		
	except:
		print fieldToDelete, " is not in layer"
	layer.commitChanges()