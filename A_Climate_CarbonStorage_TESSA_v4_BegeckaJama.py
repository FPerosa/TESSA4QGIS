# A: CLIMATE - CARBON STORAGE 
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

# -------------------------------------------------------------------------------------------------------------
# -- IMPORT PATH  --
# -------------------------------------------------------------------------------------------------------------

tool_path = QgsProject.instance().readPath("./")+"/DanubeFloodplain_ES_Assessment_Tool/"

# -------------------------------------------------------------------------------------------------------------
# -- IMPORT LIBRARY  --
# -------------------------------------------------------------------------------------------------------------

sys.path.insert(1, (tool_path +'Library_v3'))
from Import_A_Climate_CarbonStorage_tables import *
from Import_A_Climate_CarbonStorage_spatial import *
from Functions_A_Climate_CarbonStorage_readTables import *
from Functions_A_Climate_CarbonStorage_calculateResults import *

from qgis.analysis import QgsZonalStatistics

from osgeo import gdal



# -------------------------------------------------------------------------------------------------------------
# -- FUNCTIONS --
# -------------------------------------------------------------------------------------------------------------

# CREATE COPY OF SHAPEFILE
# Create new shapefile to save all results (copy from original file of habitat types) ---
# (from: https://gis.stackexchange.com/questions/205947/duplicating-layer-in-memory-using-pyqgis)
def createCopy_Shapefile(vlayer, nameNewLayer, id_code_name):
    feats_original = [feat for feat in vlayer.getFeatures()] # get features from riginal habitats shapefile
    new_layer = QgsVectorLayer("Polygon?crs=epsg:3035", nameNewLayer, "memory") # create empty new layer
    # get data from old shapefile
    new_layer_data = new_layer.dataProvider() 
    attr = vlayer.dataProvider().fields().toList()
    new_layer_data.addAttributes(attr)
    new_layer.updateFields()
    new_layer_data.addFeatures(feats_original)
    # create instance of shapefile
    QgsProject.instance().addMapLayer(new_layer)
    # get indexes of the attribute table in the new layer
    id_code = new_layer.fields().indexFromName(id_code_name)
    #return
    return new_layer




# -------------------------------------------------------------------------------------------------------------
# -- IMPORT DATA  --
# -------------------------------------------------------------------------------------------------------------

pilotArea_name = "BegeckaJama"
scenarioID = "RS2" # "RS2"# "CS"

# Import IPCC tables 
IPCC_table_2_2, IPCC_table_2_3, IPCC_table_4_3, IPCC_table_4_4, IPCC_table_4_5, IPCC_table_4_7, IPCC_table_5_2_2014, IPCC_table_5_3_2014, IPCC_table_5_5, IPCC_table_6_1, IPCC_table_6_2, table_FAO_FRA2015, table_Anderson_Teixera_2011, table_FAOSTAT_wood, table_FAOSTAT_landuse, table_FAOSTAT_MAI = ImportIPCC_tables_A_CarbonStorage(iface, tool_path)

#Import spatial data
AreaAnalysis_layer = Import_AnalysisArea_shp(iface, tool_path, pilotArea_name)
Danube_countries = Import_Danube_countries_shp(iface, tool_path)
SOC_ton_per_ha_raster = Import_SoilOrganicCarbon_ras(iface, tool_path)

# SHAPEFILE ExtCBA_2 
ExtCBA2_EcosystemTypes_layer = Import_HabitatType_ExtCBA2(iface,tool_path,pilotArea_name,scenarioID)

# Import wood ESS map and calculate area or wood harvesting
ESmapStake_wood_layer = Import_ESMapStakeholders_wood_shp(iface,tool_path,pilotArea_name,scenarioID)




# -------------------------------------------------------------------------------------------------------------
# -- AREA CHARACTERISTICS  --
# -------------------------------------------------------------------------------------------------------------
#MUST BE CHANGED -------------------------------------------------------------------------------------------------------
# AREA CHARACTERISTICS - beginning -------------------------------------------------------------------------------
# define area characteristics 
# for AGB ---
climate_reg = "Temperate"
climate_reg2 = "Warm moist"
continent = "Europe"
country = "Serbia"
# tree-dominated areas
forest_ecoZone = "Temperate continental forest" # or "Temperate scrub/woodland"
forest_type = "plantations" # "natural" # "natural" or 
tree_type = "broadleaf" # or "conifer"
tree_type2 = "hardwoods" # or "pines" or "other conifers" or "larch" or "firs" or "spruces"
forest_age = 19 # yrs
if (forest_age>20):
    forest_age_bool = 1
else:
    forest_age_bool = 0

# grass-dominated areas
grassland_ecoZone = "Temperate non-forest" #"Temperate grassland" #  or  or "Temperate pasture"
# wetland-dominated areas
wetland_ecoZone = "Freshwater Marsh and swamp" # or "Northern peatland"
#crop-dominated areas
crop_ecoZone = "Temperate cropland" # or "Wetland rice"
cultivation_type = "annual" # or perennial
if cultivation_type == "annual":
    agb_ton_dm_per_ha_crop_annual = 0.0 # ALWAYS!!
    bgb_ton_dm_per_ha_crop_annual = 0.0 # ALWAYS!!
    litter_ton_dm_per_ha_crop_annual = 0.0 # ALWAYS!!
    dead_ton_dm_per_ha_crop_annual = 0.0 # ALWAYS!!
elif cultivation_type == "perennial":
    # happens not in Europe, don't know yet 
    agb_ton_dm_per_ha_crop_perennial = None


# for BGB ---
tree_species = "other broadleaf" # or "conifers" or "Eucalyptus spp." or "Quercus spp."
grass_vegetation_type = "Semi-arid grassland" # or "Steppe/tundra/prairie grassland" 

# for LITTER and DEAD ---
tree_species2 = "Broadleaf deciduous" # or "Needleleaf evergreen"
naturalness_type =  "aggrading"  # "aggrading"  or  # "native" or "managed" 
# CS in Begecka: naturalness_type =  "managed"

# for SOIL ORGANIC CARBON
moisture_regime = "Moist" # choose between "Moist" or "Dry"
soil_type = "mineral" # choose between "organic" or "mineral"
soil_type_fromMap = "high activity clay" # "high activity clay" or  "low activity clay" or "sandy" or "spodic" or "volcanic" or "wetland"

level_landuse = "Long-term cultivated" # "Long-term cultivated" or "Paddy rice" or "Perennial Crop" or "Set aside"
level_management = "Tillage, high disturbance" # "Tillage, high disturbance" or "Tillage, low disturbance" or "No tillage"
level_input = "Medium input" # "Low input" or "Medium input" or "High input, no manure" or "High input, with manure" 
level_landuse_rewetted_crop = "Long-term cultivated" # "Long-term cultivated" or "Rewetting, years 1-20" or "Rewetting, years 21-40"


