# Functions_B_Climate_GHGsequestration_readTables
# Functions to retrieve infos from the different available tables
# by Francesca Perosa
# 20.01.2020

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

# CO2 EMISSIONS ----------------------------------------------------------------------------------------------------------------
# GET DATA FROM Table IPCC 2.1 (2014) 
def readTable_IPCC_2_1_2014(IPCC_table_2_1_2014,LandUse):
    # get indexes colums from the table 2.1: ---------------------------------------------------------------------------------
    features_table = IPCC_table_2_1_2014.getFeatures()
    idx_LU = IPCC_table_2_1_2014.fields().indexFromName('LandUse')
    idx_EF = IPCC_table_2_1_2014.fields().indexFromName('Emission_factor_tonCO2_per_ha_yr')

    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_LU]== LandUse :
            feat_value = feat
            print("EF in areas with landuse " + feat_value[idx_LU] + ": " + feat_value[idx_EF] + " tonnes CO2/ha*yr")
            EF_tonCO2_per_ha_yr = float(feat_value[idx_EF])
            
    return EF_tonCO2_per_ha_yr


# CH4 EMISSIONS ----------------------------------------------------------------------------------------------------------------
# GET DATA FROM Table EUROSTAT animals  
def readTable_EUROSTAT_animals(EUROSTAT_table_animals_NUTS2,NUTS2_region,NUTS2_area_ha,statisticsYear):
    label = str("THS_HD_" + str(statisticsYear) )
    # get indexes colums from the table: ---------------------------------------------------------------------------------
    features_table = EUROSTAT_table_animals_NUTS2.getFeatures()
    idx_number = EUROSTAT_table_animals_NUTS2.fields().indexFromName(label)
    idx_NUTS2 = EUROSTAT_table_animals_NUTS2.fields().indexFromName("NUTS2")
    idx_animal = EUROSTAT_table_animals_NUTS2.fields().indexFromName("Animals")
    idx_animal_name = EUROSTAT_table_animals_NUTS2.fields().indexFromName("Animal_description")
    
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_NUTS2]== NUTS2_region :
            if attributes_table[idx_animal]=="A2000":
                feat_value = feat
                Heads_bovine_per_yr_ha = float(feat_value[idx_number])/NUTS2_area_ha
                print("Bovine count in NUTS2 region: " + feat_value[idx_number] + " heads/yr/ha")
            if attributes_table[idx_animal]=="A2300F":
                feat_value = feat
                Heads_dairyCows_per_yr_ha = float(feat_value[idx_number])/NUTS2_area_ha
                print("Dairy cows count in NUTS2 region: " + feat_value[idx_number] + " heads/yr/ha")
            if attributes_table[idx_animal]=="A3100":
                feat_value = feat
                Heads_pigs_per_yr_ha = float(feat_value[idx_number])/NUTS2_area_ha
                print("Pigs count in NUTS2 region: " + feat_value[idx_number] + " heads/yr/ha")
            if attributes_table[idx_animal]=="A4100":
                feat_value = feat
                Heads_sheep_per_yr_ha = float(feat_value[idx_number])/NUTS2_area_ha
                print("Sheep count in NUTS2 region: " + feat_value[idx_number] + " heads/yr/ha")
            if attributes_table[idx_animal]=="A4200":
                feat_value = feat
                Heads_goats_per_yr_ha = float(feat_value[idx_number])/NUTS2_area_ha
                print("Goats count in NUTS2 region: " + feat_value[idx_number] + " heads/yr/ha")
                
    try:
        Heads_bovine_per_yr_ha
    except NameError:
        Heads_bovine_per_yr_ha = float('nan')
    try:
        Heads_dairyCows_per_yr_ha
    except NameError:
        Heads_dairyCows_per_yr_ha = float('nan')
    try:
        Heads_pigs_per_yr_ha
    except NameError:
        Heads_pigs_per_yr_ha = float('nan')
    try:
        Heads_sheep_per_yr_ha
    except NameError:
        Heads_sheep_per_yr_ha = float('nan')
    try:
        Heads_goats_per_yr_ha
    except NameError:
        Heads_goats_per_yr_ha = float('nan')
    
    return Heads_bovine_per_yr_ha, Heads_dairyCows_per_yr_ha, Heads_pigs_per_yr_ha, Heads_sheep_per_yr_ha, Heads_goats_per_yr_ha 
    
    


