# Functions_A_Climate_CarbonStorage_readTables
# Functions to retrieve infos from the different available tables
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

# AGB ----------------------------------------------------------------------------------------------------------------
# GET DATA FROM Table IPCC 4.7 
def readTable_IPCC_4_7(IPCC_table_4_7,continent,climate_reg,forest_ecoZone, forest_age_bool):
    # get indexes colums from the table 4.7: for tree-dominated ----------------------------------------------------------------------------------
    features_table = IPCC_table_4_7.getFeatures()
    idx_continent = IPCC_table_4_7.fields().indexFromName('Continent')
    idx_climate = IPCC_table_4_7.fields().indexFromName('Domain')
    idx_eco = IPCC_table_4_7.fields().indexFromName('EcologicalZone')
    idx_older = IPCC_table_4_7.fields().indexFromName('Older_20yrs')
    idx_agb = IPCC_table_4_7.fields().indexFromName('AboveGroundBiomass_ton_dry_mass_per_ha')

    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_continent]== continent and attributes_table[idx_climate]== climate_reg and attributes_table[idx_eco]== forest_ecoZone and int(attributes_table[idx_older]) == forest_age_bool :
            feat_value = feat
            print("AGB unit for specific area with trees: " + feat_value[idx_agb] + " tonnes dm/ha")
            agb_ton_dm_per_ha_forest = float(feat_value[idx_agb])
            
    return agb_ton_dm_per_ha_forest

# GET DATA FROM TABLE Anderson-Teixeira and deLucia, 2011 -----------------------------------------------------------------------------------------------------
#Habitat types affected: 
#('Grass', 2, 'yellow'), agb_ton_dm_per_ha_grass
#('Wetland', 5, 'brown'), agb_ton_dm_per_ha_wetland

