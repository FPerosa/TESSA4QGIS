# B: CLIMATE - GHG SEQUESTRATION 
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
     QgsVectorLayer,
     QgsProject
)

from qgis.analysis import QgsZonalStatistics
from osgeo import gdal

# -------------------------------------------------------------------------------------------------------------
# -- IMPORT PATH  --
# -------------------------------------------------------------------------------------------------------------

tool_path = QgsProject.instance().readPath("./")+"/DanubeFloodplain_ES_Assessment_Tool/"


# -------------------------------------------------------------------------------------------------------------
# -- IMPORT LIBRARY  --
# -------------------------------------------------------------------------------------------------------------
sys.path.insert(1, (tool_path +'Library_v3'))
from Functions_FloodRisk2_plugin import *
from Import_A_Climate_CarbonStorage_tables import *
from Import_A_Climate_CarbonStorage_spatial import *
from Functions_B_Climate_GHGsequestration_readTables import *
from Functions_A_Climate_CarbonStorage_calculateResults import *




# -------------------------------------------------------------------------------------------------------------
# -- IMPORT DATA  --
# -------------------------------------------------------------------------------------------------------------

pilotArea_name = "Morava"
scenarioID = "RS2" # "CS"  #"RS2"
# extent_string = '4737175.0667000003159046,4745089.6848000008612871,2540966.9436000008136034,2548970.6923999991267920 [EPSG:3035]' # Krka
# extent_string = '5071018.729725715,5075106.2532,2503956.0776000004,2506340.2203252995 [EPSG:3035]' # Begecka Jama


# Import IPCC tables 
IPCC_table_2_1_2014, IPCC_table_2_2_2014, IPCC_table_2_3_2014, IPCC_table_2_4_2014,IPCC_table_3_3_2014, IPCC_table_10_10, IPCC_table_10_11, IPCC_table_3A_2 = ImportIPCC_tables_B_GHGSequestration(iface,tool_path)

# Import EUROSTAT tables
EUROSTAT_table_animals_NUTS2 = ImportEUROSTAT_tables_B_GHGSequestration(iface,tool_path)

# Import FAO tables
FAO_table_agricultureEmissions = ImportFAO_tables_B_GHGSequestration(iface,tool_path)

#Import spatialdata
NUTS2_regions = Import_NUTS2_regions_shp(iface,tool_path)
Danube_countries = Import_Danube_countries_shp(iface,tool_path)
# Danube_countries_agriculture =  Import_Danube_countries_agr_shp(iface)
AreaAnalysis_layer = Import_AnalysisArea_shp(iface,tool_path,pilotArea_name)


# SHAPEFILE ExtCBA_2 
ExtCBA2_EcosystemTypes_layer = Import_HabitatType_ExtCBA2(iface,tool_path,pilotArea_name,scenarioID)

# Shapefile with the categry of the wetland
ExtCBA_6_wetlandCategory = Import_wetlandCategory_ExtCBA6(iface, tool_path,pilotArea_name,scenarioID)


# -------------------------------------------------------------------------------------------------------------
# -- AREA CHARACTERISTICS  --
# -------------------------------------------------------------------------------------------------------------
#MUST BE CHANGED -------------------------------------------------------------------------------------------------------
# AREA CHARACTERISTICS - beginning -------------------------------------------------------------------------------


# define area characteristics 
climate_reg = "Temperate"
climate_reg2 = "Warm dry"
climate_reg3 = "Warm temperate dry" 
continent = "Europe"
country = "Czech Republic"
country2 = "Czechia"
if country == "Germany" or country == "Austria":
    eastWest_europe = "Western Europe"
elif country == "Bosnia and Herzegovina" or country == "Czech Republic" or country == "Slovakia" or country == "Romania" or country == "Serbia" or country == "Slovenia" or country == "Ukraine" or country == "Croatia" or country == "Hungary" or country == "Moldova":
    eastWest_europe = "Eastern Europe"

NUTS2_region = "CZ06"
forest_ecoZone = "Temperate continental forest" # or "Temperate scrub/woodland"

# for CO2 emissions
soil_type = "organic" # choose between "organic" or "mineral"
DrainedOrganicSoils = 1
Percentage_Drained_Tree = 0.1
Percentage_Drained_Grass = 0.1
Percentage_Drained_Crops = 0.1

LandUse_grassland = "Grassland shallow-drained nutrient-rich" # "Grassland drained nutrient-poor" # or "Grassland deep-drained nutrient-rich" or "Grassland shallow-drained nutrient-rich"

# for CH4 emissions
heads_livestock_available=0 # in tot number/year and not per hectare!

statisticsYear = 2018
domesticAnimals_pilotArea = ["Other cattle","Horses"] # ["Buffalo", "Sheep", "Goats", "Camels", "Horses", "Mules ans Asses", "Deer", "Alpacas", "Swine","Dairy", "Other cattle"]
Heads_bovine_per_yr =  None
Heads_dairyCows_per_yr = None
Heads_pigs_per_yr=  None
Heads_sheep_per_yr=  None
Heads_goats_per_yr=  None

# Krka: Deer cca. 300-350 individuals, wild boar cca. 50 individuals
wildGrazers_presence = 1
wildGrazers_pilotArea = ["Small deer", "Large deer"]
#Heads_moose_per_yr_ha = 0
#Heads_elk_per_yr_ha = 0
#Heads_largeDeer_per_yr_ha = 0
#Heads_caribou_per_yr_ha = 0
Heads_smallDeer_per_yr_ha = 1500
Heads_largeDeer_per_yr_ha = 500
heads_wildGrazers_pilotArea_per_yr_ha = [wildGrazers_pilotArea, [Heads_smallDeer_per_yr_ha,Heads_largeDeer_per_yr_ha]]
#[Heads_moose_per_yr_ha,Heads_elk_per_yr_ha,Heads_largeDeer_per_yr_ha,Heads_caribou_per_yr_ha,Heads_smallDeer_per_yr_ha] ]

#Heads_moose_per_yr = 0
#Heads_elk_per_yr = 0
#Heads_largeDeer_per_yr = 0
#Heads_caribou_per_yr = 0
#Heads_smallDeer_per_yr = 0
#heads_wildGrazers_pilotArea_per_yr = [wildGrazers_pilotArea, 
#[Heads_moose_per_yr,Heads_elk_per_yr,Heads_largeDeer_per_yr,Heads_caribou_per_yr,Heads_smallDeer_per_yr] ]

