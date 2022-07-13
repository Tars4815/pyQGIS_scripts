#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   csv_to_existing_layer.py
@Time    :   2022/07/13 16:55:43
@Author  :   Federica Gaspari 
@Version :   1.0
@Contact :   federica.gaspari@polimi.it, federica.gaspari@live.it
@License :   (C)Copyright 2022, Federica Gaspari
@Desc    :   A simple script for automatic copy-and-paste procedure between input csv and target layer with same fields.
'''

import os
import processing 

#Define path and settings for csv to be imported
file_path = "" #Copy and paste here file path
uri = "file:///"+ str(file_path) + "?encoding=%s&delimiter=%s&xField=%s&yField=%s&crs=%s" % ("UTF-8",";", "x", "y","epsg:25832") #Change delimiter, fields and crs settings depending on perosnal needs

#Make a vector layer
csv_layer=QgsVectorLayer(uri,"input_csv","delimitedtext")

#Check if layer is valid
if not csv_layer.isValid():
    print ("Layer not loaded")

#Add CSV data    
QgsProject.instance().addMapLayer(csv_layer)

#Selecting all features inside csv layer
csv_layer.selectAll()

#Copying all features to clipboard
iface.copySelectionToClipboard(csv_layer)

#Get target layer knowing its layer name
target = QgsProject.instance().mapLayersByName("target_layer")[0]

#Enable editing mode for the target layer
target.startEditing()

#Paste the csv copied features in the target layer
iface.pasteFromClipboard(target)

#Stop editing mode in the target layer and save edits
target.commitChanges()