#  for C stock alteration
# HARVESTED AREAS --- 
# get area size (ha) of the country from the Danube_countries layer
features_layer = Danube_countries.getFeatures()
idx_country = Danube_countries.fields().indexFromName('NAME_ENGL')
idx_area = Danube_countries.fields().indexFromName('Area_ha')
for feat in features_layer:
    attributes_table = feat.attributes()
    if attributes_table[idx_country] == country:
        Area_country_ha = float(attributes_table[idx_area])




# Country's harvestable area
if 'Area_harvestable_country_ha' in locals():
    print('Area_harvestable_country_ha exists')
else:
    Area_harvestable_country_ha = None
    print('Area_harvestable_country_ha was assigned null value')

# Pilot area's harvestable area
if 'Area_harvestable_pilotArea_assume_ha' in locals():
    print('Area_harvestable_pilotArea_assume_ha exists')
else:
    Area_harvestable_pilotArea_assume_ha = None
    print('Area_harvestable_pilotArea_assume_ha was assigned null value')


# CARBON SEQUESTRATION
Genera_tree = "All"
Species_tree = "All"

# wood harvesting
woodHarvesting = 1

# import wood ESS map and calculate area or wood harvesting
# get area size (ha) of the country from the Danube_countries layer
idx_ess = ESmapStake_wood_layer.fields().indexFromName('ESS')
idx_area = ESmapStake_wood_layer.fields().indexFromName('Area_ha')
features_layer = ESmapStake_wood_layer.getFeatures()
# harvest area
Area_woodHarvest_pilotArea_ha = 249.1 # CS: 297.6 # RS1: 290.1 # RS2: 249.1 # None
if Area_woodHarvest_pilotArea_ha is None:
    Area_woodHarvest_pilotArea_ha = 0.0
    idx_ess = ESmapStake_wood_layer.fields().indexFromName('ESS')
    idx_area = ESmapStake_wood_layer.fields().indexFromName('Area_ha')
    features_layer = ESmapStake_wood_layer.getFeatures()
    for feat in features_layer:
        attributes_table = feat.attributes()
        if attributes_table[idx_ess] == 'wood':
            Area_woodHarvest_pilotArea_ha =  Area_woodHarvest_pilotArea_ha + float(attributes_table[idx_area])

# tree-dominated area
Area_treeDominated_pilotArea_ha = 0.0
idx_hab = ExtCBA2_EcosystemTypes_layer.fields().indexFromName('Habit_Code')
idx_area = ExtCBA2_EcosystemTypes_layer.fields().indexFromName('Area_ha')
features_layer = ExtCBA2_EcosystemTypes_layer.getFeatures()
for feat in features_layer:
    attributes_table = feat.attributes()
    if attributes_table[idx_hab] == 1:
        Area_treeDominated_pilotArea_ha =  Area_treeDominated_pilotArea_ha + float(attributes_table[idx_area])


# fuelwood and charcoal removals
fuelwood_or_charcoalRemoval = 1

#disturbances (illnesses or fire)
forestDisturbances = 1
Area_Disturbance_ha_yr = 249.1 # example # CS: 297.6 # RS1: 290.1 # RS2: 249.1
disturbance_info_m3_yr = 1
ForestDisturbance_m3_yr = 1850 # year 2019
# ABG_Disturbance_ton_dry_mass_per_ha = 0 # 1850 cubic meters of wood
# Disturbance_Fraction = 0.0 # example (e.g. due to insect, fire would be DF = 1)

#MUST BE CHANGED -------------------------------------------------------------------------------------------------------
# AREA CHARACTERISTICS - end --------------------------------------------------------------------------------------




# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- AGB
# -------------------------------------------------------------------------------------------------------------
# tree-dominated habitats
agb_ton_dm_per_ha_forest = readTable_IPCC_4_7(IPCC_table_4_7,continent,climate_reg,forest_ecoZone, forest_age_bool)
# grass-dominated and wetland-dominated habitats
# from Anderson-Teixeira and deLucia, 2011
agb_ton_dm_per_ha_grass, agb_ton_dm_per_ha_wetland, bgb_ton_dm_per_ha_wetland, litter_ton_dm_per_ha_grass, litter_ton_dm_per_ha_wetland, dead_ton_dm_per_ha_forest, dead_ton_dm_per_ha_grass, dead_ton_dm_per_ha_wetland = readTable_Anderson_Teixera_2011(table_Anderson_Teixera_2011,continent,climate_reg,grassland_ecoZone,wetland_ecoZone,naturalness_type)


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- BGB
# -------------------------------------------------------------------------------------------------------------
# BGB: for crude estimates of below-ground live biomass carbon stocks:
#Table 4.4 (for tree-dominated areas, perennial crops and urban parks) in Chapter 4 of IPCC (2006) 
#Table 6.1 (for grass-dominated or woody savannah and urban lawns) in Chapter 6 of IPCC (2006)
#For freshwater wetlands, there are no IPCC default factors for below ground biomass calculation. 
#Therefore, use locally applicable published values (as a rule of thumb, the conversion
#factor is 0.3 for annual wetland vegetation species without rhizomes (Cronk & Fennessy 2001))
#Otherwise, see table_Anderson_Teixera_2011, for a relevant estimate of below-ground biomass for your habitat.

# tree-dominated habitats
bgb_ton_dm_per_ha_forest = readTable_IPCC_4_4(IPCC_table_4_4,agb_ton_dm_per_ha_forest,continent,climate_reg,forest_ecoZone, tree_species)
# grass-dominated habitats
bgb_ton_dm_per_ha_grass = readTable_IPCC_6_1(IPCC_table_6_1,agb_ton_dm_per_ha_grass,continent,climate_reg,grass_vegetation_type)
# wetland-dominated habitats
# already gotten from Anderson-Teixeira and deLucia, 2011
print("BGB unit for specific area with wetland: " + str(bgb_ton_dm_per_ha_wetland) + " tonnes dm/ha")


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- LITTER AND DEAD WOOD
# -------------------------------------------------------------------------------------------------------------

# tree-dominated habitats
# LITTER: get indexes colums from the table IPCC_table_2_2
litter_ton_dm_per_ha_forest = readTable_IPCC_2_2(IPCC_table_2_2,continent,climate_reg,climate_reg2,tree_species2)

# DEAD WOOD: already gotten from Anderson-Teixeira and deLucia, 2011
print("DEAD unit for specific area with trees: " + str(dead_ton_dm_per_ha_forest) + " tonnes dm/ha")