# heads_wildGrazers_pilotArea_per_yr = [wildGrazers_pilotArea, [Heads_smallDeer_per_yr] ]
heads_wildGrazers_pilotArea_per_yr = None

# for CH4 emissions
IceFree_days_per_year = 330




# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- CO2 EEMISSIONS from DRAINED SOILS
# -------------------------------------------------------------------------------------------------------------
#For managed, drained, un-rewetted habitats on organic soils: 
#See Tables 2.1 & 2.2 in Chapter 2 of IPCC (2014), to select the appropriate default emissions factors as
#annual flux of carbon as CO2 from on-site oxidation or sequestration and off-site Dissolved Organic Carbon
#(EFDOCdrained) aquatic fluxes (expressed in tonnes C ha-1 y-1). These emissions factors are additive

# if DrainedOrganicSoils==1:

# Create copy of layer
GHG_layer = createCopy_habitatsShapefile(ExtCBA2_EcosystemTypes_layer, 'B_climate_output02_GHG')

# Get % of the land uses that have been drained
Percentage_Drained_Tree
Percentage_Drained_Grass
Percentage_Drained_Crops

# Calculate area of drained land and estimate the total emissions
myField = QgsField( 'DrainedArea_ha', QVariant.Double )
GHG_layer.dataProvider().addAttributes([myField])
myField = QgsField( 'EF_CO2_tonCO2_per_ha_yr', QVariant.Double )
GHG_layer.dataProvider().addAttributes([myField])
myField = QgsField( 'CO2_Emissions_tonCO2_per_yr', QVariant.Double )
GHG_layer.dataProvider().addAttributes([myField])
GHG_layer.updateFields()
idx_HA = GHG_layer.fields().indexFromName('Area_ha')
idx_DHA = GHG_layer.fields().indexFromName('DrainedArea_ha')
idx_EFco2 = GHG_layer.fields().indexFromName('EF_CO2_tonCO2_per_ha_yr')
idx_CO2em = GHG_layer.fields().indexFromName('CO2_Emissions_tonCO2_per_yr')
id_habitat_code = GHG_layer.fields().indexFromName('Habit_Code')
#start editing
GHG_layer.startEditing()
for f in GHG_layer.getFeatures():
    # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
    if f[id_habitat_code] == 1 : # tree-dominated
        # area
        f[idx_DHA] = float(f[idx_HA])*Percentage_Drained_Tree
        # EF
        EF_Tree_tonCO2_per_ha_yr = readTable_IPCC_2_1_2014(IPCC_table_2_1_2014,"Forest Land drained")
        f[idx_EFco2] = EF_Tree_tonCO2_per_ha_yr
        # Emissions
        CO2emissions_tonCO2_per_yr = EF_Tree_tonCO2_per_ha_yr * f[idx_DHA]
        f[idx_CO2em] = CO2emissions_tonCO2_per_yr
        # update the feature
        GHG_layer.updateFeature( f )
    elif f[id_habitat_code] == 2 : #grass-dominated
        # area
        f[idx_DHA] = float(f[idx_HA])*Percentage_Drained_Grass
        # EF
        EF_Grass_tonCO2_per_ha_yr = readTable_IPCC_2_1_2014(IPCC_table_2_1_2014,LandUse_grassland)
        f[idx_EFco2] = EF_Grass_tonCO2_per_ha_yr
        # Emissions
        CO2emissions_tonCO2_per_yr = EF_Grass_tonCO2_per_ha_yr * f[idx_DHA]
        f[idx_CO2em] = CO2emissions_tonCO2_per_yr
        # update the feature
        GHG_layer.updateFeature( f )
    elif f[id_habitat_code] == 3 : #crop-dominated, no rice
        # area
        f[idx_DHA] = float(f[idx_HA])*Percentage_Drained_Crops
        # EF
        EF_Crops_tonCO2_per_ha_yr = readTable_IPCC_2_1_2014(IPCC_table_2_1_2014,"Cropland drained")
        f[idx_EFco2] = EF_Crops_tonCO2_per_ha_yr
        # Emissions
        CO2emissions_tonCO2_per_yr = EF_Crops_tonCO2_per_ha_yr * f[idx_DHA]
        f[idx_CO2em] = CO2emissions_tonCO2_per_yr
        # update the feature
        GHG_layer.updateFeature( f )
    elif f[id_habitat_code] == 4 : #crop-dominated, rice
        # area
        f[idx_DHA] = float(f[idx_HA])*Percentage_Drained_Crops
        # EF
        EF_Crops_tonCO2_per_ha_yr = readTable_IPCC_2_1_2014(IPCC_table_2_1_2014,"Cropland drained")
        f[idx_EFco2] = EF_Crops_tonCO2_per_ha_yr
        # Emissions
        CO2emissions_tonCO2_per_yr = EF_Crops_tonCO2_per_ha_yr * f[idx_DHA]
        f[idx_CO2em] = CO2emissions_tonCO2_per_yr
        # update the feature
        GHG_layer.updateFeature( f )
    else:
        f[idx_CO2em] = 0.0
        # update the feature
        GHG_layer.updateFeature( f )

# commit changes
GHG_layer.commitChanges()


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- CH4 EMISSIONS from GRAZING ANIMALS
# -------------------------------------------------------------------------------------------------------------
#you need to have a reliable estimate of the number of domestic animals present and/or a population estimate for wild grazers