def readTable_Anderson_Teixera_2011(table_Anderson_Teixera_2011,continent,climate_reg,grassland_ecoZone,wetland_ecoZone,naturalness_type):
    # get indexes columns from the table_Anderson_Teixera_2011
    features_table = table_Anderson_Teixera_2011.getFeatures()
    idx_continent = table_Anderson_Teixera_2011.fields().indexFromName('Continent')
    idx_climate = table_Anderson_Teixera_2011.fields().indexFromName('Domain')
    idx_eco = table_Anderson_Teixera_2011.fields().indexFromName('EcologicalZone')
    idx_naturalness = table_Anderson_Teixera_2011.fields().indexFromName('Naturalness_type')
    idx_agb = table_Anderson_Teixera_2011.fields().indexFromName('AboveGroundBiomass_ton_dry_mass_per_ha')
    # get specific value from the table for AGB grass
    for feat in features_table:
        attributes_table = feat.attributes()
        # look for value of grassland
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]== "worldwide") and (attributes_table[idx_climate]== climate_reg or attributes_table[idx_climate]=="All")  and attributes_table[idx_eco]== grassland_ecoZone :
            feat_value = feat
            print("AGB unit for specific area with grassland: " + feat_value[idx_agb] + " tonnes dm/ha")
            agb_ton_dm_per_ha_grass = float(feat_value[idx_agb])
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]== "worldwide") and (attributes_table[idx_climate]== climate_reg or attributes_table[idx_climate]=="All")  and attributes_table[idx_eco]== wetland_ecoZone :
            feat_value = feat
            print("AGB unit for specific area with wetland: " + feat_value[idx_agb] + " tonnes dm/ha")
            agb_ton_dm_per_ha_wetland = float(feat_value[idx_agb])
    
    # get extra index for bgb
    idx_bgb = table_Anderson_Teixera_2011.fields().indexFromName('BelowGroundBiomass_ton_dry_mass_per_ha')
    # get specific value from the table for BGB grass
    features_table = table_Anderson_Teixera_2011.getFeatures()
    for feat in features_table:
        attributes_table = feat.attributes()
        # look for value of wetland
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]== "worldwide") and (attributes_table[idx_climate]== climate_reg or attributes_table[idx_climate]=="All")  and attributes_table[idx_eco]== wetland_ecoZone :
            feat_value = feat
            print("BGB unit for specific area with wetland: " + feat_value[idx_bgb] + " tonnes dm/ha")
            bgb_ton_dm_per_ha_wetland = float(feat_value[idx_bgb])
    
    # get extra index for litter and dead wood
    idx_litter = table_Anderson_Teixera_2011.fields().indexFromName('Litter_ton_dry_mass_per_ha')
    idx_dead = table_Anderson_Teixera_2011.fields().indexFromName('DeadWood_ton_dry_mass_per_ha')
    
    # get specific value for litter and dead wood
    features_table = table_Anderson_Teixera_2011.getFeatures()
    for feat in features_table:
        attributes_table = feat.attributes()
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]== "worldwide") and (attributes_table[idx_naturalness]== naturalness_type or attributes_table[idx_naturalness]== "aggrading") and (attributes_table[idx_climate]== climate_reg )  and attributes_table[idx_eco]== "Temperate forest" :
            feat_value = feat
            print("DEAD unit for specific area with trees: " + feat_value[idx_dead] + " tonnes dm/ha")
            dead_ton_dm_per_ha_forest = float(feat_value[idx_dead])
        # look for value of grassland
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]== "worldwide") and (attributes_table[idx_climate]== climate_reg or attributes_table[idx_climate]=="All")  and attributes_table[idx_eco]== grassland_ecoZone :
            feat_value = feat
            print("LITTER unit for specific area with grassland: " + feat_value[idx_litter] + " tonnes dm/ha")
            print("DEAD unit for specific area with grassland: " + feat_value[idx_dead] + " tonnes dm/ha")
            litter_ton_dm_per_ha_grass = float(feat_value[idx_litter])
            dead_ton_dm_per_ha_grass = float(feat_value[idx_dead])
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]== "worldwide") and (attributes_table[idx_climate]== climate_reg or attributes_table[idx_climate]=="All")  and attributes_table[idx_eco]== wetland_ecoZone :
            feat_value = feat
            print("LITTER unit for specific area with wetland: " + feat_value[idx_litter] + " tonnes dm/ha")
            print("DEAD unit for specific area with wetland: " + feat_value[idx_dead] + " tonnes dm/ha")
            litter_ton_dm_per_ha_wetland = float(feat_value[idx_litter])
            dead_ton_dm_per_ha_wetland = float(feat_value[idx_dead])
    
    # return
    return agb_ton_dm_per_ha_grass, agb_ton_dm_per_ha_wetland, bgb_ton_dm_per_ha_wetland, litter_ton_dm_per_ha_grass, litter_ton_dm_per_ha_wetland, dead_ton_dm_per_ha_forest, dead_ton_dm_per_ha_grass, dead_ton_dm_per_ha_wetland
    
# BGB ----------------------------------------------------------------------------------------------------------------
# GET DATA FROM Table IPCC 4.4 
def readTable_IPCC_4_4(IPCC_table_4_4,agb_ton_dm_per_ha_forest,continent,climate_reg,forest_ecoZone, tree_species):
    # get indexes colums from the table 4.4 ----------------------------------------------------------------------------------
    features_table = IPCC_table_4_4.getFeatures()
    idx_continent = IPCC_table_4_4.fields().indexFromName('Continent')
    idx_climate = IPCC_table_4_4.fields().indexFromName('Domain')
    idx_eco = IPCC_table_4_4.fields().indexFromName('EcologicalZone')
    idx_tree = IPCC_table_4_4.fields().indexFromName('Tree_species')
    idx_lowAGB = IPCC_table_4_4.fields().indexFromName('AboveGroundBiomass_lower_threshold_ton_per_ha')
    idx_uppAGB = IPCC_table_4_4.fields().indexFromName("AboveGroundBiomass_upper_threshold_ton_per_ha")
    idx_ratio = IPCC_table_4_4.fields().indexFromName('Ratio_BGB_AGB')

    # get specific value from the table: tree-dominated (perennial crops not included yet!!)
    for feat in features_table:
        attributes_table = feat.attributes()
        # tree-dominated
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]=="worldwide") and attributes_table[idx_climate]== climate_reg and attributes_table[idx_eco]== forest_ecoZone and attributes_table[idx_tree] == tree_species :
            lowAGB = float(feat[idx_lowAGB])
            uppAGB = float(feat[idx_uppAGB])
            if agb_ton_dm_per_ha_forest >= lowAGB and agb_ton_dm_per_ha_forest < uppAGB : 
                print("BGB ratio for specific area with trees: " + feat[idx_ratio])
                bgb_ton_dm_per_ha_forest = agb_ton_dm_per_ha_forest * float(feat[idx_ratio])
    return bgb_ton_dm_per_ha_forest

