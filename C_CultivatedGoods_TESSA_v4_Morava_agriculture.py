# C: CULTIVATED GOODS - AGICULTURE, LIVESTOCK, AQUACULTURE, FORESTRY 
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
from Import_C_CultivatedGoods_tables import *
from Import_C_CultivatedGoods_spatial import *
# from Functions_A_Climate_CarbonStorage_readTables import *
from Functions_C_CultivatedGoods_readTables import *
# from Functions_A_Climate_CarbonStorage_calculateResults import *

from qgis.analysis import QgsZonalStatistics

from osgeo import gdal




# -------------------------------------------------------------------------------------------------------------
# -- AREA CHARACTERISTICS  --
# -------------------------------------------------------------------------------------------------------------

#MUST BE CHANGED -------------------------------------------------------------------------------------------------------
# AREA CHARACTERISTICS - beginning -------------------------------------------------------------------------------
# define area characteristics 
continent = "Europe"
country = "Czechia" # "Slovenia" # "Serbia"
countryCode = "CZ" #"SI" # "RS"

cultivated_good_type = "_agriculture" # choose from "_agriculture" , "_fish", "_honey", "_livestock"

# selected major crops for the Danube countries
# mostImportantCrops_list = None
# mostImportantCrops_list = None # Begecka Jama
# mostImportantCrops_list =  [ "wheat", "maize", "apple" ] # Krka, option 1
# mostImportantCrops_list =  ["barley","maize","triticale","apple","sourcherry","grape","pea","plum","potato","rapeseed","soybean","wheat"] # # Krka, option 2
mostImportantCrops_list =  ["barley","cerealnes","mixedgrain","greencorn","oats","oilseednes","grape"] # Morava

#["apple",
#"barley",
#"bean",
#"greenbean",
#"cerealnes"],
#"sourcherry",
#"chilleetc",
#"mixedgrain",
#"grape",
#"lupin",
#"maize",
#"greencorn",
#"oats",
#"oilseednes",
#"pea",
#"plum",
#"poppy",
#"potato",
#"pulsenes",
#"rapeseed",
#"rasberry",
#"rye",
#"soybean",
#"sugarbeet",
#"sunflower",
#"triticale",
#"walnut",
#"wheat"]

# if mostImportantCrops_list is not None: 

FAOstats_year_producerPrices = 2017
FAOstats_year_landUse = 2017
FAOstats_year_govExp = 2017
FAOstats_year_machin = 2008
FAOstats_year_stocks = 2017
FAOstats_year_production = 2017

mostImportantLivestock_list = None
# mostImportantLivestock_list = [ "Sheep","Beehives"]   # Begecka Jama
# mostImportantLivestock_list = ["Cattle","Chickens","Horses","Pigs"] # Krka1
# mostImportantLivestock_list = ["Beehives"] # Krka2

#mostImportantLivestock_list = ["Asses",
#"Beehives",
#"Buffaloes",
#"Camels",
#"Cattle",
#"Chickens",
#"Ducks",
#"Geese and guinea fowls",
#"Goats",
#"Horses",
#"Mules",
#"Pigs",
#"Rabbits and hares",
#"Sheep",
#"Turkeys"]

## Begecka Jama --------------------------------------
#Heads_sheep_per_yr= 25 # otherwise None
#Heads_beehives_per_yr= None
#heads_livestock_pilotArea_per_yr = [mostImportantLivestock_list, [Heads_sheep_per_yr,Heads_beehives_per_yr] ]
## Begecka Jama --------------------------------------

heads_livestock_pilotArea_per_yr = None
# heads_livestock_pilotArea_per_yr = [mostImportantLivestock_list,numpy.repeat(None,len(mostImportantLivestock_list,))] # Krka 1

LivestockProducts_list = None
## Begecka Jama --------------------------------------
#LivestockProducts_list =  ["Milk, whole fresh sheep","Honey, natural"] # "Meat, sheep", 
## Begecka Jama --------------------------------------
# LivestockProducts_list =  ["Meat, cattle","Milk, whole fresh cow","Meat, pig","Meat, chicken","Eggs, hen, in shell","Meat, horse"] # Krka 1
# LivestockProducts_list =  ["Honey, natural"] # Krka 2

