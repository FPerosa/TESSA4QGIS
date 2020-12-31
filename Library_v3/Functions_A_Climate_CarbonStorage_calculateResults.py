# Functions_A_Climate_CarbonStorage_calculateResults
# Functions to calclate the results of the section
# by Francesca Perosa
# 14.01.2020

# ============================================================================================
import sys
import os
import sqlite3
import numpy 

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from qgis.core import *
from qgis.gui import *
import qgis.analysis

from qgis.core import (
     QgsApplication, 
     QgsProcessingFeedback, 
     QgsVectorLayer
)


# CREATE COPY OF SHAPEFILE
# Create new shapefile to save all results (copy from original file of habitat types) ---
# (from: https://gis.stackexchange.com/questions/205947/duplicating-layer-in-memory-using-pyqgis)
def createCopy_habitatsShapefile(vlayer, nameNewLayer):
    feats_original = [feat for feat in vlayer.getFeatures()] # get features from riginal habitats shapefile
    carbonStocks_layer = QgsVectorLayer("Polygon?crs=epsg:3035", nameNewLayer, "memory") # create empty new layer
    # get data from old shapefile
    carbonStocks_layer_data = carbonStocks_layer.dataProvider() 
    attr = vlayer.dataProvider().fields().toList()
    carbonStocks_layer_data.addAttributes(attr)
    carbonStocks_layer.updateFields()
    carbonStocks_layer_data.addFeatures(feats_original)
    # create instance of shapefile
    QgsProject.instance().addMapLayer(carbonStocks_layer)
    # get indexes of the attribute table in the new layer
    id_habitat_code = carbonStocks_layer.fields().indexFromName('Habit_Code')

    # Create Area_ha field
    myField = QgsField( 'Area_ha', QVariant.Double )
    carbonStocks_layer.dataProvider().addAttributes([myField])
    carbonStocks_layer.updateFields()
    idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
    #start editing
    carbonStocks_layer.startEditing()
    for f in carbonStocks_layer.getFeatures():
        f[idx_HA] = f.geometry().area()*0.0001
        # print(f[idx_HA])
        carbonStocks_layer.updateFeature( f )
    # commit changes
    carbonStocks_layer.commitChanges()
    #return
    return carbonStocks_layer


# CREATE COPY OF SHAPEFILE
# Create new shapefile to save all results (copy from original file of habitat types) ---
# (from: https://gis.stackexchange.com/questions/205947/duplicating-layer-in-memory-using-pyqgis)
def createCopy_wetlandsShapefile(vlayer, nameNewLayer):
    feats_original = [feat for feat in vlayer.getFeatures()] # get features from riginal habitats shapefile
    wetlands_layer = QgsVectorLayer("Polygon?crs=epsg:3035", nameNewLayer, "memory") # create empty new layer
    # get data from old shapefile
    wetlands_layer_data = wetlands_layer.dataProvider() 
    attr = vlayer.dataProvider().fields().toList()
    wetlands_layer_data.addAttributes(attr)
    wetlands_layer.updateFields()
    wetlands_layer_data.addFeatures(feats_original)
    # create instance of shapefile
    QgsProject.instance().addMapLayer(wetlands_layer)
    # get indexes of the attribute table in the new layer
    id_code = wetlands_layer.fields().indexFromName('Id')
    #return
    return wetlands_layer