# grass-dominated habitats
# already gotten from Anderson-Teixeira and deLucia, 2011
print("LITTER unit for specific area with grassland: " + str(litter_ton_dm_per_ha_grass) + " tonnes dm/ha")
print("DEAD unit for specific area with grassland: " + str(dead_ton_dm_per_ha_grass) + " tonnes dm/ha")

# wetland-dominated habitats
# already gotten from Anderson-Teixeira and deLucia, 2011
print("LITTER unit for specific area with wetland: " + str(litter_ton_dm_per_ha_wetland) + " tonnes dm/ha")
print("DEAD unit for specific area with wetland: " + str(dead_ton_dm_per_ha_wetland) + " tonnes dm/ha")

# get specific value for soil organic matter 


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- CALCULATE SEPARATE SECTIONS
# -------------------------------------------------------------------------------------------------------------

# create copy of the habitats file to save the results 
carbonStocks_layer = createCopy_habitatsShapefile(ExtCBA2_EcosystemTypes_layer, 'A_climate_output01_carbon_stocks')


# STEP 1: Above ground live biomass ---
#To calculate the total above-ground live biomass of each habitat at the site, multiply above-ground live biomass by
#the area (ha) of the habitat.

# STEP 1A: Create AboveGroundBiomass_ton_dry_mass_per_ha: create new field on new shapefile to save new results --- (from: https://gis.stackexchange.com/questions/197726/adding-field-and-calculating-expression-with-pyqgis)
# create field
myField = QgsField( 'AboveGroundBiomass_ton_dry_mass_per_ha', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_AGB = carbonStocks_layer.fields().indexFromName('AboveGroundBiomass_ton_dry_mass_per_ha')
id_habitat_code = carbonStocks_layer.fields().indexFromName('Habit_Code')
#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
    if f[id_habitat_code] == 1 : # tree-dominated
        f[idx_AGB] = agb_ton_dm_per_ha_forest
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 2 : #grass-dominated
        f[idx_AGB] = agb_ton_dm_per_ha_grass
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 3 : #crop-dominated, no rice
        if cultivation_type == "annual":
            f[idx_AGB] = agb_ton_dm_per_ha_crop_annual 
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 4 : #crop-dominated, rice
        # to finish
        f[idx_AGB] = agb_ton_dm_per_ha_rice
    elif f[id_habitat_code] == 5 : # wetland
        f[idx_AGB] = agb_ton_dm_per_ha_wetland
        # update the feature
        carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()

# STEP 1B: Create Total_AboveGround_CarbonStock_tonnes
# Conversion factors
#0.5 for tree-dominated, forest plantations, woody savannas, perennial crop-dominated habitats and urban parks
#0.47 for grass-dominated habitats, inland wetlands and urban lawn
myField = QgsField( 'Total_AboveGround_CarbonStock_tonnes', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_AGB = carbonStocks_layer.fields().indexFromName('AboveGroundBiomass_ton_dry_mass_per_ha')
idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
idx_AGCS = carbonStocks_layer.fields().indexFromName('Total_AboveGround_CarbonStock_tonnes')

#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
    if f[id_habitat_code] == 1 : # tree-dominated
        # if it is a forest
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_AGCS] = f[idx_AGB] * f[idx_HA] * 0.5
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 2 : #grass-dominated
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_AGCS] = f[idx_AGB] * f[idx_HA] * 0.47
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 3 : #crop-dominated, no rice
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_AGCS] = f[idx_AGB] * f[idx_HA] * 0.5
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 4 : #crop-dominated, rice
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_AGCS] = f[idx_AGB] * f[idx_HA] * 0.47
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 5 : # wetland
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_AGCS] = f[idx_AGB] * f[idx_HA] * 0.47
        # update the feature
        carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()

# STEP 2: Below ground live biomass ---
# STEP 2A: Create BelowGroundBiomass_ton_dry_mass_per_ha field
#create field
myField = QgsField( 'BelowGroundBiomass_ton_dry_mass_per_ha', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_AGB = carbonStocks_layer.fields().indexFromName("AboveGroundBiomass_ton_dry_mass_per_ha")
idx_BGB = carbonStocks_layer.fields().indexFromName('BelowGroundBiomass_ton_dry_mass_per_ha')
#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
    if f[id_habitat_code] == 1 : # tree-dominated
        # if it is a forest
        f[idx_BGB] = bgb_ton_dm_per_ha_forest
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 2 : #grass-dominated
        # if it is a grass
        f[idx_BGB] = bgb_ton_dm_per_ha_grass
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 3 : #crop-dominated, no rice
        if cultivation_type == "annual":
            f[idx_BGB] = bgb_ton_dm_per_ha_crop_annual 
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 4 : #crop-dominated, rice
        # to finish
        f[idx_BGB] = bgb_ton_dm_per_ha_rice
    elif f[id_habitat_code] == 5 : # wetland
        # if it is a forest
        f[idx_BGB] = bgb_ton_dm_per_ha_wetland
        # update the feature
        carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()

# STEP 2B: Create Total_BelowGround_CarbonStock_tonnes
# Conversion factors
#0.5 for treedominated, forest plantations, woody savannas, perennial crop-dominated habitats and urban parks
#0.47 for grass-dominated habitats, inland wetlands and urban lawn
myField = QgsField( 'Total_BelowGround_CarbonStock_tonnes', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_BGB = carbonStocks_layer.fields().indexFromName('BelowGroundBiomass_ton_dry_mass_per_ha')
idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
idx_BGCS = carbonStocks_layer.fields().indexFromName('Total_BelowGround_CarbonStock_tonnes')
#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
    if f[id_habitat_code] == 1 : # tree-dominated
        # if it is a forest
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_BGCS] = f[idx_BGB] * f[idx_HA] * 0.5
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 2 : #grass-dominated
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_BGCS] = f[idx_BGB] * f[idx_HA] * 0.47
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 3 : #crop-dominated, no rice
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_BGCS] = f[idx_BGB] * f[idx_HA] * 0.5
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 4 : #crop-dominated, rice
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_BGCS] = f[idx_BGB] * f[idx_HA] * 0.47
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 5 : # wetland
        # multiply by the factor according to Fourqurean et al 2012
        f[idx_BGCS] = f[idx_BGB] * f[idx_HA] * 0.47
        # update the feature
        carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()

