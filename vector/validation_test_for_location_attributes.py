#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   csv_validation_test.py
@Time    :   2022/07/05 15:13:27
@Author  :   Federica Gaspari 
@Version :   1.0
@Contact :   federica.gaspari@polimi.it, federica.gaspari@live.it
@License :   (C)Copyright 2022, Federica Gaspari
@Desc    :   pyQGIS script for validating position of points on csv based on 3 criteria (inclusion in buffers, correspondance of field values)
'''

import os
import processing 

#Steps:
#-----------------
#0. Clean the current map view and set up the environment for the csv validation
loaded_layers = QgsProject.instance().mapLayers().values()
for layer in loaded_layers:
        QgsProject.instance().removeMapLayer(layer)
#-----------------
#1. Load OSM basemap
urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG25832'
rlayer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms') 
if rlayer.isValid():
    QgsProject.instance().addMapLayer(rlayer)
else:
    print('invalid layer')
#-----------------
#2. Load points from CSV
csv_path = "" #Insert here desired csv file path
uri = "file:///" + str(csv_path) + "?encoding=%s&delimiter=%s&xField=%s&yField=%s&crs=%s" % ("UTF-8",",", "X", "Y","epsg:25832") #Change parameters depending on file definition
csv_layer=QgsVectorLayer(uri,"prova","delimitedtext")
#Check if layer is valid
if not csv_layer.isValid():
    print ("Layer not loaded")
#Add CSV data    
QgsProject.instance().addMapLayer(csv_layer)
pts_fields = csv_layer.fields()
pts_feats = csv_layer.getFeatures()
#-----------------
#3. Load road layer
uri0 ="" #Insert here desired shp file of lines
route=iface.addVectorLayer(uri0,"routes","ogr")
line_fields = route.fields()
line_feats = route.getFeatures()
#-----------------
#4. Load administrative boundaries (polygon layer)
uri1 = "" #Insert here desired shp file of polygons
admin=iface.addVectorLayer(uri1,"comuni","ogr")
#Not needed for cippi layers
#-----------------
#5. Define buffer layer
#Creating buffer at 50 meters
outFile = '' #Insert here desired output shp file path for buffer
bufDist = 50  # buffer width in map units
new_crs = QgsCoordinateReferenceSystem('EPSG:25832')
writer = QgsVectorFileWriter(outFile, 'UTF-8', line_fields, \
QgsWkbTypes.Polygon, new_crs, 'ESRI Shapefile')
for feat in line_feats:
    geom = feat.geometry()
    buffer = geom.buffer(bufDist, 5)
    feat.setGeometry(buffer)
    writer.addFeature(feat)
iface.addVectorLayer(outFile, 'buffer', 'ogr')
del(writer)
#------------------
#5. Selecting features within buffer
lyrPts = QgsProject.instance().mapLayersByName('prova')[0] # Point layer
lyrPoly = QgsProject.instance().mapLayersByName('buffer')[0] # Polygon layer
idx = lyrPts.fields().indexOf('cod_strada')
values = lyrPts.uniqueValues(idx)
validated = []
for value in values:
    lyrPts.selectByExpression("\"cod_strada\"= '{}'".format(str(value)))
    lyrPoly.selectByExpression("\"cod_strada\"= '{}'".format(str(value)))
    selectedPts = lyrPts.materialize(QgsFeatureRequest().setFilterFids(lyrPts.selectedFeatureIds()))
    selectedBuf = lyrPoly.materialize(QgsFeatureRequest().setFilterFids(lyrPoly.selectedFeatureIds()))
    lyrPts.removeSelection()
    lyrPoly.removeSelection()
    processing.run("native:selectbylocation", {'INPUT':selectedPts,'PREDICATE':[6],'INTERSECT':selectedBuf,'METHOD':0})
    QgsProject.instance().addMapLayer(selectedPts)
    for feature in selectedPts.selectedFeatures():
        validated.append(feature)
#-----------------
#6. Writing output file
outFile0 = '' #Insert here desired output shp file path for validated features
writer0 = QgsVectorFileWriter(outFile0, 'UTF-8', pts_fields, \
QgsWkbTypes.Point, new_crs, 'ESRI Shapefile')
for feat in validated:
    writer0.addFeature(feat)
iface.addVectorLayer(outFile0, 'validated', 'ogr')
layer = QgsVectorLayer(outFile0, "validated", "ogr")
del(writer0)
#-----------------
#7. Populate point field with municipality information
comuni = []
processing.run("native:selectbylocation", {'INPUT':admin,'PREDICATE':[1],'INTERSECT':layer,'METHOD':0})
selectedComuni = admin.materialize(QgsFeatureRequest().setFilterFids(admin.selectedFeatureIds()))
idx_com = admin.fields().indexOf('nome')
comuni = selectedComuni.uniqueValues(idx_com)
for comune in comuni:
    admin.selectByExpression("\"nome\"= '{}'".format(str(comune)))
    selectedCom = admin.materialize(QgsFeatureRequest().setFilterFids(admin.selectedFeatureIds()))
    processing.run("native:selectbylocation", {'INPUT':layer,'PREDICATE':[6],'INTERSECT':QgsProcessingFeatureSourceDefinition(uri1, selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),'METHOD':0})
    with edit(layer):
        for el in layer.selectedFeatures():
            el['comune']=str(comune)
            layer.updateFeature(el)
#-----------------
#8. Save validated data as a CSV file
output_name = "" #Define here file path for output csv
QgsVectorFileWriter.writeAsVectorFormat(layer,
output_name,
"utf-8",driverName = "CSV" , layerOptions = ['GEOMETRY=AS_XYZ'])