if (heads_livestock_available==0):
    # DOMESTIC ANIMALS ---
    # get NUTS2 region area
    features_table = NUTS2_regions.getFeatures()
    idx_HA = NUTS2_regions.fields().indexFromName("Area_ha")
    idx_NUTS2 = NUTS2_regions.fields().indexFromName("NUTS_ID")
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_NUTS2]== NUTS2_region :
            feat_value = feat
            NUTS2_area_ha = float(feat_value[idx_HA])
    
    # get heads of livestock 
    Heads_bovine_per_yr_ha, Heads_dairyCows_per_yr_ha, Heads_pigs_per_yr_ha, Heads_sheep_per_yr_ha, Heads_goats_per_yr_ha = readTable_EUROSTAT_animals(EUROSTAT_table_animals_NUTS2,NUTS2_region,NUTS2_area_ha,statisticsYear)
    
    # calculate the CH4 emissions 
    CH4emissions_domesticAnimal_tonCH4_per_ha_yr = 0
    
    for domesticAnimal in domesticAnimals_pilotArea:
        # get EF for CH4 for specific animal
        EF_CH4_domesticAnimal = readTable_IPCC_Ch10_10_11(IPCC_table_10_10, IPCC_table_10_11,domesticAnimal,eastWest_europe)
        print("EF CH4 for livestock " + domesticAnimal+ ": " + str(EF_CH4_domesticAnimal) + " kgCH4/head*yr")
        # calculate emissions
        if domesticAnimal == "Dairy":
            CH4emissions_Dairy_tonCH4_per_yr_ha = EF_CH4_domesticAnimal*Heads_dairyCows_per_yr_ha/1000
            CH4emissions_domesticAnimal_tonCH4_per_ha_yr = numpy.nansum([CH4emissions_Dairy_tonCH4_per_yr_ha,CH4emissions_domesticAnimal_tonCH4_per_ha_yr])
        elif domesticAnimal == "Other cattle":
            CH4emissions_otherCattle_tonCH4_per_yr_ha = EF_CH4_domesticAnimal*Heads_bovine_per_yr_ha/1000
            CH4emissions_domesticAnimal_tonCH4_per_ha_yr = numpy.nansum([CH4emissions_otherCattle_tonCH4_per_yr_ha,CH4emissions_domesticAnimal_tonCH4_per_ha_yr])
        elif domesticAnimal == "Sheep":
            CH4emissions_Sheep_tonCH4_per_yr_ha = EF_CH4_domesticAnimal*Heads_sheep_per_yr_ha/1000
            CH4emissions_domesticAnimal_tonCH4_per_ha_yr = numpy.nansum([CH4emissions_Sheep_tonCH4_per_yr_ha,CH4emissions_domesticAnimal_tonCH4_per_ha_yr])
        elif domesticAnimal == "Goats":
            CH4emissions_Goats_tonCH4_per_yr_ha = EF_CH4_domesticAnimal*Heads_goats_per_yr_ha/1000
            CH4emissions_domesticAnimal_tonCH4_per_ha_yr = numpy.nansum([CH4emissions_Goats_tonCH4_per_yr_ha,CH4emissions_domesticAnimal_tonCH4_per_ha_yr])
        elif domesticAnimal == "Swine":
            CH4emissions_Swine_tonCH4_per_yr_ha = EF_CH4_domesticAnimal*Heads_pigs_per_yr_ha/1000
            CH4emissions_domesticAnimal_tonCH4_per_ha_yr = numpy.nansum([CH4emissions_Swine_tonCH4_per_yr_ha,CH4emissions_domesticAnimal_tonCH4_per_ha_yr])
elif (heads_livestock_available==1):
    print("Bovine count in region (manually given): " + str(Heads_bovine_per_yr) + " heads/yr/ha")
    print("Dairy cows count in region (manually given): " + str(Heads_dairyCows_per_yr) + " heads/yr/ha")
    print("Pigs count in region (manually given): " + str(Heads_pigs_per_yr) + " heads/yr/ha")
    print("Sheep count in region (manually given): " + str(Heads_sheep_per_yr) + " heads/yr/ha")
    print("Goats count in region (manually given): " + str(Heads_goats_per_yr) + " heads/yr/ha")
    
    # calculate the CH4 emissions 
    CH4emissions_domesticAnimal_tonCH4_per_yr = 0
    
    for domesticAnimal in domesticAnimals_pilotArea:
        # get EF for CH4 for specific animal
        EF_CH4_domesticAnimal = readTable_IPCC_Ch10_10_11(IPCC_table_10_10, IPCC_table_10_11,domesticAnimal,eastWest_europe)
        print("EF CH4 for livestock " + domesticAnimal+ ": " + str(EF_CH4_domesticAnimal) + " kgCH4/head*yr")
        # calculate emissions
        if domesticAnimal == "Dairy":
            CH4emissions_Dairy_tonCH4_per_yr = EF_CH4_domesticAnimal*Heads_dairyCows_per_yr/1000
            CH4emissions_domesticAnimal_tonCH4_per_ha = numpy.nansum([CH4emissions_Dairy_tonCH4_per_yr,CH4emissions_domesticAnimal_tonCH4_per_yr])
        elif domesticAnimal == "Other cattle":
            CH4emissions_otherCattle_tonCH4_per_yr = EF_CH4_domesticAnimal*Heads_bovine_per_yr/1000
            CH4emissions_domesticAnimal_tonCH4_per_yr = numpy.nansum([CH4emissions_otherCattle_tonCH4_per_yr,CH4emissions_domesticAnimal_tonCH4_per_yr])
        elif domesticAnimal == "Sheep":
            CH4emissions_Sheep_tonCH4_per_yr = EF_CH4_domesticAnimal*Heads_sheep_per_yr/1000
            CH4emissions_domesticAnimal_tonCH4_per_yr = numpy.nansum([CH4emissions_Sheep_tonCH4_per_yr,CH4emissions_domesticAnimal_tonCH4_per_yr])
        elif domesticAnimal == "Goats":
            CH4emissions_Goats_tonCH4_per_yr = EF_CH4_domesticAnimal*Heads_goats_per_yr/1000
            CH4emissions_domesticAnimal_tonCH4_per_yr = numpy.nansum([CH4emissions_Goats_tonCH4_per_yr,CH4emissions_domesticAnimal_tonCH4_per_yr])
        elif domesticAnimal == "Swine":
            CH4emissions_Swine_tonCH4_per_yr = EF_CH4_domesticAnimal*Heads_pigs_per_yr/1000
            CH4emissions_domesticAnimal_tonCH4_per_yr = numpy.nansum([CH4emissions_Swine_tonCH4_per_yr,CH4emissions_domesticAnimal_tonCH4_per_yr])


# WILD ANIMALS ---
if wildGrazers_presence == 0:
    CH4emissions_wildGrazers_tonCH4_per_ha_yr = 0
    CH4emissions_wildGrazers_tonCH4_per_yr = 0