# GET DATA FROM Table IPCC 6.1
def readTable_IPCC_6_1(IPCC_table_6_1,agb_ton_dm_per_ha_grass,continent,climate_reg,grass_vegetation_type):
    # get indexes colums from the table 6.1 ----------------------------------------------------------------------------------
    features_table = IPCC_table_6_1.getFeatures()
    idx_continent = IPCC_table_6_1.fields().indexFromName('Continent')
    idx_climate = IPCC_table_6_1.fields().indexFromName('Domain')
    idx_veg = IPCC_table_6_1.fields().indexFromName('Vegetation_type')
    idx_ratio = IPCC_table_6_1.fields().indexFromName('Ratio_BGB_AGB')

    # get specific value from the table: grass-dominated
    for feat in features_table:
        attributes_table = feat.attributes()
        # grass-dominated
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]=="worldwide") and attributes_table[idx_climate]== climate_reg and attributes_table[idx_veg]== grass_vegetation_type  :
            print("BGB ratio for specific area with grassland: " + feat[idx_ratio])
            bgb_ton_dm_per_ha_grass = agb_ton_dm_per_ha_grass * float(feat[idx_ratio])
    
    # return
    return bgb_ton_dm_per_ha_grass


    
# LITTER ----------------------------------------------------------------------------------------------------------------
# GET DATA FROM Table IPCC 2.2 
def readTable_IPCC_2_2(IPCC_table_2_2,continent,climate_reg,climate_reg2,tree_species2):
    features_table = IPCC_table_2_2.getFeatures()
    idx_continent = IPCC_table_2_2.fields().indexFromName('Continent')
    idx_climate = IPCC_table_2_2.fields().indexFromName('Domain')
    idx_eco = IPCC_table_2_2.fields().indexFromName('EcologicalZone')
    idx_tree = IPCC_table_2_2.fields().indexFromName('Tree_species')
    idx_litter = IPCC_table_2_2.fields().indexFromName('LitterCarbonStocks_ton_C_per_ha')
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if (attributes_table[idx_continent]== continent or attributes_table[idx_continent]== "worldwide") and attributes_table[idx_climate]== climate_reg  and attributes_table[idx_tree] == tree_species2 and attributes_table[idx_eco]== climate_reg2 :
            feat_value = feat
            print("LITTER unit for specific area with trees: " + feat_value[idx_litter] + " tonnes dm/ha")
            litter_ton_dm_per_ha_forest = float(feat_value[idx_litter])
    # return
    return litter_ton_dm_per_ha_forest
    

# SOIL ORGANIC CARBON ----------------------------------------------------------------------------------------------------------------
# GET SOC DATA FROM Table IPCC 2.3
def readTable_IPCC_2_3(IPCC_table_2_3,climate_reg,climate_reg2,soil_type):
    features_table = IPCC_table_2_3.getFeatures()
    idx_climate = IPCC_table_2_3.fields().indexFromName('Domain')
    idx_climate2 = IPCC_table_2_3.fields().indexFromName('ClimateRegion')
    idx_soil = IPCC_table_2_3.fields().indexFromName('Soil_type')
    idx_soc = IPCC_table_2_3.fields().indexFromName('SoilOrganicCarbon_30cm_ton_C_per_ha')
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if (attributes_table[idx_climate2]== climate_reg2  and attributes_table[idx_climate]== climate_reg  and attributes_table[idx_soil] == soil_type ) :
            feat_value = feat
            print("SOC unit: " + feat_value[idx_soc] + " tonnes C/ha")
            soc_per_ha = float(feat_value[idx_soc])
    # return
    return soc_per_ha