# for only cattle: ["Meat, cattle", "Milk, whole fresh cow"]

#LivestockProducts_list = ["Beeswax",
#"Eggs, hen, in shell",
#"Eggs, other bird, in shell",
#"Honey, natural",
#"Meat, ass",
#"Meat, bird nes",
#"Meat, buffalo",
#"Meat, cattle",
#"Meat, chicken",
#"Meat, duck",
#"Meat, game",
#"Meat, goat",
#"Meat, goose and guinea fowl",
#"Meat, horse",
#"Meat, pig",
#"Meat, rabbit",
#"Meat, sheep",
#"Meat, turkey",
#"Milk, whole fresh buffalo",
#"Milk, whole fresh camel",
#"Milk, whole fresh cow",
#"Milk, whole fresh goat",
#"Milk, whole fresh sheep",
#"Silk-worm cocoons, reelable"]

mostImportantFish_list = None
# mostImportantFish_list = ["Salmons, trouts, smelts","Pike-perch - Stizostedion lucioperca","Cyprinids nei - Cyprinidae"] # Krka
#mostImportantFish_list =  ['Adriatic sturgeon - Acipenser naccarii']

# -------------------------------------------------------------------------------------------------------------
# -- IMPORT DATA  --
# -------------------------------------------------------------------------------------------------------------

pilotArea_name = "Morava" # "Krka" #"BegeckaJama"
scenarioID = "CS" # "RS3" #"CS"


# Import FAO tables
if mostImportantCrops_list is not None:
    table_FAOSTAT_names, table_FAOSTAT_prices, table_FAOSTAT_govExp, table_FAOSTAT_machinery, table_FAOSTAT_landuse = ImportFAO_tables_C_CultivatedGoods_Agriculture(iface, tool_path)
else:
    # import FAOSTAT table of land uses areas
    table_FAOSTAT_landuse_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_LandUse_specific.csv"
    table_FAOSTAT_landuse_name = "FAOSTAT_data_LandUse_specific"
    table_FAOSTAT_landuse = iface.addVectorLayer(table_FAOSTAT_landuse_path, table_FAOSTAT_landuse_name, "ogr")


table_FAOSTAT_stocks, table_FAOSTAT_production, table_FAOSTAT_production_yield,table_FAOSTAT_prices = ImportFAO_tables_C_CultivatedGoods_Livestock(iface, tool_path)

# import EUROSTAT tables
if mostImportantFish_list is not None:
    table_fishProduction, table_fishEur, table_EUROSTAT_fishNames = ImportEUROSTAT_tables_C_CultivatedGoods_Aquaculture(iface, tool_path)

#Import spatialdata
ESmapStake_layer = Import_ESMapStakeholders_shp(iface,tool_path,pilotArea_name,scenarioID,cultivated_good_type)

if mostImportantCrops_list is not None:
    harvestedArea_raster_list = Import_HarvestedAreaHectares_ras(iface, tool_path,mostImportantCrops_list)
    yieldPerHectare_raster_list = Import_YieldPerHectare_ras(iface, tool_path,mostImportantCrops_list)

Danube_countries = Import_Danube_countries_shp(iface,tool_path)
AreaAnalysis_layer = Import_AnalysisArea_shp(iface,tool_path,pilotArea_name)




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
# -- MAIN CODE - C: CULTIVATED GOODS - AGRICULTURE
# -------------------------------------------------------------------------------------------------------------