elif wildGrazers_presence == 1:
    CH4emissions_wildGrazers_tonCH4_per_ha_yr = 0
    CH4emissions_wildGrazers_tonCH4_per_yr = 0
    #Table of CH4 emissions of wild grazers 
    table_TESSA_wildGrazers_path = tool_path + "/InputData_ES/B_Climate_GHGsequestration_tables/TESSA_M11_4_B_EF_wildGrazer.csv"
    table_TESSA_wildGrazers_name = "TESSA_M11_4_B_EF_wildGrazer"
    table_TESSA_wildGrazers = iface.addVectorLayer(table_TESSA_wildGrazers_path, table_TESSA_wildGrazers_name, "ogr")
    # to finish ---------------------------
    # import info on number of wild grazers
    # get EF from table TESSA-M11
    for i in range(len(wildGrazers_pilotArea)):
        wildGrazer = wildGrazers_pilotArea[i]
        EF_CH4_wildGrazer = readTable_TESSA_M11(table_TESSA_wildGrazers, wildGrazer)
        if (heads_livestock_available==0):
            # calculate emissions per ha
            CH4emissions_wildGrazerTMP_tonCH4_per_yr_ha = EF_CH4_wildGrazer*heads_wildGrazers_pilotArea_per_yr_ha[1][i]/1000
            # sum emissions for different wild grazers types
            CH4emissions_wildGrazers_tonCH4_per_ha_yr += CH4emissions_wildGrazerTMP_tonCH4_per_yr_ha
        elif (heads_livestock_available==1):
            # calculate emissions per year
            CH4emissions_wildGrazerTMP_tonCH4_per_yr = EF_CH4_wildGrazer*heads_wildGrazers_pilotArea_per_yr[1][i]/1000
            # sum emissions for different wild grazers types
            CH4emissions_wildGrazers_tonCH4_per_yr += CH4emissions_wildGrazerTMP_tonCH4_per_yr



# TOTAL CH4 EMISSIONS FROM GRAZERS per ha 
if (heads_livestock_available==0):
    CH4emissions_totalGrazers_tonCH4_per_ha_yr = numpy.nansum([CH4emissions_domesticAnimal_tonCH4_per_ha_yr, CH4emissions_wildGrazers_tonCH4_per_ha_yr])
elif (heads_livestock_available==1):
    CH4emissions_totalGrazers_tonCH4_per_yr = numpy.nansum([CH4emissions_domesticAnimal_tonCH4_per_yr, CH4emissions_wildGrazers_tonCH4_per_yr])


# TOTAL CH4 EMISSIONS FROM GRAZERS ---
if (heads_livestock_available==0):
    # Calculate area of drained land and estimate the total emissions
    myField = QgsField( 'EF_CH4_totalGrazers_tonCH4_per_ha_yr', QVariant.Double )
    GHG_layer.dataProvider().addAttributes([myField])
    myField = QgsField( 'CH4_Emissions_totalGrazers_tonCH4_per_yr', QVariant.Double )
    GHG_layer.dataProvider().addAttributes([myField])
    GHG_layer.updateFields()
    idx_HA = GHG_layer.fields().indexFromName('Area_ha')
    id_habitat_code = GHG_layer.fields().indexFromName('Habit_Code')
    id_EFCH4 = GHG_layer.fields().indexFromName('EF_CH4_totalGrazers_tonCH4_per_ha_yr')
    id_CH4 = GHG_layer.fields().indexFromName('CH4_Emissions_totalGrazers_tonCH4_per_yr')
    
    #start editing
    GHG_layer.startEditing()
    for f in GHG_layer.getFeatures():
        if f[id_habitat_code] == 2 : #grass-dominated
            # EF
            f[id_EFCH4] = CH4emissions_totalGrazers_tonCH4_per_ha_yr
            # Emissions
            f[id_CH4] = CH4emissions_totalGrazers_tonCH4_per_ha_yr * f[idx_HA]
            # print
            print("CH4emissions_totalGrazers_tonCH4_per_ha_yr : " + str(f[id_CH4]))
            # update the feature
            GHG_layer.updateFeature( f )
        else:
            # Emissions
            f[id_CH4] = 0.0
            GHG_layer.updateFeature( f )
    # commit changes
    GHG_layer.commitChanges()
elif (heads_livestock_available==1):
    # write txt file with result 
    output_txt_file_path = tool_path + "OutputData_ES/B_climate_GHG/CH4emissions_totalGrazers_tonCH4_per_yr_"+ scenarioID +".txt"
    file_to_write = open(output_txt_file_path, 'w')
    file_to_write.write(str("CH4emissions_totalGrazers_tonCH4_per_yr: " + str(CH4emissions_totalGrazers_tonCH4_per_yr)+ " tons CH4/year"+'\n'+
    "CH4emissions_totalGrazers_tonCO2eq_per_yr: " + str(CH4emissions_totalGrazers_tonCH4_per_yr*28.0)+ " tons C02eq/year"+'\n'))
    # close 
    file_to_write.close()
    
    # create dummy column in GHG_layer
    myField = QgsField( 'CH4_Emissions_totalGrazers_tonCH4_per_yr', QVariant.Double )
    GHG_layer.dataProvider().addAttributes([myField])
    GHG_layer.updateFields()
    id_CH4 = GHG_layer.fields().indexFromName('CH4_Emissions_totalGrazers_tonCH4_per_yr')
    #start editing
    GHG_layer.startEditing()
    for f in GHG_layer.getFeatures():
        # Emissions
        f[id_CH4] = 0.0
        GHG_layer.updateFeature( f )
    GHG_layer.commitChanges()

# apply the value to the spatial GHG file (grazers admitted only on grasslands)
# C_EQ_emissions_tonCO2_per_yr


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- CH4 EMISSIONS from WETLANDS
# -------------------------------------------------------------------------------------------------------------


