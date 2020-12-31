# Import_A_Climate_CarbonStorage_tables
# Commands that import all tables for the Section A of TESSA
# by Francesca Perosa
# 03.09.2020

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


# IMPORT TABLES IPCC -----------------------------------------------------------------------------------------------------

# AGB: for crude estimates of above-ground live biomass carbon stocks:
#Table 4.7 (for natural forests) in Chapter 4 of IPCC (2006)
#Table 4.8 (for forest plantations) in Chapter 4 of IPCC (2006)
#Table 4.12 (for natural forests and forest plantations in more detailed classification) in Chapter 4 of IPCC (2006)
#Table 4.3 (for coastal Mangroves) in Chapter 4 of IPCC (2014) 
#Table 5.2 (for cropping systems, no Europe) in Chapter 5 of IPCC (2006)
#Table 5.2 (for agroforestry systems, no Europe) in Chapter 5 of IPCC (2006)
#Table 5.3 (for default values for specific types of crop-dominated habitats in Asia and Africa) in Chapter 5 of IPCC (2006)
#Alternative table for grass and wetland by Anderson-Teixeira and deLucia, 2011

# BGB: for crude estimates of below-ground live biomass carbon stocks:
#Table 4.4 (for tree-dominated areas, perennial crops and urban parks) in Chapter 4 of IPCC (2006) 
#Table 4.5 (for coastal Mangroves) in Chapter 4 of IPCC (2014)
#Table 6.1 (for grass-dominated or woody savannah and urban lawns) in Chapter 6 of IPCC (2006)
#For freshwater wetlands, there are no IPCC default factors for below ground biomass calculation.
#Therefore, use locally applicable published values (as a rule of thumb, the conversion
#factor is 0.3 for annual wetland vegetation species without rhizomes (Cronk & Fennessy 2001))
#Otherwise, see Appendix 2 of TESSA toolkit, for a relevant estimate of below-ground biomass for your habitat.

# LITTER
#Table 2.2 in Chapter 2 of IPCC (2006): for mature forests: 
# habitat tree-dominated, woody savannah, forested wetland (including coastal mangrove swamps),
# a forest plantation (including woody crop plantations and orchards) or an agroforestry system
# NO table for young forests
# NO table (for grass-dominated, wetlands, annual crops, developed area
#Table 4.7 (for coastal mangroves) in Chapter 4 of IPCC (2014)

# DEAD WOOD: NO tables
#Litter carbon stock and dead wood carbon stock are then assumed to be 50% and 40% total dry mass, respectively (IPCC 2006)

# SOIL ORGANIC MATTER
#Soil organic carbon (SOC) stocks for mineral soils are calculated to a default depth of 30 cm
#Table 2.3 in Chapter 2 of IPCC (2006) for habitat tree-dominated (natural or managed), grass- dominated (natural) or wetlands
#Table 5.2 of Chapter 5 of IPCC (2014) for inland wetland mineral soils 
#Table 5.3 of Chapter 5 of IPCC (2014) for factor of inland wetland mineral soils 
#Table 4.11 of Chapter 4 of IPCC (2014) for coastal wetland soils
#Table 6.2 in Chapter 6 of IPCC (2006) for factors on management
#Table 5.3 in Chapter 5 of IPCC (2006) for crop-dominated areas