if mostImportantCrops_list is not None:
    
    
    # CREATE COPY OF THE ES map from stakeholders
    Agriculture_products_layer = createCopy_Shapefile(ESmapStake_layer, "C_cultivated_output04_agriculture", "FID_1")
    
    # extract data from the EarthStat raster files
    for index in range(len(harvestedArea_raster_list)):
       print("Harvested area rasters: "+ str(index+1) + " of " + str(len(harvestedArea_raster_list)))
       # get harvested area in ha (sum)
       harvestedArea_raster = harvestedArea_raster_list[index]
       cropType = mostImportantCrops_list[index]
       Agriculture_products_layer.startEditing()
       zoneStat = QgsZonalStatistics (Agriculture_products_layer, harvestedArea_raster, str('harvestedArea_ha_'+cropType+'_'), 1, QgsZonalStatistics.Sum)
       zoneStat.calculateStatistics(None)
       # get yield per ha (mean)
       yieldPerHectare_raster = yieldPerHectare_raster_list[index]
       cropType = mostImportantCrops_list[index]
       Agriculture_products_layer.startEditing()
       zoneStat = QgsZonalStatistics (Agriculture_products_layer, yieldPerHectare_raster, str('Yield_tonperha_'+cropType+'_'), 1, QgsZonalStatistics.Mean)
       zoneStat.calculateStatistics(None)
       Agriculture_products_layer.commitChanges()
    
    # calculate the total yield
    for cropType in mostImportantCrops_list:
       myField = QgsField( str('TotalYield_'+cropType+'_ton_per_year'), QVariant.Double )
       Agriculture_products_layer.dataProvider().addAttributes([myField])
       Agriculture_products_layer.updateFields()
       idx_har = Agriculture_products_layer.fields().indexFromName(str('harvestedArea_ha_'+cropType+'_sum'))
       idx_yie = Agriculture_products_layer.fields().indexFromName(str('Yield_tonperha_'+cropType+'_mean'))
       idx_tyi = Agriculture_products_layer.fields().indexFromName(str('TotalYield_'+cropType+'_ton_per_year'))
       idx_ESS = Agriculture_products_layer.fields().indexFromName('ESS')
       Agriculture_products_layer.startEditing()
       for f in Agriculture_products_layer.getFeatures():
           if f[idx_ESS] == 'agricultural product' : 
               # area
               f[idx_tyi] = float(f[idx_har])*float(f[idx_yie])
               # update the feature
               Agriculture_products_layer.updateFeature( f )
           else:
               f[idx_har] = float('nan')
               f[idx_yie] = float('nan')
               f[idx_tyi] = float('nan')
               Agriculture_products_layer.updateFeature( f )
       # commit
       Agriculture_products_layer.commitChanges()
    
    
    # extract "agricultural land" area [ha] of the country
    agriculturalLand_country_ha = readTable_FAOSTAT_landuse(table_FAOSTAT_landuse,country,FAOstats_year_landUse,"Agricultural land")
    
    GrossPrices_agriculture_sum_USD_per_year = 0.0
    Costs_agriculture_sum_USD_per_year = 0.0
    # extract and then calculate market price of yield per year
    for cropType in mostImportantCrops_list:
       
       # translate EarthStat to FAO
       cropType_FAO = readTable_FAOSTAT_names(table_FAOSTAT_names, cropType)

       # get price of yield in the country
       ProducerPrices_USD_per_ton = readTable_FAOSTAT_prices(table_FAOSTAT_prices,country,FAOstats_year_producerPrices,cropType_FAO)
       
       print("Producer prices of "+cropType_FAO+ "[USD/ton]: "+str(ProducerPrices_USD_per_ton))

       # get costs from agriculture
       GovernmentExpenditure_USD2010_year = readTable_FAOSTAT_govExpenditure(table_FAOSTAT_govExp,country,FAOstats_year_govExp)

       # get costs from machinery 
       AgricultureMachinery_Import_USD_year, HarvesterMachinery_Import_USD_year, DairyMachinery_Import_USD_year, SoilMachinery_Import_USD_year = readTable_FAOSTAT_machineryImportValue(table_FAOSTAT_machinery,country,FAOstats_year_machin)

       # calculate market price of yield per year
       myField = QgsField( str('ProducerPrice_'+cropType+'_USD_per_year'), QVariant.Double )
       Agriculture_products_layer.dataProvider().addAttributes([myField])
       myField2 = QgsField( str('AgricultureCosts_'+cropType+'_USD_per_year'), QVariant.Double )
       Agriculture_products_layer.dataProvider().addAttributes([myField2])
       myField3 = QgsField( str('NetValue_'+cropType+'_USD_per_year'), QVariant.Double )
       Agriculture_products_layer.dataProvider().addAttributes([myField3])
       Agriculture_products_layer.updateFields()
       # get indexes
       idx_tyi = Agriculture_products_layer.fields().indexFromName(str('TotalYield_'+cropType+'_ton_per_year'))
       idx_ESS = Agriculture_products_layer.fields().indexFromName('ESS')
       idx_area = Agriculture_products_layer.fields().indexFromName('Area_ha')
       idx_pp = Agriculture_products_layer.fields().indexFromName(str('ProducerPrice_'+cropType+'_USD_per_year'))
       idx_cost = Agriculture_products_layer.fields().indexFromName(str('AgricultureCosts_'+cropType+'_USD_per_year'))
       idx_net = Agriculture_products_layer.fields().indexFromName(str('NetValue_'+cropType+'_USD_per_year'))
       # start calculating
       Agriculture_products_layer.startEditing()
       for f in Agriculture_products_layer.getFeatures():
           if f[idx_ESS] == 'agricultural product' : 
               # gross price
               gross_price_tmp = float(f[idx_tyi])*ProducerPrices_USD_per_ton
               f[idx_pp] = float(gross_price_tmp)
               Agriculture_products_layer.updateFeature( f )
               # costs 
               costs_tmp = numpy.nansum([GovernmentExpenditure_USD2010_year,AgricultureMachinery_Import_USD_year , HarvesterMachinery_Import_USD_year ,SoilMachinery_Import_USD_year])* float(f[idx_area]) / agriculturalLand_country_ha
               f[idx_cost] = float(costs_tmp)
               Agriculture_products_layer.updateFeature( f )
               # net price
               net_tmp = f[idx_pp]-f[idx_cost]
               f[idx_net] = net_tmp
               # update the feature
               Agriculture_products_layer.updateFeature( f )
               # check manually
               # print("costs agriculture: "+ str(f[idx_cost] ) + "; net (prices - costs): "+ str(f[idx_net] ))
               GrossPrices_agriculture_sum_USD_per_year = numpy.nansum ([GrossPrices_agriculture_sum_USD_per_year ,gross_price_tmp])
               Costs_agriculture_sum_USD_per_year = Costs_agriculture_sum_USD_per_year + costs_tmp
           else:
               f[idx_pp] = float('nan')
               f[idx_cost] = float('nan')
               f[idx_net] = float('nan')
               Agriculture_products_layer.updateFeature( f )
       # commit
       Agriculture_products_layer.commitChanges()
       
    # FINISHED AGRICULTURE
    
    # SAVE CALCULATED AGRICULTURE RESULTS
    QgsVectorFileWriter.writeAsVectorFormat(Agriculture_products_layer, str(tool_path + "/OutputData_ES/C_cultivated_goods/C_cultivated_output04_agriculture_"+scenarioID+".shp"),"UTF-8", Agriculture_products_layer.crs(), "ESRI Shapefile")
    
    # write txt file with result 
    output_txt_file_path = tool_path + "OutputData_ES/C_cultivated_goods/GrossPrices_agriculture_per_yr_"+ scenarioID +".txt"
    file_to_write = open(output_txt_file_path, 'w')
    file_to_write.write(str("GrossPrices_agriculture_sum_USD_per_year: " + str(GrossPrices_agriculture_sum_USD_per_year)+ " USD/year"+'\n'+
    "Costs_agriculture_sum_USD_per_year: " + str(Costs_agriculture_sum_USD_per_year)+ " USD/year"))
    # close 
    file_to_write.close()
    
    



# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - C: CULTIVATED GOODS - LIVESTOCK
# -------------------------------------------------------------------------------------------------------------

if mostImportantLivestock_list is not None:
    
    # CREATE COPY OF THE ES map from stakeholders
    Livestock_products_layer = createCopy_Shapefile(ESmapStake_layer, "C_cultivated_output05_livestock", "FID_1")
    
    
    # extract "agricultural land" area [ha] of the country
    pastureLanduse1 = "Land under temp, meadows and pastures"
    pastureLanduse2 = "Land under perm, meadows and pastures"
    
    pastureLand1_country_ha = readTable_FAOSTAT_landuse(table_FAOSTAT_landuse,country,FAOstats_year_landUse, pastureLanduse1)
    pastureLand2_country_ha = readTable_FAOSTAT_landuse(table_FAOSTAT_landuse,country,FAOstats_year_landUse, pastureLanduse2)
    pastureLand_country_ha = numpy.nansum ( [pastureLand1_country_ha,pastureLand2_country_ha] )
    
    
    # get sum area livestock 
    area_animal_product_ha = 0.0
    idx_ESS = Livestock_products_layer.fields().indexFromName('ESS')
    idx_HA = Livestock_products_layer.fields().indexFromName('Area_ha')
    for f in Livestock_products_layer.getFeatures():
        if f[idx_ESS] == 'animal product' :
            area_animal_product_ha = area_animal_product_ha + float(f[idx_HA])
    
    
    # get the number of heads
    for i in range(len(mostImportantLivestock_list)):
        livestockType = mostImportantLivestock_list[i]
        myField = QgsField( str('Number_'+livestockType+'_per_year'), QVariant.Double )
        Livestock_products_layer.dataProvider().addAttributes([myField])
        Livestock_products_layer.updateFields()
        idx_num = Livestock_products_layer.fields().indexFromName(str('Number_'+livestockType+'_per_year'))
        idx_ESS = Livestock_products_layer.fields().indexFromName('ESS')
        idx_HA = Livestock_products_layer.fields().indexFromName('Area_ha')
        Livestock_products_layer.startEditing()
        # number of heads
        for f in Livestock_products_layer.getFeatures():
            if f[idx_ESS] == 'animal product' :
                # number heads of livestock
                if heads_livestock_pilotArea_per_yr[1][i] is None:
                    livestock_heads  = readTable_FAOSTAT_stocks(table_FAOSTAT_stocks,country,FAOstats_year_stocks,livestockType)
                    number_tmp = livestock_heads*float(f[idx_HA])/pastureLand_country_ha
                    f[idx_num] = float(number_tmp)
                    print( "heads country: " + str(livestock_heads) + "; heads region:"+ str(f[idx_num]))
                    # update the feature
                    Livestock_products_layer.updateFeature( f )
                elif heads_livestock_pilotArea_per_yr[1][i] is not None:
                    number_tmp = heads_livestock_pilotArea_per_yr[1][i]
                    f[idx_num] = number_tmp*float(f[idx_HA])/area_animal_product_ha
                    print( "heads region:"+ str(f[idx_num]))
                    # update the feature
                    Livestock_products_layer.updateFeature( f )
            else:
                f[idx_num] = float('nan')
                Livestock_products_layer.updateFeature( f )
        # commit
        Livestock_products_layer.commitChanges()
    
    
    # get production, prices in average
    GrossPrices_livestock_sum_USD_per_year = 0.0
    for livestockProduct in LivestockProducts_list:
       myField = QgsField( str('Production_'+livestockProduct+'ton_per_year'), QVariant.Double )
       myField2 = QgsField( str('GrossPrices_'+livestockProduct+'USD_per_year'), QVariant.Double )
       Livestock_products_layer.dataProvider().addAttributes([myField,myField2])
       Livestock_products_layer.updateFields()
       idx_TON = Livestock_products_layer.fields().indexFromName(str('Production_'+livestockProduct+'ton_per_year'))
       idx_USD = Livestock_products_layer.fields().indexFromName(str('GrossPrices_'+livestockProduct+'USD_per_year'))
       idx_ESS = Livestock_products_layer.fields().indexFromName('ESS')
       idx_HA = Livestock_products_layer.fields().indexFromName('Area_ha')
       # calculate
       Livestock_products_layer.startEditing()
       for f in Livestock_products_layer.getFeatures():
           if f[idx_ESS] == 'animal product' : 
               # production of primary products from of livestock
               if heads_livestock_pilotArea_per_yr[1][i] is None:
                   production_tmp = readTable_FAOSTAT_production(table_FAOSTAT_production,country,FAOstats_year_production,livestockProduct)*float(f[idx_HA])/pastureLand_country_ha
               elif heads_livestock_pilotArea_per_yr[1][i] is not None:
                   production_tmp = readTable_FAOSTAT_production_yield(table_FAOSTAT_production_yield,country,FAOstats_year,livestockProduct)*heads_livestock_pilotArea_per_yr[1][i]*1e-06
               f[idx_TON] = float(production_tmp)
               print("production in tonnes: " + str(f[idx_TON]))
               # prices of livestock products
               price_per_ton = readTable_FAOSTAT_prices(table_FAOSTAT_prices,country,FAOstats_year_producerPrices,livestockProduct)
               prices_tmp = price_per_ton *f[idx_TON]
               f[idx_USD] = float(prices_tmp)
               print("prices: " + str(price_per_ton))
               # update the feature
               Livestock_products_layer.updateFeature( f )
               GrossPrices_livestock_sum_USD_per_year = GrossPrices_livestock_sum_USD_per_year + prices_tmp
           else:
               f[idx_TON] = float('nan')
               f[idx_USD] = float('nan')
               Livestock_products_layer.updateFeature( f )
       # commit
       Livestock_products_layer.commitChanges()
    
    # SAVE CALCULATED LIVESTOCK GOODS RESULTS
    QgsVectorFileWriter.writeAsVectorFormat(Livestock_products_layer, str(tool_path + "/OutputData_ES/C_cultivated_goods/C_cultivated_output05_livestock_"+scenarioID+".shp"),"UTF-8", Livestock_products_layer.crs(), "ESRI Shapefile")
    
    # write txt file with result 
    output_txt_file_path = tool_path + "OutputData_ES/C_cultivated_goods/GrossPrices_livestock_per_yr_"+ scenarioID +".txt"
    file_to_write = open(output_txt_file_path, 'w')
    file_to_write.write(str("GrossPrices_livestock_sum_USD_per_year: " + str(GrossPrices_livestock_sum_USD_per_year)+ " USD/year"))
    # close 
    file_to_write.close()