# STEP 3: Litter biomass ---
# STEP 3A: Create Litter_ton_dry_mass_per_ha field
#create field
myField = QgsField( 'Litter_ton_dry_mass_per_ha', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_LTT = carbonStocks_layer.fields().indexFromName('Litter_ton_dry_mass_per_ha')

#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
    if f[id_habitat_code] == 1 : # tree-dominated
        # if it is a forest
        f[idx_LTT] = litter_ton_dm_per_ha_forest
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 2 : #grass-dominated
        # if it is a grass
        f[idx_LTT] = litter_ton_dm_per_ha_grass
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 3 : #crop-dominated, no rice
        if cultivation_type == "annual":
            f[idx_LTT] = litter_ton_dm_per_ha_crop_annual 
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 4 : #crop-dominated, rice
        # to finish
        f[idx_LTT] = litter_ton_dm_per_ha_rice
    elif f[id_habitat_code] == 5 : # wetland
        # if it is a forest
        f[idx_LTT] = litter_ton_dm_per_ha_wetland
        # update the feature
        carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()

# STEP 4: Dead wood biomass ---
# STEP 4A: Create DeadWood_ton_dry_mass_per_ha field
#create field
myField = QgsField( 'DeadWood_ton_dry_mass_per_ha', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_DEAD = carbonStocks_layer.fields().indexFromName('DeadWood_ton_dry_mass_per_ha')
#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # print("gridcode: "+f[1]+"; agb rate: " f[idx_new_field])
    if f[id_habitat_code] == 1 : # tree-dominated
        # if it is a forest
        f[idx_DEAD] = dead_ton_dm_per_ha_forest
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 2 : #grass-dominated
        # if it is a grass
        f[idx_DEAD] = dead_ton_dm_per_ha_grass
        # update the feature
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 3 : #crop-dominated, no rice
        if cultivation_type == "annual":
            f[idx_DEAD] = dead_ton_dm_per_ha_crop_annual 
        carbonStocks_layer.updateFeature( f )
    elif f[id_habitat_code] == 4 : #crop-dominated, rice
        # to finish
        f[idx_DEAD] = dead_ton_dm_per_ha_rice
    elif f[id_habitat_code] == 5 : # wetland
        # if it is a forest
        f[idx_DEAD] = dead_ton_dm_per_ha_wetland
        # update the feature
        carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()

# STEP 3&4B: Create Total_DeadOrganic_CarbonStock_tonnes
# Conversion factors compared to total dry mass
#Litter carbon stock assumed to be 50% (IPCC 2006)
#Dead wood carbon stock 40% (IPCC 2006)
myField = QgsField( 'Total_DeadOrganic_CarbonStock_tonnes', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')
idx_LTT = carbonStocks_layer.fields().indexFromName('Litter_ton_dry_mass_per_ha')
idx_DEAD = carbonStocks_layer.fields().indexFromName('DeadWood_ton_dry_mass_per_ha')
idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
idx_DORG = carbonStocks_layer.fields().indexFromName('Total_DeadOrganic_CarbonStock_tonnes')
#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # multiply by the factor according to IPCC, 2006
    if f[idx_HAB]!=0:
       litter_tmp = f[idx_LTT] * f[idx_HA] * 0.5
       deadWood_tmp = f[idx_DEAD] * f[idx_HA] * 0.4
       #f[idx_DORG] = litter_tmp + deadWood_tmp
       f[idx_DORG] = float(numpy.nansum([litter_tmp,deadWood_tmp]))
    carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()



# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- SOIL ORGANIC CARBON WITH MAP
# -------------------------------------------------------------------------------------------------------------
if soil_type == "organic":
    # SOIL ORGANIC CARBON MAP: extract SOC from the imported raster file and save it in carbonStocks_layer
    carbonStocks_layer.startEditing() 
    # usage - QgsZonalStatistics (QgsVectorLayer *polygonLayer, QgsRasterLayer *rasterLayer, const QString &attributePrefix="", int rasterBand=1)
    # QgsRasterLayer 
    zoneStat = QgsZonalStatistics (carbonStocks_layer, SOC_ton_per_ha_raster, 'SoilOrganicCarbon_ton_per_ha_', 1, QgsZonalStatistics.Mean)
    zoneStat.calculateStatistics(None)
    carbonStocks_layer.commitChanges()

    # Create Total_SOM_CarbonStock_tonnes
    myField = QgsField( 'Total_SOM_CarbonStock_tonnes', QVariant.Double )
    carbonStocks_layer.dataProvider().addAttributes([myField])
    carbonStocks_layer.updateFields()
    idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')
    idx_SOM = carbonStocks_layer.fields().indexFromName('SoilOrganicCarbon_ton_per_ha_mean')
    idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
    idx_TSOM = carbonStocks_layer.fields().indexFromName('Total_SOM_CarbonStock_tonnes')
    #start editing
    carbonStocks_layer.startEditing()
    for f in carbonStocks_layer.getFeatures():
        # multiply by the factor according to IPCC, 2006
        if f[idx_HAB]!=0:
           f[idx_TSOM] = f[idx_SOM]*f[idx_HA]
        carbonStocks_layer.updateFeature( f )
    # commit changes
    carbonStocks_layer.commitChanges()

# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- SOIL ORGANIC CARBON WITH TRIER 1
# -------------------------------------------------------------------------------------------------------------
# 1) Get SOC_REF_tonC_ha from Table 2.3 (2006) if tree-dominated, grass-dominated, or crop-dominated
#       If grass-dominated is managed, then read factors F_LU, F_MG, and F_I from Table 6.2 (2006), then SOC_REF_tonC_ha = SOC_REF_tonC_ha * F_LU * F_MG * F_I
#       If crop-dominated is managed, then read factors F_LU, F_MG, and F_I from Table 5.5 (2006) or 5.3 (2014), then SOC_REF_tonC_ha = SOC_REF_tonC_ha * F_LU * F_MG * F_I
# 2) Get SOC_REF_tonC_ha from Table 5.2 (2014) if wetland dominated habitats
# 3) Multiply by Area (ha)
# 4) Sum

if soil_type == "mineral":
    # use trier 1 method
    # READ TABLES FOR FACTORS
    soc_per_ha_general = readTable_IPCC_2_3(IPCC_table_2_3,climate_reg,climate_reg2,soil_type_fromMap)
    factor_SOC_crop_landuse = readTable_IPCC_5_5(IPCC_table_5_5,climate_reg,moisture_regime,level_landuse,"land use")
    factor_SOC_crop_management = readTable_IPCC_5_5(IPCC_table_5_5,climate_reg,moisture_regime,level_management,"management")
    factor_SOC_crop_input = readTable_IPCC_5_5(IPCC_table_5_5,climate_reg,moisture_regime,level_input,"input")
    factor_SOC_grass_landuse = readTable_IPCC_6_2(IPCC_table_6_2,climate_reg,"land use")
    factor_SOC_grass_management = readTable_IPCC_6_2(IPCC_table_6_2,climate_reg,"management")
    factor_SOC_grass_input = readTable_IPCC_6_2(IPCC_table_6_2,climate_reg,"input")
    factor_SOC_grass_drained_input = readTable_IPCC_5_3_2014(IPCC_table_5_3_2014,climate_reg,level_landuse)
    soc_per_ha_wetland = readTable_IPCC_5_2_2014(IPCC_table_5_2_2014,climate_reg,climate_reg2,"wetland")

    # Create Total_SOM_CarbonStock_tonnes
    myField = QgsField( 'SoilOrganicCarbon_ton_per_ha_mean', QVariant.Double )
    carbonStocks_layer.dataProvider().addAttributes([myField])
    myField = QgsField( 'Total_SOM_CarbonStock_tonnes', QVariant.Double )
    carbonStocks_layer.dataProvider().addAttributes([myField])
    carbonStocks_layer.updateFields()
    # carbon stocks
    carbonStocks_layer.startEditing() 
    idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')
    idx_SOM = carbonStocks_layer.fields().indexFromName('SoilOrganicCarbon_ton_per_ha_mean')
    idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
    idx_TSOM = carbonStocks_layer.fields().indexFromName('Total_SOM_CarbonStock_tonnes')

    #start editing for aving the SoilOrganicCarbon_ton_per_ha_mean
    carbonStocks_layer.startEditing()

    for f in carbonStocks_layer.getFeatures():
        if f[id_habitat_code] == 1 : # tree-dominated
            f[idx_SOM] = soc_per_ha_general
            # update the feature
            carbonStocks_layer.updateFeature( f )
        elif f[id_habitat_code] == 2 : #grass-dominated
            if naturalness_type == "managed":
                f[idx_SOM] = soc_per_ha_general * factor_SOC_grass_landuse * factor_SOC_grass_management * factor_SOC_grass_input
            else:
                f[idx_SOM] = soc_per_ha_general
            # update the feature
            carbonStocks_layer.updateFeature( f )
        elif f[id_habitat_code] == 3 : #crop-dominated, no rice
            f[idx_SOM] = soc_per_ha_general *  factor_SOC_crop_landuse * factor_SOC_crop_management * factor_SOC_crop_input
            carbonStocks_layer.updateFeature( f )
        elif f[id_habitat_code] == 4 : #crop-dominated, rice
            f[idx_SOM] = soc_per_ha_general
        elif f[id_habitat_code] == 5 : # wetland
            f[idx_SOM] = soc_per_ha_wetland
            # update the feature
            carbonStocks_layer.updateFeature( f )
    # commit changes
    carbonStocks_layer.commitChanges()

    #start editing for aving the Total_SOM_CarbonStock_tonnes
    carbonStocks_layer.startEditing()
    for f in carbonStocks_layer.getFeatures():
        if f[idx_HAB]!=0:
           f[idx_TSOM] = float(f[idx_SOM])*float(f[idx_HA])
        carbonStocks_layer.updateFeature( f )
    # commit changes
    carbonStocks_layer.commitChanges()



# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- CALCULATE TOTAL CARBON STOCKS
# -------------------------------------------------------------------------------------------------------------
# Calculate total C stock
Total_AboveGround_CarbonStock_ton = 0.0
Total_BelowGround_CarbonStock_ton = 0.0
Total_DeadOrganic_CarbonStock_ton = 0.0
Total_SOM_CarbonStock_ton = 0.0

TotalCarbonStock_ton = 0.0

# Create TotalCarbonStock_tonnes
myField = QgsField( 'TotalCarbonStock_tonnes', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
myField2 = QgsField( 'TotalCarbonStock_ton_per_ha', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField2])
carbonStocks_layer.updateFields()
idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')
idx_AGCS = carbonStocks_layer.fields().indexFromName('Total_AboveGround_CarbonStock_tonnes')
idx_BGCS = carbonStocks_layer.fields().indexFromName('Total_BelowGround_CarbonStock_tonnes')
idx_DORG = carbonStocks_layer.fields().indexFromName('Total_DeadOrganic_CarbonStock_tonnes')
idx_TSOM = carbonStocks_layer.fields().indexFromName('Total_SOM_CarbonStock_tonnes')
idx_TCS = carbonStocks_layer.fields().indexFromName('TotalCarbonStock_tonnes')
idx_SpTCS = carbonStocks_layer.fields().indexFromName('TotalCarbonStock_ton_per_ha')
idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')

#create empty list
Spatial_TotalCarbonStock_list = []

#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # multiply by the factor according to IPCC, 2006
    if f[idx_HAB]!=0:
        array_sum_tmp = [float(f[idx_AGCS]) , f[idx_BGCS] , f[idx_DORG], f[idx_TSOM] ]
        sumCstock_ton_tmp = float(numpy.nansum(array_sum_tmp))
        f[idx_TCS] = sumCstock_ton_tmp
        f[idx_SpTCS] = float(f[idx_TCS])/float(f[idx_HA])
        Spatial_TotalCarbonStock_list.append(f[idx_SpTCS])
        
        Total_AboveGround_CarbonStock_ton = float(numpy.nansum([Total_AboveGround_CarbonStock_ton,float(f[idx_AGCS]) ]))
        Total_BelowGround_CarbonStock_ton = float(numpy.nansum([Total_BelowGround_CarbonStock_ton,float(f[idx_BGCS]) ]))
        Total_DeadOrganic_CarbonStock_ton = float(numpy.nansum([Total_DeadOrganic_CarbonStock_ton,float(f[idx_DORG]) ]))
        Total_SOM_CarbonStock_ton = float(numpy.nansum([Total_SOM_CarbonStock_ton,float(f[idx_TSOM]) ]))
        
        TotalCarbonStock_ton = TotalCarbonStock_ton + sumCstock_ton_tmp
    carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()


# REPRESENT TOTAL CARBON STOCKS
min_value = min(Spatial_TotalCarbonStock_list)
max_value = max(Spatial_TotalCarbonStock_list)
join_layer = carbonStocks_layer
target_field = "TotalCarbonStock_ton_per_ha"
apply_graduated_symbology_10(join_layer, target_field, min_value, max_value)


# SAVE CALCULATED TOTAL CARBON STOCKS IN TONS
QgsVectorFileWriter.writeAsVectorFormat(carbonStocks_layer, str(tool_path + "/OutputData_ES/A_climate_carbon_stocks/A_climate_output01_carbon_stocks_"+scenarioID+".shp"),"UTF-8", carbonStocks_layer.crs(), "ESRI Shapefile")

# write txt file with result 
output_txt_file_path = tool_path + "OutputData_ES/A_climate_carbon_stocks/A_climate_output01_carbon_stocks_"+scenarioID+".txt"
file_to_write = open(output_txt_file_path, 'w')
file_to_write.write(str("TotalCarbonStock_ton: " + str(TotalCarbonStock_ton)+ " ton"+'\n\n'+
"Total_AboveGround_CarbonStock_ton: " + str(Total_AboveGround_CarbonStock_ton)+ " ton"+'\n'+
"Total_BelowGround_CarbonStock_ton: " + str(Total_BelowGround_CarbonStock_ton)+ " ton"+'\n'+
"Total_DeadOrganic_CarbonStock_ton: " + str(Total_DeadOrganic_CarbonStock_ton)+ " ton"+'\n'+
"Total_SOM_CarbonStock_ton: " + str(Total_SOM_CarbonStock_ton)+ " ton"+'\n'
))
# close 
file_to_write.close()



# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A to B: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- INCREMENT IN C and GROSS C SEQUESTRATION
# -------------------------------------------------------------------------------------------------------------
# growing rates of planted trees taken from the database Plantes Forests Database (PFDB)
# http://www.fao.org/3/y9933e/Y9933E12.htm#P5195_171494



# MAI [m3_per_ha_yr]: Assume that the change of carbon stock takes place in the tree-dominated area only
MAI_m3_per_ha_yr = readTable_FAO_MAI(table_FAOSTAT_MAI,Genera_tree, Species_tree)

# CF [tonC_per_ton_dm]
# get Carbon Fraction to dry matter of wood from table 4.3 
CarbonFraction_tonC_per_ton_d_m = readTable_IPCC_4_3(IPCC_table_4_3,climate_reg,tree_type)

# BCEF_I [ton_per_m3]
Forest_Area_country_ha, GrowingStock_country_m3_yr, FAOstats_year = readTable_FAO_ForestResourcesAssessment(table_FAO_FRA2015, country)
# get growing stock level to get data from tabe 4.5
GrowingStockLevel_country_m3_per_ha = GrowingStock_country_m3_yr/Forest_Area_country_ha
# get BCEF_I from table 4.5
BCEF_I = readTable_IPCC_4_5(IPCC_table_4_5,climate_reg,tree_type2,GrowingStockLevel_country_m3_per_ha,"BCEF_I")

# IncrementWood
AnnualCarbonIncrement_Trees_tonC_per_yr_ha = MAI_m3_per_ha_yr*BCEF_I*CarbonFraction_tonC_per_ton_d_m


# save the gross carbon sequestration per year
myField = QgsField( 'MAI_m3_per_ha_yr', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
myField2 = QgsField( 'CarbonStock_Increment_ton_per_yr', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField2])
carbonStocks_layer.updateFields()
idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')
idx_MAI = carbonStocks_layer.fields().indexFromName('MAI_m3_per_ha_yr')
idx_ACI = carbonStocks_layer.fields().indexFromName('CarbonStock_Increment_ton_per_yr')
idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
#start editing
Annual_GrossCarbonSequestration_PiloArea_tonC_per_yr = 0.0
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # multiply by the factor according to IPCC, 2006
    if f[idx_HAB]==1: # tree-dominated
        f[idx_MAI] = MAI_m3_per_ha_yr
        f[idx_ACI] = AnnualCarbonIncrement_Trees_tonC_per_yr_ha * f[idx_HA]
        print("AnnualCarbonIncrement_Trees_tonC_per_yr: " + str(f[idx_ACI]))
        Annual_GrossCarbonSequestration_PiloArea_tonC_per_yr += f[idx_ACI]
    carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()

print('ASSUMPTION: gross carbon sequestration per year comes only from the tree-dominated habitats')

# write txt file with result 
output_txt_file_path = tool_path + "OutputData_ES/A_climate_carbon_stocks/A_climate_output01_Annual_GrossCarbonSequestration_"+scenarioID+".txt"
file_to_write = open(output_txt_file_path, 'w')
file_to_write.write(str("Annual_GrossCarbonSequestration_PiloArea_tonC_per_yr: " + str(Annual_GrossCarbonSequestration_PiloArea_tonC_per_yr)+ " ton/yr"+'\n'
))
# close 
file_to_write.close()


# -------------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A to B: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- CALCULATE C STOCK LOSSES in tree-dominated areas
# -------------------------------------------------------------------------------------------------------------------

# total losses = #L_WOODREMOVALS + L_FUELWOOD + L_DISTURBANCE

# LOSS OF VEGETATION CARBON STOCK = ABOVE GROUND BIOMASS REMOVALS  --------------------------------------------------------------------------------------------

# if the site experiencing wood harvesting
# or 
# if the site is experiencing fuelwood or charocoal removals 
if woodHarvesting == 1 or fuelwood_or_charcoalRemoval == 1:
    # get Carbon Fraction to dry matter of wood from table 4.3 
    CarbonFraction_tonC_per_ton_d_m = readTable_IPCC_4_3(IPCC_table_4_3,climate_reg,tree_type)

    # Global Forest Resources Assessment (FRA) 2015 is needed to know the Growing Stock level in m3/ha
    # get data from FAO table: FAO_ForestResourcesAssessment_2015
    Forest_Area_country_ha, GrowingStock_country_m3_yr, FAOstats_year = readTable_FAO_ForestResourcesAssessment(table_FAO_FRA2015, country)

    # get growing stock level to get data from tabe 4.5
    GrowingStockLevel_country_m3_per_ha = GrowingStock_country_m3_yr/Forest_Area_country_ha

    # get BCEF_R from table 4.5
    BCEF_R = readTable_IPCC_4_5(IPCC_table_4_5,climate_reg,tree_type2,GrowingStockLevel_country_m3_per_ha, "BCEF_R")
        
    # get wood removal values
    AnnualRoundwoodRemoval_country_m3_per_year, AnnualFuelwoodRemoval_country_m3_per_year, AnnualCharocoalRemoval_country_m3_per_year = readTable_FAOSTAT_wood(table_FAOSTAT_wood,country,FAOstats_year)
    
    # 1) L_WOODREMOVALS = H x BCEF_R x CF --- * --- * ---
    if woodHarvesting == 1:
        # get harvest area in Hungary from FAO statistics of "Planted Forest"
        Area_woodHarvest_country_ha = readTable_FAOSTAT_landuse(table_FAOSTAT_landuse,country,FAOstats_year,"Planted Forest")
        # multiply annual roundwood removals times 1.15
        R_areas_woodHarvest_pilot_country = Area_woodHarvest_pilotArea_ha/Area_woodHarvest_country_ha
        # H: annual roundwood removals for the area = annual national * ratio * 1.15
        AnnualRoundwoodRemoval_pilotArea_m3_per_year = AnnualRoundwoodRemoval_country_m3_per_year*R_areas_woodHarvest_pilot_country*1.15
        # L_WOODREMOVALS
        AnnualCarbonLoss_WoodRemoval_tonC_per_yr = AnnualRoundwoodRemoval_pilotArea_m3_per_year*BCEF_R*CarbonFraction_tonC_per_ton_d_m
        # per ha
        AnnualCarbonLoss_WoodRemoval_tonC_per_ha_yr = AnnualCarbonLoss_WoodRemoval_tonC_per_yr/Area_woodHarvest_pilotArea_ha
    else:
        print("The pilot area is not experiencing any C losses from wood harvesting")
        AnnualCarbonLoss_WoodRemoval_tonC_per_yr = 0.0
        # per ha
        AnnualCarbonLoss_WoodRemoval_tonC_per_ha_yr = 0.0
    #2) L_FUELWOOD = FG x BCEF_R x CF --- * --- * ---
    if fuelwood_or_charcoalRemoval == 1:
        # FG: annual fuelwood and charcoal removals = annual national * ratio
        AnnualFuelwoodRemoval_m3_per_ha_year = (AnnualFuelwoodRemoval_country_m3_per_year+AnnualCharocoalRemoval_country_m3_per_year)/Area_woodHarvest_country_ha
        AnnualFuelwoodRemoval_m3_per_year = AnnualFuelwoodRemoval_m3_per_ha_year*Area_woodHarvest_pilotArea_ha
        # L_FUELWOOD
        AnnualCarbonLoss_Fuelwood_tonC_per_yr = AnnualFuelwoodRemoval_m3_per_year*BCEF_R*CarbonFraction_tonC_per_ton_d_m
        # per hacc
        AnnualCarbonLoss_Fuelwood_tonC_per_ha_yr = AnnualCarbonLoss_Fuelwood_tonC_per_yr/ Area_woodHarvest_pilotArea_ha
    else:
        print("The pilot area is not experiencing any C losses from wood removals or charcoal removal")
        AnnualCarbonLoss_Fuelwood_tonC_per_yr = 0.0
        # per ha
        AnnualCarbonLoss_Fuelwood_tonC_per_ha_yr = 0.0
    

else:
    print("The pilot area is not experiencing any C losses from wood harvesting")
    print("The pilot area is not experiencing any C losses from wood removals or charcoal removal")
    AnnualCarbonLoss_WoodRemoval_tonC_per_yr = 0.0
    AnnualCarbonLoss_Fuelwood_tonC_per_yr = 0.0
    # per ha
    AnnualCarbonLoss_WoodRemoval_tonC_per_ha_yr = 0.0
    AnnualCarbonLoss_Fuelwood_tonC_per_ha_yr = 0.0

# if the site experiences disturbances (e.g. fire, insect damage)
if forestDisturbances == 1:
    #Annual decrease in carbon stocks due to biomass loss = -------------------  
    #3A) L_DISTURBANCE = A * B* CF --- * --- * ---
    if disturbance_info_m3_yr == 0:
        AnnualCarbonLoss_Disturbance_tonC_per_yr = CarbonFraction_tonC_per_ton_d_m * Area_Disturbance_ha_yr * ABG_Disturbance_ton_dry_mass_per_ha * Disturbance_Fraction
        # per ha (TO CORRECT!)
        AnnualCarbonLoss_Disturbance_tonC_per_ha_yr = AnnualCarbonLoss_Disturbance_tonC_per_yr/Area_woodHarvest_pilotArea_ha
    # 3B) if we have the losses in m3
    elif disturbance_info_m3_yr == 1:
        # BCEF_S [ton_per_m3] (biomass conversion)
        Forest_Area_country_ha, GrowingStock_country_m3_yr, FAOstats_year = readTable_FAO_ForestResourcesAssessment(table_FAO_FRA2015, country)
        # get growing stock level to get data from tabe 4.5
        GrowingStockLevel_country_m3_per_ha = GrowingStock_country_m3_yr/Forest_Area_country_ha
        # get BCEF_S from table 4.5
        BCEF_S = readTable_IPCC_4_5(IPCC_table_4_5,climate_reg,tree_type2,GrowingStockLevel_country_m3_per_ha,"BCEF_S")
        # get tons C of disturbance
        AnnualCarbonLoss_Disturbance_tonC_per_yr = ForestDisturbance_m3_yr*BCEF_S*CarbonFraction_tonC_per_ton_d_m
        AnnualCarbonLoss_Disturbance_tonC_per_ha_yr = AnnualCarbonLoss_Disturbance_tonC_per_yr/Area_woodHarvest_pilotArea_ha
        
else:
    print("The pilot area is not experiencing any C losses from disturbances")
    AnnualCarbonLoss_Disturbance_tonC_per_yr = 0.0
    # per ha
    AnnualCarbonLoss_Disturbance_tonC_per_ha_yr = 0.0


#Annual decrease in carbon stocks due to biomass loss = -------------------
#L_WOODREMOVALS + L_FUELWOOD + L_DISTURBANCE
AnnualCarbonLoss_Total_tonC_per_yr =  AnnualCarbonLoss_WoodRemoval_tonC_per_yr + AnnualCarbonLoss_Fuelwood_tonC_per_yr + AnnualCarbonLoss_Disturbance_tonC_per_yr 
print("Total losses of tons C per year: " + str(AnnualCarbonLoss_Total_tonC_per_yr))

# write txt file with result 
output_txt_file_path = tool_path + "OutputData_ES/A_climate_carbon_stocks/A_climate_output01_Annual_CarbonLoss_"+scenarioID+".txt"
file_to_write = open(output_txt_file_path, 'w')
file_to_write.write(str("AnnualCarbonLoss_Total_tonC_per_yr: " + str(AnnualCarbonLoss_Total_tonC_per_yr)+ " ton/yr"+'\n'
))
# close 
file_to_write.close()

# Represent this spatially in the carbon stocks shapefile -------------------------------------------------------------
AnnualCarbonLoss_Total_tonC_per_ha_yr = AnnualCarbonLoss_Total_tonC_per_yr/Area_treeDominated_pilotArea_ha

myField = QgsField( 'C_Losses_ton_per_yr', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')
idx_CLO = carbonStocks_layer.fields().indexFromName('C_Losses_ton_per_yr')
idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
#start editing
AnnualCarbonLoss_Total_tonC_per_yr_test = 0
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # multiply by the factor according to IPCC, 2006
    if f[idx_HAB]==1:
        f[idx_CLO] = AnnualCarbonLoss_Total_tonC_per_ha_yr * f[idx_HA]
        print("AnnualCarbonLosses_Trees_tonC_per_yr: " + str(f[idx_CLO]))
        AnnualCarbonLoss_Total_tonC_per_yr_test += f[idx_CLO]
    carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- CALCULATE NET CARBON SEQUESTRATION
# -------------------------------------------------------------------------------------------------------------

Annual_NetCarbonSequestration_PilotArea_tonC_per_yr = Annual_GrossCarbonSequestration_PiloArea_tonC_per_yr - AnnualCarbonLoss_Total_tonC_per_yr
print("Annual Net Carbon Sequestration in tons C per year: " + str(Annual_NetCarbonSequestration_PilotArea_tonC_per_yr))


# Represent this spatially in the carbon stocks shapefile
NetCarbonSequestration_tonC_per_ha_yr = Annual_NetCarbonSequestration_PilotArea_tonC_per_yr/Area_treeDominated_pilotArea_ha

myField = QgsField( 'NetCseq_ton_per_yr', QVariant.Double )
carbonStocks_layer.dataProvider().addAttributes([myField])
carbonStocks_layer.updateFields()
idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')
idx_NET = carbonStocks_layer.fields().indexFromName('NetCseq_ton_per_yr')
idx_HA = carbonStocks_layer.fields().indexFromName('Area_ha')
#start editing
carbonStocks_layer.startEditing()
for f in carbonStocks_layer.getFeatures():
    # multiply by the factor according to IPCC, 2006
    if f[idx_HAB]==1:
        f[idx_NET] = NetCarbonSequestration_tonC_per_ha_yr * f[idx_HA]
        print("Net carbon sequestration for trees [tonC/yr]: " + str(f[idx_NET]))
    carbonStocks_layer.updateFeature( f )
# commit changes
carbonStocks_layer.commitChanges()


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- CALCULATE NET CARBON SEQUESTRATION ON ESS MAP
# -------------------------------------------------------------------------------------------------------------

# netCsequestration_layer = createCopy_Shapefile(ESmapStake_wood_layer, 'A_climate_output01b_carbon_seq', 'FID_1')
netCsequestration_layer = createCopy_Shapefile(ExtCBA2_EcosystemTypes_layer, 'A_climate_output01b_carbon_seq', 'FID_1')

# losses per ha
AnnualCarbonLoss_WoodRemoval_tonC_per_ha_yr
AnnualCarbonLoss_Fuelwood_tonC_per_ha_yr
AnnualCarbonLoss_Disturbance_tonC_per_ha_yr
AnnualCarbonLoss_Total_tonC_per_ha_yr

# wood increment
AnnualCarbonIncrement_Trees_tonC_per_yr_ha

# Represent this spatially in the wood removal shapefile
myField_1 = QgsField( 'Cincr_ton_per_yr', QVariant.Double )
myField_2 = QgsField( 'Closses_ton_per_yr', QVariant.Double )
myField_3 = QgsField( 'NetCseq_ton_per_yr', QVariant.Double )
myField_4 = QgsField( 'NetCO2eq_ton_per_yr', QVariant.Double )
myField_5 = QgsField( 'CO2eqHA', QVariant.Double )


netCsequestration_layer.dataProvider().addAttributes([myField_1,myField_2,myField_3,myField_4,myField_5])
netCsequestration_layer.updateFields()

# write
idx_CIN = netCsequestration_layer.fields().indexFromName('Cincr_ton_per_yr')
idx_CLO = netCsequestration_layer.fields().indexFromName('Closses_ton_per_yr')
idx_NET = netCsequestration_layer.fields().indexFromName('NetCseq_ton_per_yr')
idx_EQ = netCsequestration_layer.fields().indexFromName('NetCO2eq_ton_per_yr')
idx_perha = netCsequestration_layer.fields().indexFromName('CO2eqHA')

idx_HA = netCsequestration_layer.fields().indexFromName('Area_ha')
idx_HAB = carbonStocks_layer.fields().indexFromName('Habit_Code')

#start editing
Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr = 0.0
netCsequestration_layer.startEditing()
for f in netCsequestration_layer.getFeatures():
    if f[idx_HAB]==1:
        f[idx_CIN] = AnnualCarbonIncrement_Trees_tonC_per_yr_ha * f[idx_HA]
        f[idx_CLO] = AnnualCarbonLoss_Total_tonC_per_ha_yr * f[idx_HA]
        f[idx_NET] = f[idx_CIN]-f[idx_CLO]
        f[idx_EQ] = f[idx_NET] * 44.0/12.0
        f[idx_perha] = (AnnualCarbonIncrement_Trees_tonC_per_yr_ha-AnnualCarbonLoss_Total_tonC_per_ha_yr)* 44.0/12.0
        Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr += f[idx_NET]
    netCsequestration_layer.updateFeature( f )
# commit changes
netCsequestration_layer.commitChanges()


print("Annual Net Carbon Sequestration in tons C per year (stakeholders map): " + str(Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr))


# SAVE CALCULATED SEQUESTRED CARBON
QgsVectorFileWriter.writeAsVectorFormat(netCsequestration_layer, str(tool_path + "/OutputData_ES/A_climate_carbon_stocks/A_climate_output01b_carbon_seq_"+scenarioID+".shp"),"UTF-8", netCsequestration_layer.crs(), "ESRI Shapefile")


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - A: GLOBAL CLIMATE REGULATION - CARBON STORAGE -- SAVE NET CARBON SEQUESTRATION IN BOTH WAYS
# -------------------------------------------------------------------------------------------------------------


# write txt file with result 
output_txt_file_path = tool_path + "OutputData_ES/A_climate_carbon_stocks/A_climate_output01_Annual_NetCarbon_"+scenarioID+".txt"
file_to_write = open(output_txt_file_path, 'w')
file_to_write.write(str(
"Carbon increase is positive, Carbon loss is negative."+'\n'+
"Negative net value: C emissions"+'\n'+
"Positive net value: C sequestration"+'\n'+
"Annual Net Carbon Sequestration in tons C per year: " + str(Annual_NetCarbonSequestration_PilotArea_tonC_per_yr)+ " tonC/yr"+'\n'+
"Annual Net CO2 eq Sequestration in tons CO2eq per year: " + str(Annual_NetCarbonSequestration_PilotArea_tonC_per_yr*44.0/12.0)+ " tonCO2eq/yr"+'\n'+
"Annual Net Carbon Sequestration in tons C per year (stakeholders map): " + str(Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr)+ " tonC/yr"+'\n'+
"Annual Net CO2 eq Sequestration in tons CO2eq per year (stakeholders map): " + str(Annual_NetCarbonSequestrationWOOD_PilotArea_tonC_per_yr*44.0/12.0)+ " tonCO2eq/yr"+'\n'
))
# close 
file_to_write.close()


