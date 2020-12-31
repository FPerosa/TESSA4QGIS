# Functions_FloodRisk2_plugin
# Functions of the already existing plugin FloodRisk2
# by FloodRisk community

## ============================================================================================
#import sys
#import os
#import sqlite3
#import numpy 
#
#from PyQt5 import QtCore, QtGui, QtWidgets, uic
#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import *
#from PyQt5.QtCore import *
#
#from qgis.core import *
#from qgis.gui import *
#import qgis.analysis
#
#from qgis.core import (
#     QgsApplication, 
#     QgsProcessingFeedback, 
#     QgsVectorLayer
#)

# from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox, QPushButton, QDialog
# from PyQt5.QtGui import QIcon, QImage
# from PyQt5.QtCore import pyqtSlot
# ============================================================================================

# TEST THE UPLOADING FUNCTIONS OF THE PLUGIN
# -- FUNCTIONS --	
# Functions before: 1: CampiTabella -------------------------------------------------------------------------------------------------------------
def CampiTabella(sql):
    nn=str.find(sql,'(')+1
    pp1=sql[nn:-1]
    campi=str.split(pp1,',')
    numcampi=len(campi)
    NomeCampo=[]
    TipoCampo=[]
	# for through fields
    for campo in campi:
        testo=campo
		# check previous fields
        if campo[-1]== ' ':
            testo=campo[:-1]
		# find the id of the field without name
        nn=str.find(testo,' ')
		# if all fields have a name
        if nn==0:
            testo=campo[1:]
            nn=str.find(testo,' ')
		# save the name of the field
        NomeCampo.append(testo[:nn])
        TipoCampo.append(testo[nn+1:])
	# return the result
    return NomeCampo,TipoCampo
# Functions before: 2: GeomColumn
def GeomColumn(TipoCampo,NomeCampo):
    tipi = ['POINT', 'LINESTRING', 'POLYGON', 'MULTILINESTRING', 'MULTIPOLYGON']
    nn=len(TipoCampo)
    ColGeom='Null'
    tipoGeom='Null'
	# if the length is bigger than 0
    if nn>0:
        for k in range(nn):
            i=nn-k-1
            tipo=TipoCampo[i]
			# 
            if tipo in tipi:
                tipoGeom=tipo
                ColGeom=NomeCampo[i]
                break
	# return the result
    return tipo, ColGeom
# Functions before: 3: CampiSHP -------------------------------------------------------------------------------------------------------------
def CampiSHP(layer,feat):
    feat_defn = layer.GetLayerDefn()
    NumFields=feat_defn.GetFieldCount()
    NameField=[]
    TypeField=[]
    NumFields=feat.GetFieldCount()
	# for for fields
    for i in range(NumFields):
        field_defn = feat_defn.GetFieldDefn(i)
        NameField.append(field_defn.GetName())
		# check type
        if field_defn.GetType() == ogr.OFTInteger:
            TypeField.append('INTEGER')
        elif field_defn.GetType() == ogr.OFTReal:
            TypeField.append('REAL')
        elif field_defn.GetType() == ogr.OFTString:
            width=field_defn.GetWidth()
            stringa='VARCHAR(%d)' % (width)
            TypeField.append(stringa)
        else:
            TypeField.append('VARCHAR(20)')
	# return
    return NameField,TypeField
    
# Functions before: 4: NewGeom -------------------------------------------------------------------------------------------------------------
def NewGeom(raw_geom,typeTab,NumEPSG):
    pp=str.split(raw_geom,' ')
    typeCurr=pp[0]

    # forced the geodatabase to import MULTIPOLYGON and MULTILINESTRING
    if typeCurr!=typeTab:
        if typeCurr=='POLYGON' and typeTab=='MULTIPOLYGON':
            pp1=raw_geom.replace('((','(((')
            new_geom='%s%s)' % ('MULTI',pp1)
        elif typeCurr=='LINESTRING' and typeTab=='MULTILINESTRING':
            pp1=raw_geom.replace('(','((')
            new_geom='%s%s)' % ('MULTI',pp1)
        else:
            new_geom=raw_geom
    else:
        new_geom=raw_geom

    geom = "GeomFromText('%s', %s)" %(new_geom,NumEPSG)
    return geom