# -------------------------------------------------------------------------------------------------------------
# -- MAIN CODE - C: CULTIVATED GOODS - AQUACULTURE
# -------------------------------------------------------------------------------------------------------------

if mostImportantFish_list is not None:
    # CREATE COPY OF THE ES map from stakeholders
    Aquaculture_products_layer = createCopy_Shapefile(ESmapStake_layer, "C_cultivated_output06_fish", "FID_1")
    
    # get area size (ha) of the country from the Danube_countries layer
    features_layer = Danube_countries.getFeatures()
    idx_country = Danube_countries.fields().indexFromName('NAME_ENGL')
    idx_area = Danube_countries.fields().indexFromName('Area_ha')
    for feat in features_layer:
        attributes_table = feat.attributes()
        if attributes_table[idx_country] == country:
            Area_country_ha = float(attributes_table[idx_area])
    
    # get area of the pilot area
    idx_ha = AreaAnalysis_layer.fields().indexFromName("Area_ha")
    features_table = AreaAnalysis_layer.getFeatures()
    for feat in features_table:
        attributes_table = feat.attributes()
        feat_value = feat
        Area_pilotArea_ha = float(feat_value[idx_ha])
    
    
    # get the area information on where aquaculture is done in the pilot
    myField = QgsField( 'AreaFish_perc', QVariant.Double )
    Aquaculture_products_layer.dataProvider().addAttributes([myField])
    Aquaculture_products_layer.updateFields()
    idx_ESS = Aquaculture_products_layer.fields().indexFromName('ESS')
    idx_HA = Aquaculture_products_layer.fields().indexFromName('Area_ha')
    idx_PERC = Aquaculture_products_layer.fields().indexFromName('AreaFish_perc')
    # extract values of areas
    Area_fishAquaculture_pilot_ha = 0.0
    for f in Aquaculture_products_layer.getFeatures():
        if f[idx_ESS] == 'fish' : 
            Area_fishAquaculture_pilot_ha += float(f[idx_HA])
    # start calculating
    Aquaculture_products_layer.startEditing()
    for f in Aquaculture_products_layer.getFeatures():
        if f[idx_ESS] == 'fish' : 
            percentage_fish_area = float(f[idx_HA])/Area_fishAquaculture_pilot_ha
            f[idx_PERC] = float(percentage_fish_area)
            Aquaculture_products_layer.updateFeature( f )
    Aquaculture_products_layer.commitChanges()
    
    
    # save results in the shapefile
    GrossPrices_fish_sum_USD_per_year = 0.0
    for fishType in mostImportantFish_list:
        # 1) GET THE NATIONAL VALUES
        # get the fish code
        fishCode = readTable_EUROSTAT_fishNames(table_EUROSTAT_fishNames, fishType)
        #get production
        fishProduction_country_ton_year = readTable_EUROSTAT_fish(table_fishProduction, fishCode, countryCode)
        #get eur value
        fishValue_country_eur_year = readTable_EUROSTAT_fish(table_fishEur, fishCode, countryCode)
        
        # 2) GET THE PILOT AREA VALUES
        fishProduction_pilotArea_ton_year = fishProduction_country_ton_year*(Area_pilotArea_ha/Area_country_ha)
        fishValue_pilotArea_ton_year = fishValue_country_eur_year*(Area_pilotArea_ha/Area_country_ha)
        
        # 3) SCALE THE RESULTS TO THE AREA
        myField = QgsField( str('Production_'+fishType+'_ton_per_year'), QVariant.Double )
        myField2 = QgsField( str('GrossPrices_'+fishType+'_EUR_per_year'), QVariant.Double )
        Aquaculture_products_layer.dataProvider().addAttributes([myField,myField2])
        Aquaculture_products_layer.updateFields()
        idx_TON = Aquaculture_products_layer.fields().indexFromName(str('Production_'+fishType+'_ton_per_year'))
        idx_EUR = Aquaculture_products_layer.fields().indexFromName(str('GrossPrices_'+fishType+'_EUR_per_year'))
        idx_ESS = Aquaculture_products_layer.fields().indexFromName('ESS')
        idx_PERC = Aquaculture_products_layer.fields().indexFromName('AreaFish_perc')
        # calculate
        Aquaculture_products_layer.startEditing()
        for f in Aquaculture_products_layer.getFeatures():
            if f[idx_ESS] == 'fish' : 
                # production of primary products from of livestock
                production_tmp = fishProduction_pilotArea_ton_year*float(f[idx_PERC])
                f[idx_TON] = float(production_tmp)
                print("production in tonnes: " + str(f[idx_TON]))
                # prices of livestock products
                prices_tmp = fishValue_pilotArea_ton_year*float(f[idx_PERC])
                f[idx_EUR] = float(prices_tmp)
                print("prices: " + str(prices_tmp))
                # update the feature
                Aquaculture_products_layer.updateFeature( f )
                GrossPrices_fish_sum_USD_per_year = GrossPrices_fish_sum_USD_per_year + prices_tmp
            else:
                f[idx_TON] = float('nan')
                f[idx_EUR] = float('nan')
                Aquaculture_products_layer.updateFeature( f )
        # commit
        Aquaculture_products_layer.commitChanges()
    
    # SAVE CALCULATED AQUACULTURE GOODS RESULTS
    QgsVectorFileWriter.writeAsVectorFormat(Aquaculture_products_layer, str(tool_path + "/OutputData_ES/C_cultivated_goods/C_cultivated_output06_fish_"+ scenarioID +".shp"),"UTF-8", Aquaculture_products_layer.crs(), "ESRI Shapefile")
    
    # write txt file with result 
    output_txt_file_path = tool_path + "OutputData_ES/C_cultivated_goods/GrossPrices_fish_per_yr_"+ scenarioID +".txt"
    file_to_write = open(output_txt_file_path, 'w')
    file_to_write.write(str("GrossPrices_fish_sum_USD_per_year: " + str(GrossPrices_fish_sum_USD_per_year)+ " USD/year"))
    # close 
    file_to_write.close()

