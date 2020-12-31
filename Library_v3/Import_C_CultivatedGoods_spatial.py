# Import_C_CultivatedGoods_spatial
# Commands that import all spatial files for the Section A of TESSA
# by Francesca Perosa
# 05.02.2020

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




# SPATIAL DATA --------------------------------------------------------------------------------------------------

# DANUBE COUNTRIES SHAPE
def Import_Danube_countries_shp(iface,tool_path):
    Danube_countries_path = tool_path + "InputData_ES/0_Area_characteristics/DanubeCountries/Countries_Danube.shp"
    Danube_countries_name = "Countries_Danube"
    Danube_countries = iface.addVectorLayer(Danube_countries_path, Danube_countries_name, "ogr")
    return Danube_countries


# ANALYSIS AREA
def Import_AnalysisArea_shp(iface,tool_path,pilotArea_name):
    AreaAnalysis_layer_path = tool_path + "InputData_ES/0_Area_characteristics/"+pilotArea_name+"_AreaAnalysis/"+pilotArea_name+"_AreaAnalysis.shp"
    AreaAnalysis_layer_name = pilotArea_name+"_AreaAnalysis"
    AreaAnalysis_layer = iface.addVectorLayer(AreaAnalysis_layer_path, AreaAnalysis_layer_name, 'ogr')
    return AreaAnalysis_layer


# ES MAP STAKEHOLDERS
def Import_ESMapStakeholders_shp(iface,tool_path,pilotArea_name,scenarioID,cultivated_good_type):
    ESmapStake_layer_path = tool_path+"InputData_ES/ExtCBA_ESMapStakeholders_cultivatedGoods_"+pilotArea_name+"/"+scenarioID+"/ESMapStakeholders_cultivatedGoods_"+pilotArea_name+"_"+scenarioID+cultivated_good_type+".shp"
    ESmapStake_layer_name = "ESMapStakeholders_cultivatedGoods_"+pilotArea_name+"_"+scenarioID + cultivated_good_type
    ESmapStake_layer = iface.addVectorLayer(ESmapStake_layer_path, ESmapStake_layer_name, 'ogr')
    return ESmapStake_layer

# EARTHSTAT: HARVESTED AREA HECTARES
def Import_HarvestedAreaHectares_ras(iface,tool_path, mostImportantCrops_list):
    harvestedArea_raster_list = []
    for cropType in mostImportantCrops_list:
        harvestedArea_raster_path = tool_path+"InputData_ES/C_CultivatedGoods_spatial/HarvestedAreaYield175Crops_Geotiff_clippedDanube/" + cropType + "_HarvestedAreaHectares_Danube.tif"
        harvestedArea_raster_name = str(cropType + "_HarvestedAreaHectares_Danube")
        harvestedArea_raster = iface.addRasterLayer(harvestedArea_raster_path, harvestedArea_raster_name)
        harvestedArea_raster_list.append(harvestedArea_raster)
    return harvestedArea_raster_list



# EARTHSTAT: YIELD
def Import_YieldPerHectare_ras(iface,tool_path, mostImportantCrops_list):
    yieldPerHectare_raster_list = []
    for cropType in mostImportantCrops_list:
        yieldPerHectare_raster_path = tool_path+"InputData_ES/C_CultivatedGoods_spatial/HarvestedAreaYield175Crops_Geotiff_clippedDanube/" + cropType + "_YieldPerHectare_Danube.tif"
        yieldPerHectare_raster_name = str(cropType + "_YieldPerHectare_Danube")
        yieldPerHectare_raster = iface.addRasterLayer(yieldPerHectare_raster_path, yieldPerHectare_raster_name)
        yieldPerHectare_raster_list.append(yieldPerHectare_raster)
    return yieldPerHectare_raster_list