if ExtCBA_6_wetlandCategory is not None: 
    # create a copy of ExtCBA_6
    CH4_wetlands_layer = createCopy_wetlandsShapefile(ExtCBA_6_wetlandCategory, "B_climate_output03_CH4")
    # import table for natural wetlands
    table_TESSA_naturalWetlands = ImportTESSA_tables_B_GHGsequestration(iface,tool_path)
    # add column to the ExtCBA_6 file
    myField = QgsField( 'CH4_Emissions_wetlands_tonCH4_per_yr', QVariant.Double )
    CH4_wetlands_layer.dataProvider().addAttributes([myField])
    myField = QgsField( 'C_eq_Emissions_wetlands_tonC_per_yr', QVariant.Double )
    CH4_wetlands_layer.dataProvider().addAttributes([myField])
    CH4_wetlands_layer.updateFields()
    idx_HA = CH4_wetlands_layer.fields().indexFromName('Area_ha')
    idx_WET = CH4_wetlands_layer.fields().indexFromName('Category')
    idx_WETspec = CH4_wetlands_layer.fields().indexFromName('Specified')
    idx_SH = CH4_wetlands_layer.fields().indexFromName('Shunts_01')
    idx_LU = CH4_wetlands_layer.fields().indexFromName('LandUse')
    idx_NU = CH4_wetlands_layer.fields().indexFromName('Nutrients')
    idx_CH4 = CH4_wetlands_layer.fields().indexFromName('CH4_Emissions_wetlands_tonCH4_per_yr')
    #start editing
    CH4_wetlands_layer.startEditing()
    # calculate CH4emissions from wetlands
    for f in CH4_wetlands_layer.getFeatures():
        # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
        if f[idx_WET] == "Natural inland":
            if f[idx_WETspec]=="Distance to water table more than 20 cm":
                wetland_type_TESSAtable = "Dry"
            elif f[idx_WETspec]=="Distance to water table less than 20 cm" and f[idx_SH] == 0:
                wetland_type_TESSAtable = "Wet without shunts"
            elif f[idx_WETspec]=="Distance to water table less than 20 cm" and f[idx_SH] == 1:
                wetland_type_TESSAtable = "Wet with shunts"
            # get EF
            EF_CH4_wetland = readTable_TESSA_M11_5_A(table_TESSA_naturalWetlands, wetland_type_TESSAtable)
            print("Emissions wetland: " + str(EF_CH4_wetland*float(f[idx_HA])) + " tonCH4/yr")
            f[idx_CH4] = EF_CH4_wetland*float(f[idx_HA])
            CH4_wetlands_layer.updateFeature( f )
        elif f[idx_WET] == "Managed drained":
            # tables 2.3, 2.4 and 3.3
            if f[idx_WETspec]=="Drained not rewetted":
                EFland_tonCH4_per_ha_yr = readTable_IPCC_2_3_2014(IPCC_table_2_3_2014,f[idx_LU])
                EFditch_tonCH4_per_ha_yr, Frac_ditch = readTable_IPCC_2_4_2014(IPCC_table_2_4_2014, climate_reg,f[idx_LU])
                EF_tonCH4_per_ha_yr = EFland_tonCH4_per_ha_yr/(1-Frac_ditch) + EFditch_tonCH4_per_ha_yr*Frac_ditch
                f[idx_CH4] = EF_tonCH4_per_ha_yr *float(f[idx_HA])
            elif f[idx_WETspec]=="Drained and rewetted":
                EFrewet_tonCH4_per_ha_yr = readTable_IPCC_3_3_2014(IPCC_table_3_3_2014,climate_reg,f[idx_NU])
                EFditch_tonCH4_per_ha_yr, Frac_ditch = readTable_IPCC_2_4_2014(IPCC_table_2_4_2014, climate_reg,f[idx_LU])
                EF_tonCH4_per_ha_yr = EFrewet_tonCH4_per_ha_yr/(1-Frac_ditch) + EFditch_tonCH4_per_ha_yr*Frac_ditch
                f[idx_CH4] = EF_tonCH4_per_ha_yr*float(f[idx_HA])
            CH4_wetlands_layer.updateFeature( f )
        elif f[idx_WET] == "Managed not drained":
            if f[idx_WETspec]=="Flooded":
                # table appendix 3A.2
                EF_tonCH4_per_ha_day = readTable_IPCC_3A_2(IPCC_table_3A_2,climate_reg3)
                EF_tonCH4_per_ha_year = EF_tonCH4_per_ha_day*IceFree_days_per_year
                f[idx_CH4] = EF_tonCH4_per_ha_yr*float(f[idx_HA])
                # number of ice-free days per year 
            if f[idx_WETspec]=="Rice field" or f[idx_WETspec]=="Wastewater treatment":
                print("No package available for "+ f[idx_WETspec]+ " yet!")
            CH4_wetlands_layer.updateFeature( f )
    # commit changes
    CH4_wetlands_layer.commitChanges()
else:
    print("No results from wetlands becauase no ExtCXBA_06 file was found")



# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- N2O EMISSIONS from DRAINED PEATLANDS
# -------------------------------------------------------------------------------------------------------------

print("No package available for N2O emission from drained peatlands yet!")


# ----------------------------------------------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- N2O EMISSIONS from AGRICULTURE TOTAL (instead of FERTILIZERS / GRAZING ANIMALS)
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# get emissions according to FAOSTAT
EmissionsCountry_tonN2O_per_yr = readTable_FAO_agricultureEmissions(FAO_table_agricultureEmissions, "2017", "Emissions (N2O)", "Agriculture total", country2)

# get area of agricultural land from CORINE 2018
# CORINE2018
CORINE18_raster_path = tool_path + "InputData_ES/0_Area_characteristics/CLC2018/clc2018_clc2018_v2018_20_raster100m/clc2018_clc2018_v2018_20_raster100m/CLC2018_CLC2018_V2018_20.tif"
CORINE18_raster_name = "CLC2018_CLC2018_V2018_20.tif"
CORINE18_raster = iface.addRasterLayer(CORINE18_raster_path, CORINE18_raster_name)


# add file CORINE18 with codes [211 to 244] as 1, the rest is 0 --> used to recognizes the areas with agriculture
CORINE18_agriculture_raster_path = tool_path + "InputData_ES/0_Area_characteristics/CLC2018_Agriculture1/CLC2018_Agriculture1.tif"
CORINE18_agriculture_raster_name = "CLC2018_Agriculture1.tif"
CORINE18_agriculture_raster = iface.addRasterLayer(CORINE18_agriculture_raster_path, CORINE18_agriculture_raster_name)

#Extact cropland area from CORINE18 raster file and the Danube_countries shapefile
band_CORINE18=1
Danube_countries.startEditing()
zonalstats = QgsZonalStatistics( Danube_countries, CORINE18_agriculture_raster, 'HA_agr_', band_CORINE18, QgsZonalStatistics.Sum)
zonalstats.calculateStatistics( None )
Danube_countries.commitChanges()
# get cropland area in country in hectares
idx_country = Danube_countries.fields().indexFromName("NAME_ENGL")
idx_agr_ha = Danube_countries.fields().indexFromName("HA_agr_sum")
features_table = Danube_countries.getFeatures()
for feat in features_table:
    attributes_table = feat.attributes()
    if attributes_table[idx_country]== country :
        feat_value = feat
        Area_harvestable_country_ha = float(feat_value[idx_agr_ha])