# GET EMISSION FACTORS FROM Table IPCC 10.10 and 10.11   
def readTable_IPCC_Ch10_10_11(IPCC_table_10_10, IPCC_table_10_11,domesticAnimal,eastWest_europe):
    # get indexes colums from the table 10: ---------------------------------------------------------------------------------
    features_table10 = IPCC_table_10_10.getFeatures()
    idx_LS = IPCC_table_10_10.fields().indexFromName("Livestock")
    idx_EF10 = IPCC_table_10_10.fields().indexFromName("Emission_Factor_kgCH4_per_head_yr")
    # get indexes colums from the table 11: --------------------------------------------------------------------------------- 
    features_table11 = IPCC_table_10_11.getFeatures()
    idx_reg = IPCC_table_10_11.fields().indexFromName("Region")
    idx_cattle = IPCC_table_10_11.fields().indexFromName("CattleCathegory")
    idx_EF11 = IPCC_table_10_11.fields().indexFromName("Emission_Factor_kgCH4_per_head_yr")
    # get specific value from the table
    if domesticAnimal == "Dairy" or domesticAnimal == "Other cattle": 
        for feat in features_table11:
            attributes_table = feat.attributes()
            if attributes_table[idx_cattle]== domesticAnimal and attributes_table[idx_reg]== eastWest_europe :
                feat_value = feat
                EF_CH4_domesticAnimal = float(feat_value[idx_EF11])
    else: 
        for feat in features_table10:
            attributes_table = feat.attributes()
            if attributes_table[idx_LS]== domesticAnimal :
                feat_value = feat
                EF_CH4_domesticAnimal = float(feat_value[idx_EF10])
    return EF_CH4_domesticAnimal


# GET EMISSION FACTORS FROM Table TESSA M11 wild Grazers  
def readTable_TESSA_M11(table_TESSA_wildGrazers, wildGrazer):
    # get indexes colums from the table found in TESSA M11: ---------------------------------------------------------------------------------
    features_table = table_TESSA_wildGrazers.getFeatures()
    idx_WG = table_TESSA_wildGrazers.fields().indexFromName("Wild_grazer")  
    idx_EF = table_TESSA_wildGrazers.fields().indexFromName("Emission_Factor_kgCH4_per_head_yr")
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_WG]== wildGrazer :
            feat_value = feat
            EF_CH4_wildGrazer = float(feat_value[idx_EF])
    return EF_CH4_wildGrazer


# GET EMISSION FACTORS FROM Table TESSA M11  natural wetlands
def readTable_TESSA_M11_5_A(table_TESSA_naturalWetlands, wetland_type_TESSAtable):
    # get indexes colums from the table found in TESSA M11: ---------------------------------------------------------------------------------
    features_table = table_TESSA_naturalWetlands.getFeatures()
    idx_WT = table_TESSA_naturalWetlands.fields().indexFromName("Wetland_type")  
    idx_EF = table_TESSA_naturalWetlands.fields().indexFromName("Emission_Factor_tonCH4_per_ha_yr")
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_WT]== wetland_type_TESSAtable :
            feat_value = feat
            EF_CH4_wetland = float(feat_value[idx_EF])
    return EF_CH4_wetland


# GET DATA FROM Table IPCC 2.3 (2014) 
def readTable_IPCC_2_3_2014(IPCC_table_2_3_2014,LandUse):
    # get indexes colums from the table 2.3: ---------------------------------------------------------------------------------
    features_table = IPCC_table_2_3_2014.getFeatures()
    idx_LU = IPCC_table_2_3_2014.fields().indexFromName('LandUse')
    idx_EF = IPCC_table_2_3_2014.fields().indexFromName('Emission_factor_kgCH4_per_ha_yr')

    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_LU]== LandUse :
            feat_value = feat
            print("EF in areas with landuse " + feat_value[idx_LU] + ": " + feat_value[idx_EF] + " kg CH4/ha*yr")
            EF_tonCH4_per_ha_yr = float(feat_value[idx_EF])/1000
            
    return EF_tonCH4_per_ha_yr