# GET SOC DATA FROM Table IPCC 5.2 (2014)
def readTable_IPCC_5_2_2014(IPCC_table_5_2_2014,climate_reg,climate_reg2,soil_type):
    features_table = IPCC_table_5_2_2014.getFeatures()
    idx_climate = IPCC_table_5_2_2014.fields().indexFromName('Domain')
    idx_climate2 = IPCC_table_5_2_2014.fields().indexFromName('ClimateRegion')
    idx_soil = IPCC_table_5_2_2014.fields().indexFromName('Soil_type')
    idx_soc = IPCC_table_5_2_2014.fields().indexFromName('SoilOrganicCarbon_30cm_ton_C_per_ha')
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if (attributes_table[idx_climate2]== climate_reg2  and attributes_table[idx_climate]== climate_reg  and attributes_table[idx_soil] == soil_type ) :
            feat_value = feat
            print("SOC unit for wetlands: " + feat_value[idx_soc] + " tonnes C/ha")
            soc_per_ha = float(feat_value[idx_soc])
    # return
    return soc_per_ha

# GET FACTORS DATA FROM Table IPCC 5.3 (2014)
def readTable_IPCC_5_3_2014(IPCC_table_5_3_2014,climate_reg,level_type):
    features_table = IPCC_table_5_3_2014.getFeatures()
    idx_climate = IPCC_table_5_3_2014.fields().indexFromName('Domain')
    idx_level = IPCC_table_5_3_2014.fields().indexFromName('Level')
    idx_type = IPCC_table_5_3_2014.fields().indexFromName('Factor_type')
    idx_fact = IPCC_table_5_3_2014.fields().indexFromName('Factor_IPCC')
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if (( attributes_table[idx_climate]== climate_reg)  and attributes_table[idx_level] == level_type) :
            feat_value = feat
            print("Factor for " + feat_value[idx_level] + ": " + feat_value[idx_fact] )
            factor_SOC = float(feat_value[idx_fact])
    # return
    return factor_SOC

# GET FACTORS DATA FROM Table IPCC 5.5
def readTable_IPCC_5_5(IPCC_table_5_5,climate_reg,moisture_regime,level_type,factor_type):
    features_table = IPCC_table_5_5.getFeatures()
    idx_climate = IPCC_table_5_5.fields().indexFromName('Domain')
    idx_moist = IPCC_table_5_5.fields().indexFromName('Moisture_regime')
    idx_level = IPCC_table_5_5.fields().indexFromName('Level')
    idx_type = IPCC_table_5_5.fields().indexFromName('Factor_type')
    idx_fact = IPCC_table_5_5.fields().indexFromName('Factor_IPCC')
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if ((attributes_table[idx_climate]== climate_reg) and attributes_table[idx_moist] == moisture_regime and attributes_table[idx_type] == factor_type and attributes_table[idx_level] == level_type) :
            feat_value = feat
            print("Factor for " + factor_type + ": " + feat_value[idx_fact] )
            factor_SOC = float(feat_value[idx_fact])
        elif ((attributes_table[idx_climate]== "All"  ) and attributes_table[idx_moist] == moisture_regime and attributes_table[idx_type] == factor_type and attributes_table[idx_level] == level_type) :
            feat_value = feat
            print("Factor for " + factor_type + ": " + feat_value[idx_fact] )
            factor_SOC = float(feat_value[idx_fact])
    # return
    return factor_SOC


# GET FACTORS DATA FROM Table IPCC 6.2
def readTable_IPCC_6_2(IPCC_table_6_2,climate_reg,factor_type):
    features_table = IPCC_table_6_2.getFeatures()
    idx_climate = IPCC_table_6_2.fields().indexFromName('Domain')
    idx_deg = IPCC_table_6_2.fields().indexFromName('Degraded')
    idx_man = IPCC_table_6_2.fields().indexFromName('Managed')
    idx_type = IPCC_table_6_2.fields().indexFromName('Factor_type')
    idx_fact = IPCC_table_6_2.fields().indexFromName('Factor_IPCC')
    # get specific value from the table
    for feat in features_table:
        attributes_table = feat.attributes()
        if ((attributes_table[idx_climate]== climate_reg ) and factor_type == "management"  and attributes_table[idx_type] == factor_type and float(attributes_table[idx_deg]) < 0.5) :
            feat_value = feat
            print("Factor for " + factor_type + ": " + feat_value[idx_fact] )
            factor_SOC = float(feat_value[idx_fact])
        elif ((attributes_table[idx_climate]== "All" ) and factor_type != "management"  and attributes_table[idx_type] == factor_type and float(attributes_table[idx_deg]) < 0.5 and float(attributes_table[idx_man]) < 1) :
            feat_value = feat
            print("Factor for " + factor_type + ": " + feat_value[idx_fact] )
            factor_SOC = float(feat_value[idx_fact])
    # return
    print("Assuming non-degraded grassland")
    return factor_SOC



