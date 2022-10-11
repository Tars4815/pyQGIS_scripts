#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   merge_csv_with_id_1n.py
@Time    :   2022/10/11 14:27:50
@Author  :   Federica Gaspari 
@Version :   1.0
@Contact :   federica.gaspari@polimi.it, federica.gaspari@live.it
@License :   (C)Copyright 2022, Federica Gaspari
@Desc    :   PyQGIS script for processing csv tables in 1:n relationship and merge them in existing layers.
'''


#Import pandas for processing csv data
import pandas as pd
#Getting maximum value of ids of parent and child layers and store them in variables
#id field of parent layer in QGIS
fieldname='id_parent'
#parent layer in QGIS
layer=QgsProject.instance().mapLayersByName(
    "parent_layer")[0]
idx=layer.fields().indexFromName(fieldname)
max = layer.maximumValue(idx)
#id field of child layer in QGIS
fieldname='id_child'
#child layer in QGIS
layer2=QgsProject.instance().mapLayersByName(
    "child_layer")[0]
idxsegn=layer2.fields().indexFromName(fieldname)
maxsegn = layer2.maximumValue(idxsegn)
#Get parent csv layer
csvlayer = QgsProject.instance().mapLayersByName(
    "csvparent")[0]
#----
#Trigger loop for renumbering parent elements and corresponding parent id in child elements
#Create new fields for storing correct id
myField = QgsField('id', QVariant.Int)
csvlayer.dataProvider().addAttributes([myField])
csvlayer.updateFields()
idx = csvlayer.fields().indexOf('id')
#Opening with pandas child csv
data = pd.read_csv(r"csvchild.csv", sep=';')
#Rename original ref parent id column to avoid confusion with format
data.rename(columns={"old_parentid": "gs"}, inplace=True)
#Add new column for correct ref parent id
data["parent_id"]=""
k=1
with edit(csvlayer):
    for feature in csvlayer.getFeatures():
        feature['id']= k + max
        k=k+1
        csvlayer.updateFeature(feature)
        #Store old valye of parent id in parent layer
        value = feature['old_id']
        #Find correspondance in child csv layer and updated it in the new parent id column
        data.loc[data['gs']== value,'parent_id'] = feature['id']
#Remove useless column of old id
data = data.drop(columns=['gs'])
#Recalculate child id in child csv starting from maximum id in child layer in QGIS
data['id_segnale_fisico'] = range(int(maxsegn), int(maxsegn)+len(data))
#Write child csv output
data.to_csv('newchildcsv.csv', mode='w')
#Load data from child csv
uri = "file:///C:/Users/Admin/Desktop/newchildcsv.csv?delimiter=%s" % (",") #Change path and delimiter according to personal needs
lyr = QgsVectorLayer(uri, 'newchildcsv','delimitedtext')
QgsProject.instance().addMapLayer(lyr)
#Copy and paste new data in the destination layer
csvlayer.selectAll()
lyr.selectAll()
#Copying all features to clipboard
iface.copySelectionToClipboard(csvlayer)
#Get target layer knowing its layer name
targetparent = QgsProject.instance().mapLayersByName("parent_layer")[0]
#Enable editing mode for the target layer
targetparent.startEditing()
#Paste the csv copied features in the target layer
iface.pasteFromClipboard(targetparent)
#Stop editing mode in the target layer and save edits
targetparent.commitChanges()
#Copying all child features to clipboard
iface.copySelectionToClipboard(lyr)
#Get target layer knowing its layer name
targetchild = QgsProject.instance().mapLayersByName("child_layer")[0]
#Enable editing mode for the target layer
targetchild.startEditing()
#Paste the csv copied features in the target layer
iface.pasteFromClipboard(targetchild)
#Stop editing mode in the target layer and save edits
targetchild.commitChanges()