# GET DATA FROM Table IPCC 2.4 (2014) 
def readTable_IPCC_2_4_2014(IPCC_table_2_4_2014,climate_reg,LandUse):
    # get indexes colums from the table 2.3: ---------------------------------------------------------------------------------
    features_table = IPCC_table_2_4_2014.getFeatures()
    idx_CL = IPCC_table_2_4_2014.fields().indexFromName('Domain')
    idx_LU = IPCC_table_2_4_2014.fields().indexFromName('LandUse')
    idx_EF = IPCC_table_2_4_2014.fields().indexFromName('Emission_factor_ditch_kgCH4_per_ha_yr')
    idx_FR = IPCC_table_2_4_2014.fields().indexFromName('Ratio_Ditch')
    # adapt land use
    if LandUse == "Grassland shallow-drained nutrient-rich" :
        LandUse = "Grassland shallow-drained"
    elif LandUse == "Grassland deep-drained nutrient-rich" :
        LandUse = "Grassland deep-drained"
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_LU]== LandUse and attributes_table[idx_CL]== climate_reg:
            feat_value = feat
            print("EF in ditches with landuse " + feat_value[idx_LU] + ": " + feat_value[idx_EF] + " kg CH4/ha*yr")
            EF_tonCH4_per_ha_yr = float(feat_value[idx_EF])/1000
            Frac_ditch = float(feat_value[idx_FR])
    #return
    return EF_tonCH4_per_ha_yr, Frac_ditch


# GET DATA FROM Table IPCC 3.3 (2014) 
def readTable_IPCC_3_3_2014(IPCC_table_3_3_2014,climate_reg,nutrientStatus):
    # get indexes colums from the table 3.3: ---------------------------------------------------------------------------------
    features_table = IPCC_table_3_3_2014.getFeatures()
    idx_D = IPCC_table_3_3_2014.fields().indexFromName('Domain')
    idx_NU = IPCC_table_3_3_2014.fields().indexFromName('NutrientStatus')
    idx_EF = IPCC_table_3_3_2014.fields().indexFromName('Emission_factor_kgCH4_per_ha_yr')

    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_NU]== nutrientStatus and attributes_table[idx_D]==climate_reg:
            feat_value = feat
            print("EF in areas with nutrient status " + feat_value[idx_NU] + ": " + feat_value[idx_EF] + " kg CH4/ha*yr")
            EF_tonCH4_per_ha_yr = float(feat_value[idx_EF])/1000
            
    return EF_tonCH4_per_ha_yr

# GET DATA FROM Table IPCC 3A.2
def readTable_IPCC_3A_2(IPCC_table_3A_2,climate_reg3):
    # get indexes colums from the table 3A.2: ---------------------------------------------------------------------------------
    features_table = IPCC_table_3A_2.getFeatures()
    idx_CL = IPCC_table_3A_2.fields().indexFromName('Climate')
    idx_EF = IPCC_table_3A_2.fields().indexFromName('Emission_factor_kgCH4_per_ha_day')
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_CL]== climate_reg3 :
            feat_value = feat
            print("EF in areas with climate " + feat_value[idx_CL] + ": " + feat_value[idx_EF] + " kg CH4/ha*day")
            EF_tonCH4_per_ha_day = float(feat_value[idx_EF])/1000            
    return EF_tonCH4_per_ha_day


# GET DATA FROM Table FAO
def readTable_FAO_agricultureEmissions(FAO_table_agricultureEmissions, year_stats, emissionsType, emissionsProcess, country):
    features_table = FAO_table_agricultureEmissions.getFeatures()
    idx_EM = FAO_table_agricultureEmissions.fields().indexFromName("Emissions_ton_per_year")
    idx_ET = FAO_table_agricultureEmissions.fields().indexFromName("EmissionsType")
    idx_EP = FAO_table_agricultureEmissions.fields().indexFromName("EmissionsProcess")
    idx_YR = FAO_table_agricultureEmissions.fields().indexFromName("Year")
    idx_CC = FAO_table_agricultureEmissions.fields().indexFromName("Area")
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_CC]== country and attributes_table[idx_YR]== year_stats and attributes_table[idx_ET]==emissionsType and attributes_table[idx_EP]==emissionsProcess:
            feat_value = feat
            #print(" " + feat_value[idx_ET] " from "+ feat_value[idx_EP] +": " + feat_value[idx_EM] + " ton/yr" + feat_value[idx_YR])
            EmissionsCountry_ton_per_yr = float(feat_value[idx_EM])
    return EmissionsCountry_ton_per_yr
    
    
    
    