# REMOVALS ----------------------------------------------------------------------------------------------------------------
# GET DATA (carbon fraction) FROM Table IPCC 4.3
def readTable_IPCC_4_3(IPCC_table_4_3,climate_reg,tree_type):
    features_table = IPCC_table_4_3.getFeatures()
    idx_climate = IPCC_table_4_3.fields().indexFromName('Domain')
    idx_tree = IPCC_table_4_3.fields().indexFromName('Tree_type')
    idx_CF = IPCC_table_4_3.fields().indexFromName('CarbonFraction_tonC_per_ton_d_m')
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_climate]== climate_reg and attributes_table[idx_tree]== tree_type :
            CarbonFraction_tonC_per_ton_d_m = float(feat[idx_CF])
        else:
            CarbonFraction_tonC_per_ton_d_m = 0.47 # stardard for all climates and tree types
    #return
    return CarbonFraction_tonC_per_ton_d_m


# get data from FAO table: FAO_ForestResourcesAssessment_2015
def readTable_FAO_ForestResourcesAssessment(table_FAO_FRA2015, country):
    # get national forest area and growing stock level from FAO statistics
    features_table = table_FAO_FRA2015.getFeatures()
    idx_country = table_FAO_FRA2015.fields().indexFromName('Country')
    idx_year = table_FAO_FRA2015.fields().indexFromName('Year')
    idx_area = table_FAO_FRA2015.fields().indexFromName('Area_Forest_ha')
    idx_GS = table_FAO_FRA2015.fields().indexFromName('TotalGrowingStock_m3_yr')
    year_tmp = 0
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_country]== country :
            if int(attributes_table[idx_year])>year_tmp:
                year_tmp = int(attributes_table[idx_year])
                Forest_Area_country_ha = float(attributes_table[idx_area])
                GrowingStock_country_m3_yr = float(attributes_table[idx_GS])
    print(year_tmp)
    FAOstats_year = year_tmp
    # return
    return Forest_Area_country_ha, GrowingStock_country_m3_yr, FAOstats_year


# GET DATA FROM Table IPCC 4.5 
def readTable_IPCC_4_5(IPCC_table_4_5,climate_reg,tree_type2,GrowingStockLevel_country_m3_per_ha,BCER_type):
    features_table = IPCC_table_4_5.getFeatures()
    idx_climate = IPCC_table_4_5.fields().indexFromName('Domain')
    idx_tree = IPCC_table_4_5.fields().indexFromName('Tree_type')
    idx_BCEF = IPCC_table_4_5.fields().indexFromName('BCEF_ton_per_m3_wood')
    idx_GS_less20 = IPCC_table_4_5.fields().indexFromName('GrowingStockLevel_m3_per_ha_less_20')
    idx_GS_21_to_40 = IPCC_table_4_5.fields().indexFromName('GrowingStockLevel_m3_per_ha_21_to_40')
    idx_GS_41_to_100 = IPCC_table_4_5.fields().indexFromName('GrowingStockLevel_m3_per_ha_41_to_100')
    idx_GS_101_to_200 = IPCC_table_4_5.fields().indexFromName('GrowingStockLevel_m3_per_ha_101_to_200')
    idx_GS_more200 = IPCC_table_4_5.fields().indexFromName('GrowingStockLevel_m3_per_ha_more_200')
    # get BCEF_R from table 4.5
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_climate]== climate_reg and attributes_table[idx_tree]== tree_type2 and attributes_table[idx_BCEF] == BCER_type :
            if GrowingStockLevel_country_m3_per_ha <= 20:
                BCEF_R = float(attributes_table[idx_GS_less20])
            elif GrowingStockLevel_country_m3_per_ha > 20 and GrowingStockLevel_country_m3_per_ha <= 40:
                BCEF_R = float(attributes_table[idx_GS_21_to_40])
            elif GrowingStockLevel_country_m3_per_ha > 40 and GrowingStockLevel_country_m3_per_ha <= 100:
                BCEF_R = float(attributes_table[idx_GS_41_to_100])
            elif GrowingStockLevel_country_m3_per_ha > 100 and GrowingStockLevel_country_m3_per_ha <= 200:
                BCEF_R = float(attributes_table[idx_GS_101_to_200])
            elif GrowingStockLevel_country_m3_per_ha > 200 :
                BCEF_R = float(attributes_table[idx_GS_more200])
    #return
    return BCEF_R