# Functions before: 5: UploadLayerInSQL -------------------------------------------------------------------------------------------------------------
def UploadLayerInSQL(layer,TargetEPSG,GeomAreawkt,NomeTabella,NameField,TypeField,dic_fiels,CampiInsert,typeTab,ListaSql,instance):
    # load a layer in memory and write a SQL file
    Err='ok'
    dic = {1:'POINT', 2:'LINESTRING', 3:'POLYGON', 5:'MULTILINESTRING', 6:'MULTIPOLYGON'}
    feat_defn = layer.GetLayerDefn()
    NumFieldsShp=feat_defn.GetFieldCount()
    NumFields=len(CampiInsert)
    NomeTabellaShp=layer.GetName()
    print ('Uploading to database shapefile:', NomeTabellaShp)
    carmin=0
    spatialRef = layer.GetSpatialRef()
    # looking for the code of the reference system
    spatialRef.AutoIdentifyEPSG()
    NumEPSG= spatialRef.GetAuthorityCode(None)
    if NumEPSG==None:
        prj_txt=spatialRef.ExportToPrettyWkt()
        NumEPSG=NumEPSGFromOpenGeo(prj_txt)
    else:
        try:
            NumEPSG=int(NumEPSG)
        except:
            pass
    numFeatures = layer.GetFeatureCount()
    ini = 10.0
    fin = 40.0
    if numFeatures>0:
        dx = (fin - ini) / float(numFeatures)
        if TargetEPSG!=NumEPSG:
            targetSR = osr.SpatialReference()
            targetSR.ImportFromEPSG(TargetEPSG)
            sourceSR = osr.SpatialReference()
            sourceSR.ImportFromEPSG(NumEPSG)
            coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
            trasformare=bool('True')
        else:
            trasformare=bool()
        if len(GeomAreawkt)>0:
            intersezione=bool('True')
            GeomStudy=ogr.CreateGeometryFromWkt(GeomAreawkt)
        else:
            intersezione=bool()
        # Reading data into memory
        #===========================================
        feat = layer.GetNextFeature()
        kk = 0
        # err_check = 0
        while feat:
            geom_class = feat.GetGeometryRef()
            geom_type = geom_class.GetGeometryType()
            GeomType = dic[geom_type]
            # writing sql text
            sql = "INSERT INTO " + NomeTabella +" ("
            # add instance field
            sql+='instance,'
            # insert the field names
            for i in range(NumFieldsShp):
                field_defn = feat_defn.GetFieldDefn(i)
                name=field_defn.GetName()
                try:
                    ind=CampiInsert.index(field_defn.GetName())
                    nome=dic_fiels[CampiInsert[ind]]
                    sql +=nome+','
                except:
                    pass
            if typeTab!='Null':
                sql +="geom) "
                try:
                    geometry = feat.GetGeometryRef()
                    if trasformare:
                        geometry.Transform(coordTrans)
                    Area=geometry.GetArea()
                    if intersezione:
                        # changed by Francesca --- from here ---
                        try:
                            inters=geometry.Intersection(GeomStudy)
                            raw_geom= inters.ExportToWkt()
                        except:
                            pass
                        # changed by Francesca --- until here ---
                    else:
                        raw_geom= geometry.ExportToWkt()
                    geom=NewGeom(raw_geom,typeTab,TargetEPSG)
                    # err_check = err_check +1
                except:
                    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                    errMsg= "Table %s  Error! ->%s" % (NomeTabella,exceptionValue)
                    NotErr=bool()
                    print('NotErr:',NotErr)
                    return NotErr, errMsg
            else:
                sql=sql[:-1]+") "
            sql += "VALUES ("
            # add instance value
            sql+='%d,' % instance
            # insert the field values
            for i in range(NumFieldsShp):
                field_defn = feat_defn.GetFieldDefn(i)
                name_field_shp=field_defn.GetName()
                try:
                    NomeCampoCur=dic_fiels[name_field_shp]
                    if NomeCampoCur=='Shape_Area':
                        valore= "%.3f" % (Area)
                        sql += valore
                    else:
                        kfield=NameField.index(NomeCampoCur)
                        tipo=TypeField[kfield]
                        if field_defn.GetType() == ogr.OFTInteger:
                            valore= "%d" % feat.GetFieldAsInteger(i)
                            sql += valore
                        elif field_defn.GetType() == ogr.OFTReal:
                            valore= "%.3f" % feat.GetFieldAsDouble(i)
                            sql += valore
                        elif field_defn.GetType() == ogr.OFTString:
                            stringa=feat.GetFieldAsString(i)
                            stringa=str(stringa).replace("'"," ")
                            valore= "%s" % stringa
                            if len(stringa)<1:
                                stringa='Null'
                            sql += "'%s" % stringa+"'"
                        else:
                            stringa=feat.GetFieldAsString(i)
                            stringa=str(stringa).replace("'"," ")
                            valore= "%s" % stringa
                            if len(stringa)<1:
                                stringa='Null'
                            sql += "'%s" % stringa+"'"
                    sql +=','
                except:
                    pass
            if typeTab!='Null':
                # enters the value of geometry
                sql += " %s)" % (geom)
                sql +=';'
            else:
                sql += ");"
            ListaSql.append(sql)
            feat.Destroy()
            kk = kk+1
            numCur = int(ini + dx * kk)
            #bar.setValue(numCur)
            feat = layer.GetNextFeature()
    #bar.setValue(40)
    return Err
    
    
# Functions before: 6: clip_raster_by_vector -------------------------------------------------------------------------------------------------------------
# clips raster with a mask of a shapefile
def clip_raster_by_vector(input_raster, input_vector, output_raster, overwrite=False):
    if overwrite:
        if os.path.isfile(output_raster):
            os.remove(output_raster)

    if not os.path.isfile(input_raster):
        print ("File doesn't exists", input_raster)
        return None
    else:
        params = {'INPUT': input_raster,
                  'MASK': input_vector,
                  'NODATA': 255.0,
                  'ALPHA_BAND': False,
                  'CROP_TO_CUTLINE': True,
                  'KEEP_RESOLUTION': True,
                  'OPTIONS': 'COMPRESS=LZW',
                  'DATA_TYPE': 0,  # Byte
                  'OUTPUT': output_raster,
                  }

        feedback = qgis.core.QgsProcessingFeedback()
        alg_name = 'gdal:cliprasterbymasklayer'
        #print(processing.algorithmHelp(alg_name))
        result = processing.run(alg_name, params, feedback=feedback)
        return result