# Extact cropland area from CORINE18 raster file and the PilotArea shapefile
band_CORINE18=1
AreaAnalysis_layer.startEditing()
zonalstats = QgsZonalStatistics( AreaAnalysis_layer, CORINE18_agriculture_raster, 'HA_agr_', band_CORINE18, QgsZonalStatistics.Sum)
zonalstats.calculateStatistics( None )
AreaAnalysis_layer.commitChanges()
# get cropland area in pilot area in hectares
idx_agr_ha = AreaAnalysis_layer.fields().indexFromName("HA_agr_sum")
features_table = AreaAnalysis_layer.getFeatures()
for feat in features_table:
    attributes_table = feat.attributes()
    feat_value = feat
    Area_harvestable_pilotArea_ha = float(feat_value[idx_agr_ha])


# extract value per yr and ha emissions according to FAOSTAT
Emissions_tonN2O_per_yr_ha = EmissionsCountry_tonN2O_per_yr/Area_harvestable_country_ha


# TOTAL N2O EMISSIONS FROM AGRICULTURE ---
myField = QgsField( 'EF_N2O_totalAgriculture_tonN2O_per_ha_yr', QVariant.Double )
GHG_layer.dataProvider().addAttributes([myField])
myField = QgsField( 'N2O_Emissions_totalAgriculture_tonN2O_per_yr', QVariant.Double )
GHG_layer.dataProvider().addAttributes([myField])
GHG_layer.updateFields()
idx_HA = GHG_layer.fields().indexFromName('Area_ha')
id_habitat_code = GHG_layer.fields().indexFromName('Habit_Code')
id_EFN2O = GHG_layer.fields().indexFromName('EF_N2O_totalAgriculture_tonN2O_per_ha_yr')
id_N2O = GHG_layer.fields().indexFromName('N2O_Emissions_totalAgriculture_tonN2O_per_yr')

#start editing
GHG_layer.startEditing()
for f in GHG_layer.getFeatures():
    if f[id_habitat_code] == 2 or f[id_habitat_code] == 3 : #grass-dominated and crop-dominated
        # EF
        f[id_EFN2O] = Emissions_tonN2O_per_yr_ha
        # Emissions
        f[id_N2O] = Emissions_tonN2O_per_yr_ha * f[idx_HA]
        # update the feature
        GHG_layer.updateFeature( f )
    else:
        f[id_N2O] = 0.0
        # update the feature
        GHG_layer.updateFeature( f )

# commit changes
GHG_layer.commitChanges()


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- CO2 EQUIVALENT
# -------------------------------------------------------------------------------------------------------------
#Separately, for each habitat at the site, pull together all your data on annual greenhouse gas fluxes and express
#in a single figure (tonnes per year), using Climate M14.

# Get the net C sequestration from the results of the previous part
Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr = 0.0

netCsequestration_layer = Import_output01b_carbon_seq_shp(iface,tool_path,scenarioID)

idx_NET = netCsequestration_layer.fields().indexFromName('NetCseq_to')
idx_HA = netCsequestration_layer.fields().indexFromName('Area_ha')
#start editing
Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr = 0.0
for f in netCsequestration_layer.getFeatures():
    Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr += f[idx_NET]




# 1) C sequestration from trees 
#Each atom of carbon sequestered represents one molecule of CO2 removed from the atmosphere. So, take the figure
#that you calculated for net carbon sequestration (t C y-1) and express this in terms of CO2 (t CO2y-1) by
#multiplying by 44/12. This is because the molecular weights of C and O are 12 and 16 respectively.
# EqCO2
EqCO2_NetCarbonSequestration_tonCO2_per_yr = Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr * 44.0/12.0


# 2) emissions from soil (sum over area)
if ExtCBA_6_wetlandCategory is not None:
    CH4_Emissions_wetlands_PiloArea_tonCH4_per_yr = 0.0
    idx_CH4 = CH4_wetlands_layer.fields().indexFromName('CH4_Emissions_wetlands_tonCH4_per_yr')
    for f in CH4_wetlands_layer.getFeatures():
        if f[idx_CH4]:
            CH4_Emissions_wetlands_PiloArea_tonCH4_per_yr = numpy.nansum( [CH4_Emissions_wetlands_PiloArea_tonCH4_per_yr, f[idx_CH4]])
else:
    CH4_Emissions_wetlands_PiloArea_tonCH4_per_yr = 0.0

# EqCO2
EqCO2_CH4_Emissions_wetlands_tonCO2_per_yr =  CH4_Emissions_wetlands_PiloArea_tonCH4_per_yr * 28 # without feedbacks


# 3) emissions from all habitats
# Convert the carbon dioxide, methane, and nitrous oxide fluxes to carbon dioxide equivalents, so that they can be
# added together to calculate the overall greenhouse gas flux

#the IPCC now publishes two GWP100 values, one that takes into account climate-carbon feedbacks (which measure the indirect
#effects of changes in carbon storage due to changes in climate) as well as one that doesn’t (which has been used
#previously, including in earlier versions of this toolkit).
#(1) GWP100 of methane is 28 (34)
#(2) GWP100 of nitrous oxide is 265 (298)

CO2_Emissions_PiloArea_tonCO2_per_yr = 0.0
N2O_Emissions_PiloArea_totalAgriculture_tonN2O_per_yr = 0.0
if heads_livestock_available==1:
    CH4_Emissions_totalGrazers_PiloArea_tonCH4_per_yr = CH4emissions_totalGrazers_tonCH4_per_yr
elif heads_livestock_available==0:
    CH4_Emissions_totalGrazers_PiloArea_tonCH4_per_yr = 0.0



# (sum over area)
id_CO2 = GHG_layer.fields().indexFromName('CO2_Emissions_tonCO2_per_yr')
id_CH4 = GHG_layer.fields().indexFromName('CH4_Emissions_totalGrazers_tonCH4_per_yr')
id_N2O = GHG_layer.fields().indexFromName('N2O_Emissions_totalAgriculture_tonN2O_per_yr')