def ImportIPCC_tables_A_CarbonStorage(iface, tool_path):
  
    #Table 2.2
    table_2_2_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_02_Ch2_Table2_2_LITTER_forest.csv"
    table_2_2_name = "V4_02_Ch2_Table2_2_LITTER_forest"
    IPCC_table_2_2 = iface.addVectorLayer(table_2_2_path, table_2_2_name, "ogr")

    # Table 2.3
    table_2_3_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_02_Ch2_Table2_3_SOC.csv"
    table_2_3_name = "V4_02_Ch2_Table2_3_SOC"
    IPCC_table_2_3 = iface.addVectorLayer(table_2_3_path, table_2_3_name, "ogr")

    #Table 4.3
    # import table 4.3 for carbon fraction of dry matter (CF) expressed in tonnes C (tonne dry mass)-1
    table_4_3_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_04_Ch4_Table4_3_CF_tree.csv"
    table_4_3_name = "V4_04_Ch4_Table4_3_CF_tree"
    IPCC_table_4_3 = iface.addVectorLayer(table_4_3_path, table_4_3_name, "ogr")

    #Table 4.4
    table_4_4_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_04_Ch4_Table4_4_BGB_tree.csv"
    table_4_4_name = "V4_04_Ch4_Table4_4_BGB_tree"
    IPCC_table_4_4 = iface.addVectorLayer(table_4_4_path, table_4_4_name, "ogr")

    #Table 4.5
    # import table 4.5 for biomass conversion and expansion factor (BCEF_R) for conversion of wood and fuelwood removals
    # to total above-ground biomass removals (including bark) expressed in [tonnes of biomass removal (m3 of biomass removals)-1]
    table_4_5_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_04_Ch4_Table4_5_BCEF_tree.csv"
    table_4_5_name = "V4_04_Ch4_Table4_5_BCEF_tree"
    IPCC_table_4_5 = iface.addVectorLayer(table_4_5_path, table_4_5_name, "ogr")

    #Table 4.7 
    table_4_7_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_04_Ch4_Table4_7_AGB_natural.csv"
    table_4_7_name = "V4_04_Ch4_Table4_7_AGB_natural"
    #IPCC_table_4_7 = QgsVectorLayer(table_4_7_path, table_4_7_name, "ogr")
    IPCC_table_4_7 = iface.addVectorLayer(table_4_7_path, table_4_7_name, "ogr")

    # Table 5.2, 2014
    table_5_2_2014_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/WS_Ch5_Table5_2_SOC_wetland.csv"
    table_5_2_2014_name = "WS_Ch5_Table5_2_SOC_wetland"
    IPCC_table_5_2_2014 = iface.addVectorLayer(table_5_2_2014_path, table_5_2_2014_name, "ogr")
    
    # Table 5.3, 2014
    table_5_3_2014_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/WS_Ch5_Table5_3_SOC_crops.csv"
    table_5_3_2014_name = "WS_Ch5_Table5_3_SOC_crops"
    IPCC_table_5_3_2014 = iface.addVectorLayer(table_5_3_2014_path, table_5_3_2014_name, "ogr")

    #Table 5.5
    table_5_5_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_05_Ch5_Table5_5_factors_crops.csv"
    table_5_5_name = "V4_05_Ch5_Table5_5_factors_crops"
    IPCC_table_5_5 = iface.addVectorLayer(table_5_5_path, table_5_5_name, "ogr")
    
    #Table 6.1
    table_6_1_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_06_Ch6_Table6_1_BGB_grass.csv"
    table_6_1_name = "V4_06_Ch6_Table6_1_BGB_grass"
    IPCC_table_6_1 = iface.addVectorLayer(table_6_1_path, table_6_1_name, "ogr")

    #Table 6.2
    table_6_2_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/V4_06_Ch6_Table6_2_factors_grass.csv"
    table_6_2_name = "V4_06_Ch6_Table6_2_factors_grass"
    IPCC_table_6_2 = iface.addVectorLayer(table_6_2_path, table_6_2_name, "ogr")


    # OTHER TABLES
    # Global Forest Resources Assessment (FRA) 2015 is then needed to know the Growing Stock level in m3/ha
    # get data from FAO table: FAO_ForestResourcesAssessment_2015
    table_FAO_FRA2015_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/FAO_ForestResourcesAssessment_2015.csv"
    table_FAO_FRA2015_name = "FAO_ForestResourcesAssessment_2015"
    table_FAO_FRA2015 = iface.addVectorLayer(table_FAO_FRA2015_path, table_FAO_FRA2015_name, "ogr")

    #Table Anderson-Teixeira and deLucia, 2011
    table_Anderson_Teixera_2011_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/Alternative_Table_Biomass_MineralSoil.csv"
    table_Anderson_Teixera_2011_name = "Alternative_Table_Biomass_MineralSoil"
    table_Anderson_Teixera_2011 = iface.addVectorLayer(table_Anderson_Teixera_2011_path, table_Anderson_Teixera_2011_name, "ogr")
    
    # import FAOSTAT table to get 'Fuelwood_removal_m3_yr', 'Roundwood_removal_m3_yr', 'Charcoal_removal_tonnes_yr'
    table_FAOSTAT_wood_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/FAOSTAT_WOOD_PRODUCTION_TOTAL.csv"
    table_FAOSTAT_wood_name = "FAOSTAT_WOOD_PRODUCTION_TOTAL"
    table_FAOSTAT_wood = iface.addVectorLayer(table_FAOSTAT_wood_path, table_FAOSTAT_wood_name, "ogr")
    
    # import FAOSTAT table of land uses areas
    table_FAOSTAT_landuse_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/FAOSTAT_data_LandUse_specific.csv"
    table_FAOSTAT_landuse_name = "FAOSTAT_data_LandUse_specific"
    table_FAOSTAT_landuse = iface.addVectorLayer(table_FAOSTAT_landuse_path, table_FAOSTAT_landuse_name, "ogr")
    
    # import trees' growing rates table  FAO_2003_PFDB_MeanAnnualIncrement_trees
    table_FAOSTAT_MAI_path = tool_path + "InputData_ES/A_Climate_CarbonStorage_tables/FAO_2003_PFDB_MeanAnnualIncrement_trees.csv"
    table_FAOSTAT_MAI_name = "FAO_2003_PFDB_MeanAnnualIncrement_trees"
    table_FAOSTAT_MAI = iface.addVectorLayer(table_FAOSTAT_MAI_path, table_FAOSTAT_MAI_name, "ogr")    
    
    # return all tables
    return IPCC_table_2_2, IPCC_table_2_3, IPCC_table_4_3, IPCC_table_4_4, IPCC_table_4_5, IPCC_table_4_7, IPCC_table_5_2_2014, IPCC_table_5_3_2014, IPCC_table_5_5, IPCC_table_6_1, IPCC_table_6_2, table_FAO_FRA2015, table_Anderson_Teixera_2011, table_FAOSTAT_wood, table_FAOSTAT_landuse, table_FAOSTAT_MAI



