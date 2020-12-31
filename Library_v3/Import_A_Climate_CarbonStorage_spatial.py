# Import_A_Climate_CarbonStorage_spatial
# Commands that import all spatial files for the Section A of TESSA
# by Francesca Perosa
# 13.01.2020

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

# slovenia
# ANALYSIS AREA
def Import_AnalysisArea_shp(iface, tool_path, pilotArea_name):
    AreaAnalysis_layer_path = tool_path + "InputData_ES/0_Area_characteristics/" + pilotArea_name + "_AreaAnalysis/"+ pilotArea_name + "_AreaAnalysis.shp"
    AreaAnalysis_layer_name = pilotArea_name + "_AreaAnalysis"
    AreaAnalysis_layer = iface.addVectorLayer(AreaAnalysis_layer_path, AreaAnalysis_layer_name, 'ogr')
    return AreaAnalysis_layer


# DANUBE COUNTRIES SHAPE
def Import_Danube_countries_shp(iface, tool_path ):
    Danube_countries_path = tool_path + "InputData_ES/0_Area_characteristics/DanubeCountries/Countries_Danube.shp"
    Danube_countries_name = "Countries_Danube"
    Danube_countries = iface.addVectorLayer(Danube_countries_path, Danube_countries_name, "ogr")
    return Danube_countries

def Import_Danube_countries_agr_shp(iface,tool_path ):
    Danube_countries_path = tool_path + "InputData_ES/0_Area_characteristics/DanubeCountries_agriculture/Countries_Danube_agriculture.shp"
    Danube_countries_name = "Countries_Danube_agriculture"
    Danube_countries = iface.addVectorLayer(Danube_countries_path, Danube_countries_name, "ogr")
    return Danube_countries_agriculture


# NUTS2 REGIONS SHAPE
def Import_NUTS2_regions_shp(iface, tool_path ):
    NUTS2_regions_path = tool_path + "InputData_ES/0_Area_characteristics/NUTS_RG_01M_2016_3035_LEVL_2/NUTS_RG_01M_2016_3035_LEVL_2.shp"
    NUTS2_regions_name = "NUTS_RG_01M_2016_3035_LEVL_2"
    NUTS2_regions = iface.addVectorLayer(NUTS2_regions_path, NUTS2_regions_name, "ogr")
    return NUTS2_regions

# EXT_CBA_2: HABITAT TYPE
def Import_HabitatType_ExtCBA2(iface,tool_path,pilotArea_name,scenarioID ):
    ExtCBA2_EcosystemTypes_path = tool_path + "InputData_ES/ExtCBA_2_Ecosystem_types_"+pilotArea_name+"/"+scenarioID+"/"+"ExtCBA_2_Ecosystem_types_"+ pilotArea_name +"_"+scenarioID+".shp"
    ExtCBA2_EcosystemTypes_name = "ExtCBA_2_Ecosystem_types_" + pilotArea_name +"_"+scenarioID
    ExtCBA2_EcosystemTypes_layer = iface.addVectorLayer(ExtCBA2_EcosystemTypes_path, ExtCBA2_EcosystemTypes_name, "ogr")
    if not ExtCBA2_EcosystemTypes_layer:
      print("Layer "+ExtCBA2_EcosystemTypes_name+" failed to load!")

    # set colors ---
    # define ranges: label, lower value, upper value, color name
    # in the field named 'Habit_Code' (from attributes table) 
    colors_ExtCBA_2 = (
        ('Tree', 0.5, 1.5, 'green'),
        ('Grass', 1.5, 2.5, 'yellow'),
        ('Crop', 2.5, 3.5, 'orange'),
        ('Rice', 3.5, 4.5, 'beige'),
        ('Wetland', 4.5, 5.5, 'brown')
    )
    # create a category for each item 
    ranges = []
    for label, lower, upper, color in colors_ExtCBA_2:
        symbol = QgsSymbol.defaultSymbol(ExtCBA2_EcosystemTypes_layer.geometryType())
        symbol.setColor(QColor(color))
        rng = QgsRendererRange(lower, upper, symbol, label)
        ranges.append(rng)
    # create the renderer and assign it to a layer
    expression = 'Habit_Code' # field name
    renderer = QgsGraduatedSymbolRenderer(expression, ranges)
    ExtCBA2_EcosystemTypes_layer.setRenderer(renderer)
    # more efficient than refreshing the whole canvas, which requires a redraw of ALL layers
    ExtCBA2_EcosystemTypes_layer.triggerRepaint()
    # update legend for layer
    qgis.utils.iface.layerTreeView().refreshLayerSymbology(ExtCBA2_EcosystemTypes_layer.id())
    # return
    return ExtCBA2_EcosystemTypes_layer


# SOIL ORGANIC CARBON (SOC) ---
# FAO Global Soil Organic Carbon Map
def Import_SoilOrganicCarbon_ras(iface,tool_path):
    SOC_ton_per_ha_raster_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_spatial/GLOCmap/FAO_GlobalSoilOrganicCarbonMap_V1_5_0.tiff"
    SOC_ton_per_ha_raster_name = "FAO_GlobalSoilOrganicCarbonMap_V1_5_0"
    SOC_ton_per_ha_raster = iface.addRasterLayer(SOC_ton_per_ha_raster_path, SOC_ton_per_ha_raster_name)
    return SOC_ton_per_ha_raster