for f in GHG_layer.getFeatures():
    if f[id_CO2]:
        CO2_Emissions_PiloArea_tonCO2_per_yr = numpy.nansum( [CO2_Emissions_PiloArea_tonCO2_per_yr, f[id_CO2]])
    if (heads_livestock_available==0):
        if f[id_CH4]:
            CH4_Emissions_totalGrazers_PiloArea_tonCH4_per_yr = numpy.nansum( [CH4_Emissions_totalGrazers_PiloArea_tonCH4_per_yr, f[id_CH4]])
    if f[id_N2O]:
        N2O_Emissions_PiloArea_totalAgriculture_tonN2O_per_yr = numpy.nansum( [N2O_Emissions_PiloArea_totalAgriculture_tonN2O_per_yr, f[id_N2O]])

EqCO2_CO2_Emissions_tonCO2_per_yr =                 CO2_Emissions_PiloArea_tonCO2_per_yr *1 # without feedbacks
EqCO2_CH4_Emissions_totalGrazers_tonCO2_per_yr =    CH4_Emissions_totalGrazers_PiloArea_tonCH4_per_yr * 28 # without feedbacks
EqCO2_N2O_Emissions_tonCO2_per_yr =                 N2O_Emissions_PiloArea_totalAgriculture_tonN2O_per_yr * 265 # without feedbacks


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- OVERALL GHG FLUX (in CO2 EQUIVALENT)
# -------------------------------------------------------------------------------------------------------------

EqCO2_TotalGHG_Sequestration_tonCO2_per_yr = EqCO2_NetCarbonSequestration_tonCO2_per_yr - EqCO2_CH4_Emissions_wetlands_tonCO2_per_yr - EqCO2_CO2_Emissions_tonCO2_per_yr - EqCO2_CH4_Emissions_totalGrazers_tonCO2_per_yr - EqCO2_N2O_Emissions_tonCO2_per_yr

print("Annual Total Net GHG flux (negative values stand for GHG emissions in the atmosphere): " + str(EqCO2_TotalGHG_Sequestration_tonCO2_per_yr)+ " tons CO2eq/year")


# write txt file with result 
output_txt_file_path = tool_path + "OutputData_ES/B_climate_GHG/EqCO2_TotalGHG_Sequestration_tonCO2_per_yr_"+ scenarioID +".txt"
file_to_write = open(output_txt_file_path, 'w')
file_to_write.write(str("Annual Total Net GHG flux (negative values stand for GHG emissions in the atmosphere): " + str(EqCO2_TotalGHG_Sequestration_tonCO2_per_yr)+ " tons CO2eq/year"+'\n\n'+

"EqCO2_NetCarbonSequestration_tonCO2_per_yr: " + str(EqCO2_NetCarbonSequestration_tonCO2_per_yr)+ " tons CO2eq/year"+'\n'+
"EqCO2_CH4_Emissions_wetlands_tonCO2_per_yr: " + str(EqCO2_CH4_Emissions_wetlands_tonCO2_per_yr)+ " tons CO2eq/year"+'\n'+
"EqCO2_CO2_Emissions_tonCO2_per_yr: " + str(EqCO2_CO2_Emissions_tonCO2_per_yr)+ " tons CO2eq/year"+'\n'+
"EqCO2_CH4_Emissions_totalGrazers_tonCO2_per_yr: " + str(EqCO2_CH4_Emissions_totalGrazers_tonCO2_per_yr)+ " tons CO2eq/year"+'\n'+
"EqCO2_N2O_Emissions_tonCO2_per_yr: " + str(EqCO2_N2O_Emissions_tonCO2_per_yr)+ " tons CO2eq/year"+'\n\n'+

"CO2_Emissions_PiloArea_tonCO2_per_yr: " + str(CO2_Emissions_PiloArea_tonCO2_per_yr)+ " tons CO2eq/year"+'\n'+
"CH4_Emissions_totalGrazers_PiloArea_tonCH4_per_yr: " + str(CH4_Emissions_totalGrazers_PiloArea_tonCH4_per_yr)+ " tons CH4eq/year"+'\n'+
"N2O_Emissions_PiloArea_totalAgriculture_tonN2O_per_yr: " + str(N2O_Emissions_PiloArea_totalAgriculture_tonN2O_per_yr)+ " tons NO2eq/year"+'\n'


))
# close 
file_to_write.close()




# -----------------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - B: GLOBAL CLIMATE REGULATION - GHG SEQUESTRATION -- OVERALL GHG FLUX (in CO2 EQUIVALENT) ON MAP!!!
# -----------------------------------------------------------------------------------------------------------------------

# 1) C sequestration from trees 
# EqCO2
netCsequestration_layer_path = tool_path + "OutputData_ES/A_climate_carbon_stocks/A_climate_output01b_carbon_seq_"+scenarioID+".shp"
carbonSeq_CO2eq_per_ha_raster_path = tool_path +  "OutputData_ES/A_climate_carbon_stocks/A_climate_carbon_seq_CO2eq_per_ha_"+scenarioID+".tif"
carbonSeq_CO2eq_per_ha_raster_name = "A_climate_carbon_seq_CO2eq_per_ha"
# get extent
extent_pilot = ExtCBA2_EcosystemTypes_layer.extent() 
extent_string  = str(extent_pilot.xMinimum())+","+str(extent_pilot.xMaximum())+","+str(extent_pilot.yMinimum())+","+str(extent_pilot.yMaximum())+ "[EPSG:3035]" 
# get pixel number
width_raster = round((extent_pilot.xMaximum()-extent_pilot.xMinimum())/100)
height_raster = round((extent_pilot.yMaximum()-extent_pilot.yMinimum())/100)
# or no data: 1.79769e+308
params_new  = { 'BURN' : 0, 
                'DATA_TYPE' : 5, 
                'EXTENT' : extent_string, 
                'FIELD' : 'CO2eqHA', 
                'HEIGHT' : height_raster, 
                'INIT' : None, 
                'INPUT' : netCsequestration_layer_path, 
                'INVERT' : False, 
                'NODATA' : None, 
                'OPTIONS' : '', 
                'OUTPUT' : carbonSeq_CO2eq_per_ha_raster_path, 
                'UNITS' : 0, 
                'WIDTH' : width_raster
                }
feedback = qgis.core.QgsProcessingFeedback()
alg_name = 'gdal:rasterize'
#print(processing.algorithmHelp(alg_name))
result = processing.run(alg_name, params_new, feedback=feedback)

