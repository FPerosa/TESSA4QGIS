# Functions_C_CultivatedGoods_readTables
# Functions to retrieve infos from the different available tables
# by Francesca Perosa
# 31.08.2020

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


# get cropType name in FAOSTAT
def readTable_FAOSTAT_names(table_FAOSTAT_names, cropType_EarthStat):
    features_table = table_FAOSTAT_names.getFeatures()
    idx_ES = table_FAOSTAT_names.fields().indexFromName('CROPNAME')
    idx_FAO = table_FAOSTAT_names.fields().indexFromName('CROPNAME_FAO')
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_ES] == cropType_EarthStat:
            cropType_FAO = attributes_table[idx_FAO]
    try:
        cropType_FAO
    except NameError:
        cropType_FAO = 'NoName'
    return cropType_FAO

# get producer prices
def readTable_FAOSTAT_prices(table_FAOSTAT_prices,country,FAOstats_year,cropType):
    features_table = table_FAOSTAT_prices.getFeatures()
    idx_country = table_FAOSTAT_prices.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_prices.fields().indexFromName('Year')
    idx_item = table_FAOSTAT_prices.fields().indexFromName('Item')
    idx_pp = table_FAOSTAT_prices.fields().indexFromName('ProducerPrices_USD_per_ton')
    prices_list_DanubeCountries = []
    for feat in features_table:
        attributes_table = feat.attributes()
        if int(attributes_table[idx_year])== FAOstats_year  and attributes_table[idx_item]== cropType and attributes_table[idx_country]== country :
            ProducerPrices_USD_per_ton = float(attributes_table[idx_pp])
    try:
        ProducerPrices_USD_per_ton
    except:
        print("Taking average prices of the Danube countries for " + str(FAOstats_year) + " and " + cropType + " in "+ country)
        features_table = table_FAOSTAT_prices.getFeatures()
        for feat in features_table:
            attributes_table = feat.attributes()
            if attributes_table[idx_item]== cropType :
                prices_list_DanubeCountries.append(float(attributes_table[idx_pp]))
        # attribute average of other countries: get mean from Danube countries
        ProducerPrices_USD_per_ton = numpy.nanmean(prices_list_DanubeCountries)
    # worst case
    try:
        ProducerPrices_USD_per_ton
    except NameError:
        ProducerPrices_USD_per_ton = float('nan')
        print("No prices provided for " + cropType)
    #return
    return ProducerPrices_USD_per_ton

# get government expenditure
# table_FAOSTAT_govExp
def readTable_FAOSTAT_govExpenditure(table_FAOSTAT_govExp,country,FAOstats_year):
    features_table = table_FAOSTAT_govExp.getFeatures()
    idx_country = table_FAOSTAT_govExp.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_govExp.fields().indexFromName('Year')
    idx_ge = table_FAOSTAT_govExp.fields().indexFromName('GovernmentExpenditure_USD2010')
    for feat in features_table:
        attributes_table = feat.attributes()
        # print("Gov. expenditure in "+attributes_table[idx_year] + " in " + attributes_table[idx_country]+ ": "+ attributes_table[idx_ge])
        if int(attributes_table[idx_year])== FAOstats_year and attributes_table[idx_country]== country :
            # print('ok!!')
            GovernmentExpenditure_USD2010_year = float(attributes_table[idx_ge])
#    try:
#        GovernmentExpenditure_USD2010_year
#    except NameError:
#        GovernmentExpenditure_USD2010_year = float('nan')
    #return
    #print("Gov. expenditure taken in " +country + ": "+ str(GovernmentExpenditure_USD2010_year))
    return GovernmentExpenditure_USD2010_year