# get wood removal values
def readTable_FAOSTAT_wood(table_FAOSTAT_wood,country,FAOstats_year):
    features_table = table_FAOSTAT_wood.getFeatures()
    idx_country = table_FAOSTAT_wood.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_wood.fields().indexFromName('Year')
    idx_fuelw = table_FAOSTAT_wood.fields().indexFromName('Fuelwood_removal_m3_yr')
    idx_roundw = table_FAOSTAT_wood.fields().indexFromName('Roundwood_removal_m3_yr')
    idx_charc = table_FAOSTAT_wood.fields().indexFromName('Charcoal_removal_tonnes_yr')
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_country]== country and int(attributes_table[idx_year])== FAOstats_year  :
            AnnualRoundwoodRemoval_country_m3_per_year = float(attributes_table[idx_roundw])
            AnnualFuelwoodRemoval_country_m3_per_year = float(attributes_table[idx_fuelw])
            AnnualCharocoalRemoval_country_m3_per_year = float(attributes_table[idx_charc])
    #return
    return AnnualRoundwoodRemoval_country_m3_per_year, AnnualFuelwoodRemoval_country_m3_per_year, AnnualCharocoalRemoval_country_m3_per_year

# get area of land use type
def readTable_FAOSTAT_landuse(table_FAOSTAT_landuse,country,FAOstats_year,landuseType):
    features_table = table_FAOSTAT_landuse.getFeatures()
    idx_country = table_FAOSTAT_landuse.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_landuse.fields().indexFromName('Year')
    idx_ha = table_FAOSTAT_landuse.fields().indexFromName('Area_ha')
    idx_item = table_FAOSTAT_landuse.fields().indexFromName('Item')
    for feat in features_table:
        attributes_table = feat.attributes()
        #print("Landuse_specific_area_ha in " + attributes_table[idx_country] + " for landuse " + attributes_table[idx_item] + ". " +attributes_table[idx_ha])
        if int(attributes_table[idx_year])== FAOstats_year  and attributes_table[idx_item]== landuseType and attributes_table[idx_country]== country :
            Landuse_specific_area_ha = float(attributes_table[idx_ha])
    try:
        Landuse_specific_area_ha
    except NameError:
        Landuse_specific_area_ha = float('nan')
    #return
    return Landuse_specific_area_ha


# get the mean annual increment of trees
def readTable_FAO_MAI(table_FAOSTAT_MAI,Genera_tree, Species_tree):
    features_table = table_FAOSTAT_MAI.getFeatures()
    listMAI = []
    idx_gen = table_FAOSTAT_MAI.fields().indexFromName('Genera')
    idx_spe = table_FAOSTAT_MAI.fields().indexFromName('Species')
    idx_MAI = table_FAOSTAT_MAI.fields().indexFromName('MAI-AVG')
    for feat in features_table:
        attributes_table = feat.attributes()
        listMAI.append(float(attributes_table[idx_MAI]))
        if attributes_table[idx_gen]== Genera_tree  and attributes_table[idx_spe]== Species_tree :
            MAI_m3_per_ha_yr = float(attributes_table[idx_MAI])
    # if the Genera and the Species is not provided, provide the average value
    try:
        MAI_m3_per_ha_yr
    except NameError:
        MAI_m3_per_ha_yr = sum(listMAI)/len(listMAI)
        print("The MAI was calculated based on the average of all tree Genera and Species")
    # return
    return MAI_m3_per_ha_yr
    
    