carbonSeq_CO2eq_per_ha_raster = iface.addRasterLayer(carbonSeq_CO2eq_per_ha_raster_path, carbonSeq_CO2eq_per_ha_raster_name)



#2) emissions from soil (sum over area)
if ExtCBA_6_wetlandCategory is not None:
    myField = QgsField( 'CH4CO2ha', QVariant.Double )
    CH4_wetlands_layer.dataProvider().addAttributes([myField])
    CH4_wetlands_layer.updateFields()
    idx_HA = CH4_wetlands_layer.fields().indexFromName('Area_ha')
    idx_CH4 = CH4_wetlands_layer.fields().indexFromName('CH4_Emissions_wetlands_tonCH4_per_yr')
    idx_ceqha = CH4_wetlands_layer.fields().indexFromName('CH4CO2ha')
    for f in CH4_wetlands_layer.getFeatures():
        CH4_ha = f[idx_CH4]/f[idx_HA]
        f[idx_ceqha] = CH4_ha*28
        CH4_wetlands_layer.updateFeature( f )
    # commit changes
    CH4_wetlands_layer.commitChanges()



#if ExtCBA_6_wetlandCategory is not None:
#    # save the output as shapefile
#    # CREATE RASTER
#    # missing



# 3) emissions from all habitats
# - GWP100 of methane is 28
# - GWP100 of nitrous oxide is 265

myField = QgsField( 'CO2eqHA', QVariant.Double )
GHG_layer.dataProvider().addAttributes([myField])
GHG_layer.updateFields()
idx_HA = GHG_layer.fields().indexFromName('Area_ha')
idx_CO2 = GHG_layer.fields().indexFromName('CO2_Emissions_tonCO2_per_yr')
idx_CH4 = GHG_layer.fields().indexFromName('CH4_Emissions_totalGrazers_tonCH4_per_yr')
idx_N2O = GHG_layer.fields().indexFromName('N2O_Emissions_totalAgriculture_tonN2O_per_yr')
idx_Ceqha = GHG_layer.fields().indexFromName('CO2eqHA')

#start editing
GHG_layer.startEditing()
for f in GHG_layer.getFeatures():
    totalCO2eq_per_ha = numpy.nansum([  float(f[idx_N2O]) * 265.0, float(f[idx_CH4]) * 28.0, float(f[idx_CO2])  ])/float(f[idx_HA])
    f[idx_Ceqha]=float(totalCO2eq_per_ha)
    GHG_layer.updateFeature( f )
    print('totalCO2eq_per_ha: ' + str(f[idx_Ceqha]))
    # update the feature
# commit changes
GHG_layer.commitChanges()


# SAVE THE FINAL SHAPEFILE OF TOTAL CARBON STOCKS
QgsVectorFileWriter.writeAsVectorFormat(GHG_layer, tool_path + "OutputData_ES/B_climate_GHG/B_climate_output02_GHG_"+scenarioID+".shp","UTF-8", GHG_layer.crs(), "ESRI Shapefile")


# CREATE RASTER
# EqCO2
GHG_layer_path = tool_path + "OutputData_ES/B_climate_GHG/B_climate_output02_GHG_"+scenarioID+".shp"
GHG_CO2eq_per_ha_raster_path = tool_path + "OutputData_ES/B_climate_GHG/B_climate_GHGem_CO2eq_per_ha_"+scenarioID+".tif"
GHG_CO2eq_per_ha_raster_name = "B_climate_GHGem_CO2eq_per_ha"
# get extent
extent_pilot = ExtCBA2_EcosystemTypes_layer.extent() 
extent_string  = str(extent_pilot.xMinimum())+","+str(extent_pilot.xMaximum())+","+str(extent_pilot.yMinimum())+","+str(extent_pilot.yMaximum())+ "[EPSG:3035]" 
# get pixel number
width_raster = round((extent_pilot.xMaximum()-extent_pilot.xMinimum())/100)
height_raster = round((extent_pilot.yMaximum()-extent_pilot.yMinimum())/100)

params_new  = { 'BURN' : 0, 
                'DATA_TYPE' : 5, 
                'EXTENT' : extent_string, 
                'FIELD' : 'CO2eqHA', 
                'HEIGHT' : height_raster, 
                'INIT' : None, 
                'INPUT' : GHG_layer_path, 
                'INVERT' : False, 
                'NODATA' : None, 
                'OPTIONS' : '', 
                'OUTPUT' : GHG_CO2eq_per_ha_raster_path, 
                'UNITS' : 0, 
                'WIDTH' : width_raster 
                }
feedback = qgis.core.QgsProcessingFeedback()
alg_name = 'gdal:rasterize'
#print(processing.algorithmHelp(alg_name))
result = processing.run(alg_name, params_new, feedback=feedback)

GHG_CO2eq_per_ha_raster = iface.addRasterLayer(GHG_CO2eq_per_ha_raster_path, GHG_CO2eq_per_ha_raster_name)




# SUBTRACT 2 RASTERS
# carbonSeq_CO2eq_per_ha_raster + GHG_CO2eq_per_ha_raster

result_CO2eq_per_ha_raster_path = tool_path+ "OutputData_ES/B_climate_GHG/B_climate_output03_GHGflux_CO2eq_"+scenarioID+".tif"
   
param_sum2  =  { 'BAND_A' : 1, 
'BAND_B' : 1, 
'BAND_C' : -1, 
'BAND_D' : -1, 
'BAND_E' : -1, 
'BAND_F' : -1, 
'FORMULA' : 'A - B', 
'INPUT_A' : carbonSeq_CO2eq_per_ha_raster_path, 
'INPUT_B' : GHG_CO2eq_per_ha_raster_path, 
'INPUT_C' : None, 'INPUT_D' : None, 'INPUT_E' : None, 'INPUT_F' : None, 
'NO_DATA' : None, 
'OPTIONS' : '', 
'OUTPUT' : result_CO2eq_per_ha_raster_path, 
'RTYPE' : 5 }

feedback = qgis.core.QgsProcessingFeedback()
alg_name = 'gdal:rastercalculator'
#print(processing.algorithmHelp(alg_name))
result = processing.run(alg_name, param_sum2, feedback=feedback)

B_climate_output03_GHGflux_CO2eq_raster = iface.addRasterLayer(result_CO2eq_per_ha_raster_path, 'B_climate_output03_GHGflux_CO2eq_raster')