# get machinery infos
# table_FAOSTAT_machinery
def readTable_FAOSTAT_machineryImportValue(table_FAOSTAT_machinery,country,FAOstats_year):
    features_table = table_FAOSTAT_machinery.getFeatures()
    idx_country = table_FAOSTAT_machinery.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_machinery.fields().indexFromName('Year')
    idx_item = table_FAOSTAT_machinery.fields().indexFromName('Item')
    idx_iv = table_FAOSTAT_machinery.fields().indexFromName('ImportValue_USD')
    for feat in features_table:
        attributes_table = feat.attributes()
        if int(attributes_table[idx_year])== FAOstats_year and attributes_table[idx_country]== country :
            if attributes_table[idx_item] == 'Agricultural machinery nes (trade)':
                AgricultureMachinery_Import_USD_year = float(attributes_table[idx_iv])
            elif attributes_table[idx_item] == 'Harvester and threshers (trade)':
                HarvesterMachinery_Import_USD_year = float(attributes_table[idx_iv])
            elif attributes_table[idx_item] == 'Milking, dairy machinery (trade)':
                DairyMachinery_Import_USD_year = float(attributes_table[idx_iv])
            elif attributes_table[idx_item] == 'Soil working equipment (trade)':
                SoilMachinery_Import_USD_year = float(attributes_table[idx_iv])
                
    try:
        AgricultureMachinery_Import_USD_year
    except NameError:
        AgricultureMachinery_Import_USD_year = float('nan')
    try:
        HarvesterMachinery_Import_USD_year
    except NameError:
        HarvesterMachinery_Import_USD_year = float('nan')
    try:
        DairyMachinery_Import_USD_year
    except NameError:
        DairyMachinery_Import_USD_year = float('nan')
    try:
        SoilMachinery_Import_USD_year
    except NameError:
        SoilMachinery_Import_USD_year = float('nan')
    #return
    #print("Agr. machinery costs in " + country + ": "+ str(AgricultureMachinery_Import_USD_year))
    #print("Harvester machinery costs in "+ country + ": "+ str(HarvesterMachinery_Import_USD_year))
    #print("Dairy machinery costs in " +country + ": "+ str(DairyMachinery_Import_USD_year))
    #print("Soil machinery costs in "+ country + ": "+ str(SoilMachinery_Import_USD_year))
    return AgricultureMachinery_Import_USD_year, HarvesterMachinery_Import_USD_year, DairyMachinery_Import_USD_year, SoilMachinery_Import_USD_year



# get number of stocks 
def readTable_FAOSTAT_stocks(table_FAOSTAT_stocks,country,FAOstats_year,livestockType):
    features_table = table_FAOSTAT_stocks.getFeatures()
    idx_country = table_FAOSTAT_stocks.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_stocks.fields().indexFromName('Year')
    idx_item = table_FAOSTAT_stocks.fields().indexFromName('Item')
    idx_st = table_FAOSTAT_stocks.fields().indexFromName('StocksNumber')
    stocks_list_DanubeCountries = []
    for feat in features_table:
        attributes_table = feat.attributes()
        if int(attributes_table[idx_year])== FAOstats_year  and attributes_table[idx_item]== livestockType and attributes_table[idx_country]== country :
            StocksNumber_per_year = float(attributes_table[idx_st])
    try:
        StocksNumber_per_year
    except NameError:
        # average of the other countries
        print("Taking average stocks number of the Danube countries for " + str(FAOstats_year) + " and " + livestockType + " in "+ country)
        features_table = table_FAOSTAT_stocks.getFeatures()
        for feat in features_table:
            attributes_table = feat.attributes()
            if attributes_table[idx_item]== livestockType :
                stocks_list_DanubeCountries.append(float(attributes_table[idx_st]))
        # attribute average of other countries: get mean from Danube countries
        StocksNumber_per_year = numpy.nanmean(stocks_list_DanubeCountries)
    
    # worst case
    try:
        StocksNumber_per_year
    except NameError:
        StocksNumber_per_year = float('nan')
    #return
    return StocksNumber_per_year