# EXT_CBA_6: WETLAND CATEGORY
def Import_wetlandCategory_ExtCBA6(iface, tool_path,pilotArea_name,scenarioID):
    ExtCBA_6_wetlandCategory_path = tool_path + "InputData_ES/ExtCBA_6_wetlandCategory_" + pilotArea_name + "/"+scenarioID+"/"+"ExtCBA_6_wetlandCategory_"+ pilotArea_name +   "_" +scenarioID+".shp"
    ExtCBA_6_wetlandCategory_name = "ExtCBA_6_wetlandCategory_" + pilotArea_name + "_" +scenarioID
    ExtCBA_6_wetlandCategory = iface.addVectorLayer(ExtCBA_6_wetlandCategory_path, ExtCBA_6_wetlandCategory_name, "ogr")
    
    if not ExtCBA_6_wetlandCategory:
        print("Layer "+ExtCBA_6_wetlandCategory_name+" failed to load!")
        print("No wetland category file is available")
        
    else :
        return ExtCBA_6_wetlandCategory



# ES MAP STAKEHOLDERS
def Import_ESMapStakeholders_wood_shp(iface,tool_path,pilotArea_name,scenarioID):
    ESmapStake_layer_path = tool_path + "InputData_ES/ExtCBA_ESMapStakeholders_wood_"+pilotArea_name+"/"+scenarioID+"/"+pilotArea_name+"_used_ecosystem_services_final_wood_"+scenarioID+".shp"
    ESmapStake_layer_name = pilotArea_name + "_used_ecosystem_services_final_wood_"+scenarioID
    ESmapStake_wood_layer = iface.addVectorLayer(ESmapStake_layer_path, ESmapStake_layer_name, 'ogr')
    return ESmapStake_wood_layer

# RESULTS PART A
def Import_output01b_carbon_seq_shp(iface,tool_path,scenarioID):
    layer_path = tool_path + "OutputData_ES/A_climate_carbon_stocks/A_climate_output01b_carbon_seq_"+scenarioID+".shp"
    layer_name = "A_climate_output01b_carbon_seq_"+scenarioID
    netCsequestration_layer = iface.addVectorLayer(layer_path, layer_name, 'ogr')
    return netCsequestration_layer



# SOIL ORGANIC MATTER - ALTERNATIVE: soil organic carbon (SOC) raster map from FAO (2019) in tonnes/ha 
# clip SOM raster according to needs of the analysis
#input_raster = r"I:/05_Projects/2018_Danube_Floodplain/5_Working_Packages/A4.3/5_ES_assessment/InputData_ES/A_Global_Climate_Regulation_input/FAO_source/GLOCmap/FAO_GlobalSoilOrganicCarbonMap_V1_5_0.tiff"
#output_raster = r"I:/05_Projects/2018_Danube_Floodplain/5_Working_Packages/A4.3/5_ES_assessment/InputData_ES/A_Global_Climate_Regulation_input/FAO_source/GLOCmap/FAO_GlobalSoilOrganicCarbonMap_V1_5_0_MiddleTisza.tiff"
#input_vector = r"I:/05_Projects/2018_Danube_Floodplain/5_Working_Packages/A4.3/5_ES_assessment/InputData_ES/0_Area_characteristics/2Dmodelarea/2D_model_area_clarification.shp"
#input_vector_big = r"I:\05_Projects\2018_Danube_Floodplain\5_Working_Packages\A4.3\5_ES_assessment\InputData_ES\0_Area_characteristics\AnalysisAreaBig/AnalysisAreaBig.shp"
#clipped_SOM_MiddleTisza = clip_raster_by_vector(input_raster, input_vector_big, output_raster, overwrite=False)
#print('clipped_SOM_MiddleTisza =', clipped_SOM_MiddleTisza)
#
## processing.algorithmHelp("qgis:clip")
## imput layer: QgsVectorLayer
## overlay layer: QgsVectorLayer
## output place:  str 'd:/test.shp'
#parameters_CLC = {'INPUT': CORINE2018_vector,
#                  'OVERLAY': AreaAnalysis_layer,
#                  'OUTPUT': CORINE2018_clipped_path, # z.B. 'd:/test.shp'
#                  }
#processing.run("qgis:clip", parameters_CLC)


# CHANGE COLORS
def apply_graduated_symbology_10(join_layer, target_field, min_value, max_value):
    myRangeList = []
    colorList = ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee090" ,"#ffffbf", "#e0f3f8", "#abd9e9", "#74add1", "#4575b4", "#313695"]
    one_color_delta = (max_value - min_value)/10.0
    for i in range(0,10):
        symbol = QgsSymbol.defaultSymbol(join_layer.geometryType())
        symbol.setColor(QColor(colorList[i]))
        myRange = QgsRendererRange(min_value+(i)*one_color_delta, min_value+(i+1)*one_color_delta, symbol, str(str(round(min_value+(i)*one_color_delta))+ " - " + str(round(min_value+(i+1)*one_color_delta))) )
        myRangeList.append(myRange)
    myRenderer = QgsGraduatedSymbolRenderer(target_field, myRangeList)  
    myRenderer.setMode(QgsGraduatedSymbolRenderer.Custom)               
    join_layer.setRenderer(myRenderer)                                  
    print(f"Graduated color scheme applied")


