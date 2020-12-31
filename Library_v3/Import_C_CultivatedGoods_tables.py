# Import_C_CultivatedGoods_tables
# Commands that import all tables for the Section C of TESSA
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


# IMPORT TABLES FAO -----------------------------------------------------------------------------------------------------


def ImportFAO_tables_C_CultivatedGoods_Agriculture(iface,tool_path):
    
    # import translation of names of crops
    table_FAOSTAT_names_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/legend_cropnameEarthStat_cropnameFAO.csv"
    table_FAOSTAT_names_name = "legend_cropnameEarthStat_cropnameFAO"
    table_FAOSTAT_names = iface.addVectorLayer(table_FAOSTAT_names_path, table_FAOSTAT_names_name, "ogr")
    
    # import FAOSTAT table on prices of goods, as they are direclty sold by the producer
    table_FAOSTAT_prices_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_ProducerPrices.csv"
    table_FAOSTAT_prices_name = "FAOSTAT_data_ProducerPrices"
    table_FAOSTAT_prices = iface.addVectorLayer(table_FAOSTAT_prices_path, table_FAOSTAT_prices_name, "ogr")
    
    # import data on FAOSTAT_data_GovernmentExpenditure
    table_FAOSTAT_govExp_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_GovernmentExpenditure.csv"
    table_FAOSTAT_govExp_name = "FAOSTAT_data_GovernmentExpenditure"
    table_FAOSTAT_govExp = iface.addVectorLayer(table_FAOSTAT_govExp_path, table_FAOSTAT_govExp_name, "ogr")

    #import data on FAOSTAT_data_MachineryImport
    table_FAOSTAT_machinery_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_MachineryImport.csv"
    table_FAOSTAT_machinery_name = "FAOSTAT_data_MachineryImport"
    table_FAOSTAT_machinery = iface.addVectorLayer(table_FAOSTAT_machinery_path, table_FAOSTAT_machinery_name, "ogr")
    
    # import FAOSTAT table of land uses areas
    table_FAOSTAT_landuse_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_LandUse_specific.csv"
    table_FAOSTAT_landuse_name = "FAOSTAT_data_LandUse_specific"
    table_FAOSTAT_landuse = iface.addVectorLayer(table_FAOSTAT_landuse_path, table_FAOSTAT_landuse_name, "ogr")
    
    # return all tables
    return table_FAOSTAT_names, table_FAOSTAT_prices, table_FAOSTAT_govExp, table_FAOSTAT_machinery, table_FAOSTAT_landuse



def ImportFAO_tables_C_CultivatedGoods_Livestock(iface, tool_path):
    
    # import FAOSTAT table on livestocks quantity
    table_FAOSTAT_stocks_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_Stocks.csv"
    table_FAOSTAT_stocks_name = "FAOSTAT_data_Stocks"
    table_FAOSTAT_stocks = iface.addVectorLayer(table_FAOSTAT_stocks_path, table_FAOSTAT_stocks_name, "ogr")
    
    # import FAOSTAT table on production quantity 
    table_FAOSTAT_production_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_LivestockPrimary_Production_v2.csv"
    table_FAOSTAT_production_name = "FAOSTAT_data_LivestockPrimary_Production_v2"
    table_FAOSTAT_production = iface.addVectorLayer(table_FAOSTAT_production_path, table_FAOSTAT_production_name, "ogr")
    
    # import FAOSTAT table on production quantity 
    table_FAOSTAT_production_yield_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_LivestockPrimary_Production_Yield.csv"
    table_FAOSTAT_production_yield_name = "FAOSTAT_data_LivestockPrimary_Production_Yield"
    table_FAOSTAT_production_yield = iface.addVectorLayer(table_FAOSTAT_production_yield_path, table_FAOSTAT_production_yield_name, "ogr")
    
    # import FAOSTAT table on prices of goods, as they are direclty sold by the producer
    table_FAOSTAT_prices_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/FAOSTAT_data_ProducerPrices.csv"
    table_FAOSTAT_prices_name = "FAOSTAT_data_ProducerPrices"
    table_FAOSTAT_prices = iface.addVectorLayer(table_FAOSTAT_prices_path, table_FAOSTAT_prices_name, "ogr")
    
    return table_FAOSTAT_stocks, table_FAOSTAT_production, table_FAOSTAT_production_yield, table_FAOSTAT_prices
    
    


def ImportEUROSTAT_tables_C_CultivatedGoods_Aquaculture(iface, tool_path):
    
    # import EUROSTAT fish value in tons liveweight
    table_fishProduction_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/EUROSTAT_fish_aq2a_Danube_v2_TLW.csv"
    table_fishProduction_name = "EUROSTAT_fish_aq2a_Danube_v2_TLW"
    table_fishProduction = iface.addVectorLayer(table_fishProduction_path, table_fishProduction_name, "ogr")
    
    # import EUROSTAT fish value in EUR
    table_fishEur_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/EUROSTAT_fish_aq2a_Danube_v2_EUR.csv"
    table_fishEur_name = "EUROSTAT_fish_aq2a_Danube_v2_EUR"
    table_fishEur = iface.addVectorLayer(table_fishEur_path, table_fishEur_name, "ogr")
    
    # import translation of names of fish
    table_EUROSTAT_fishNames_path = tool_path + "InputData_ES/C_CultivatedGoods_tables/EUROSTAT_fishInlandSpecies_legend.csv"
    table_EUROSTAT_fishNames_name = "EUROSTAT_fishInlandSpecies_legend"
    table_EUROSTAT_fishNames = iface.addVectorLayer(table_EUROSTAT_fishNames_path, table_EUROSTAT_fishNames_name, "ogr")
    
    

    return table_fishProduction, table_fishEur, table_EUROSTAT_fishNames