def readTable_FAOSTAT_production(table_FAOSTAT_production,country,FAOstats_year,livestockProduct):
    features_table = table_FAOSTAT_production.getFeatures()
    idx_country = table_FAOSTAT_production.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_production.fields().indexFromName('Year')
    idx_item = table_FAOSTAT_production.fields().indexFromName('Item')
    idx_ton = table_FAOSTAT_production.fields().indexFromName('Production_tonnes')
    production_list_DanubeCountries = []
    for feat in features_table:
        attributes_table = feat.attributes()
        if int(attributes_table[idx_year])== FAOstats_year  and attributes_table[idx_item]== livestockProduct and attributes_table[idx_country]== country :
            Production_tonnes_per_year = float(attributes_table[idx_ton])
    try:
        Production_tonnes_per_year
    except NameError:
        # average of the other countries
        print("Taking average production of the Danube countries for " + str(FAOstats_year) + " and " + livestockProduct + " in "+ country)
        features_table = table_FAOSTAT_production.getFeatures()
        for feat in features_table:
            attributes_table = feat.attributes()
            if attributes_table[idx_item]== livestockProduct :
                production_list_DanubeCountries.append(float(attributes_table[idx_ton]))
        # attribute average of other countries: get mean from Danube countries
        Production_tonnes_per_year = numpy.nanmean(production_list_DanubeCountries)
    
    # worst case
    try:
        Production_tonnes_per_year
    except NameError:
        Production_tonnes_per_year = float('nan')
    #return
    return Production_tonnes_per_year
    

def readTable_FAOSTAT_production_yield(table_FAOSTAT_production_yield,country,FAOstats_year,livestockProduct):
    features_table = table_FAOSTAT_production.getFeatures()
    idx_country = table_FAOSTAT_production.fields().indexFromName('Country')
    idx_year = table_FAOSTAT_production.fields().indexFromName('Year')
    idx_item = table_FAOSTAT_production.fields().indexFromName('Item')
    idx_gran = table_FAOSTAT_production.fields().indexFromName('Yield_grams_animal')
    for feat in features_table:
        attributes_table = feat.attributes()
        if int(attributes_table[idx_year])== FAOstats_year  and attributes_table[idx_item]== livestockProduct and attributes_table[idx_country]== country :
            Production_tonnes_per_year = float(attributes_table[idx_gran])
    try:
        Production_tonnes_per_year
    except NameError:
        Production_tonnes_per_year = float('nan')
    #return
    return Production_tonnes_per_year
    


# get fishType name in EUROSTAT
def readTable_EUROSTAT_fishNames(table_EUROSTAT_fishNames, fishType):
    features_table = table_EUROSTAT_fishNames.getFeatures()
    idx_code = table_EUROSTAT_fishNames.fields().indexFromName('Code')
    idx_name = table_EUROSTAT_fishNames.fields().indexFromName('FishSpecies')
    for feat in features_table:
        attributes_table = feat.attributes()
        if attributes_table[idx_name] == fishType:
            fishCode = attributes_table[idx_code]
    try:
        fishCode
    except NameError:
        fishCode = 'unknown'
    return fishCode


# get produced tons of fish OR  get production value in EUR
def readTable_EUROSTAT_fish(table_fish, fishCode, countryCode):
    # check the code
    if fishCode == 'unknown':
        fishCode = 'F00' # all aquatic organisms
    # start reading table
    features_table = table_fish.getFeatures()
    idx_code = table_fish.fields().indexFromName('species')
    idx_value = table_fish.fields().indexFromName('value_2017')
    idx_coco = table_fish.fields().indexFromName('geo')        
    for feat in features_table:
        attributes_table = feat.attributes()
        # correct country
        if attributes_table[idx_code] == fishCode and attributes_table[idx_coco] == countryCode:
            fishValue = float(attributes_table[idx_value])
            # the value could be 'nan'
            for i in range(9):
                if numpy.isnan(fishValue):
                    fishValue = float(attributes_table[idx_value+i+1])
#            # to include eu
#            elif attributes_table[idx_code] == fishCode and attributes_table[idx_coco] == 'EU28':
#                fishValue = float(attributes_table[idx_value])
#                # the value could be 'nan'
#                for i in range(9):
#                    if numpy.isnan(fishValue):
#                        fishValue = float(attributes_table[idx_value+i+1])
#    # otherwise take all fish species
#    elif fishCode == 'unknown':
#        allFishSum = 0
#        for feat in features_table:
#            attributes_table = feat.attributes()
#            if attributes_table[idx_coco] == countryCode:
#                oneFishValue = float(attributes_table[idx_value])
#                allFishSum = numpy.nansum([allFishSum, oneFishValue])
#        fishValue = allFishSum

    # check 
    try:
        fishValue
    except NameError:
        fishValue = float('nan')
    return fishValue