def ImportIPCC_tables_B_GHGSequestration(iface, tool_path):

    #Table 2.1 (2014)
    table_2_1_2014_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/WS_Chp2_Table_2_1_EFCO2.csv"
    table_2_1_2014_name = "WS_Chp2_Table_2_1_EFCO2"
    IPCC_table_2_1_2014 = iface.addVectorLayer(table_2_1_2014_path, table_2_1_2014_name, "ogr")
    
    #Table 2.2 (2014)
    table_2_2_2014_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/WS_Chp2_Table_2_2_EFDOC.csv"
    table_2_2_2014_name = "WS_Chp2_Table_2_2_EFDOC"
    IPCC_table_2_2_2014 = iface.addVectorLayer(table_2_2_2014_path, table_2_2_2014_name, "ogr")
    
    #Table 2.3 (2014)
    table_2_3_2014_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/WS_Chp2_Table_2_3_EFCH4.csv"
    table_2_3_2014_name = "WS_Chp2_Table_2_3_EFCH4"
    IPCC_table_2_3_2014 = iface.addVectorLayer(table_2_3_2014_path, table_2_3_2014_name, "ogr")
    
    #Table 2.4 (2014)
    table_2_4_2014_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/WS_Chp2_Table_2_4_EFCH4_ditches.csv"
    table_2_4_2014_name = "WS_Chp2_Table_2_4_EFCH4_ditches"
    IPCC_table_2_4_2014 = iface.addVectorLayer(table_2_4_2014_path, table_2_4_2014_name, "ogr")
    
    #Table 3.3 (2014)
    table_3_3_2014_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/WS_Chp3_Table_3_3_EFCH4_rewetted.csv"
    table_3_3_2014_name = "WS_Chp3_Table_3_3_EFCH4_rewetted"
    IPCC_table_3_3_2014 = iface.addVectorLayer(table_3_3_2014_path, table_3_3_2014_name, "ogr")
  
    #Table 10.10
    table_10_10_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/V4_10_Ch10_Table10_10_EFLivestock_devCountries.csv"
    table_10_10_name = "V4_10_Ch10_Table10_10_EFLivestock_devCountries"
    IPCC_table_10_10 = iface.addVectorLayer(table_10_10_path, table_10_10_name, "ogr")
    
    #Table 10.11
    table_10_11_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/V4_10_Ch10_Table10_11_EFCattle.csv"
    table_10_11_name = "V4_10_Ch10_Table10_10_EFLivestock_devCountries"
    IPCC_table_10_11 = iface.addVectorLayer(table_10_11_path, table_10_11_name, "ogr")
    
    #Table 10.11
    table_3A_2_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/V4_p_Ap3_Table_3A_2_EFCH4_flooded.csv"
    table_3A_2_name = "V4_p_Ap3_Table_3A_2_EFCH4_flooded"
    IPCC_table_3A_2 = iface.addVectorLayer(table_3A_2_path, table_3A_2_name, "ogr")
    
    
    return IPCC_table_2_1_2014, IPCC_table_2_2_2014, IPCC_table_2_3_2014, IPCC_table_2_4_2014,IPCC_table_3_3_2014, IPCC_table_10_10, IPCC_table_10_11, IPCC_table_3A_2



def ImportEUROSTAT_tables_B_GHGSequestration(iface, tool_path ):
    #Table animals in NUTS2 regions
    table_animalsNUTS2_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/Animal_populations_NUTS2_EUROPE.csv"
    table_animalsNUTS2_name = "Animal_populations_NUTS2_EUROPE"
    EUROSTAT_table_animals_NUTS2 = iface.addVectorLayer(table_animalsNUTS2_path, table_animalsNUTS2_name, "ogr")
    return EUROSTAT_table_animals_NUTS2


def ImportTESSA_tables_B_GHGsequestration(iface,tool_path ):
    # TESSA_M11_5_A_EF_naturalWetlands
    table_TESSA_naturalWetlands_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/TESSA_M11_5_A_EF_naturalWetlands.csv"
    table_TESSA_naturalWetlands_name = "TESSA_M11_5_A_EF_naturalWetlands"
    table_TESSA_naturalWetlands = iface.addVectorLayer(table_TESSA_naturalWetlands_path, table_TESSA_naturalWetlands_name, "ogr")
    return table_TESSA_naturalWetlands


def ImportFAO_tables_B_GHGSequestration(iface,tool_path ):
    #Table animals in NUTS2 regions
    table_agricultureEmissions_path = tool_path + "InputData_ES/B_Climate_GHGsequestration_tables/FAOSTAT_Danube_Agriculture_Total_emissions.csv"
    table_agricultureEmissions_name = "FAOSTAT_Danube_Agriculture_Total_emissions"
    FAO_table_agricultureEmissions = iface.addVectorLayer(table_agricultureEmissions_path, table_agricultureEmissions_name, "ogr")
    return FAO_table_agricultureEmissions





