#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   point_along_line_based_on_line_attribute.py
@Time    :   2022/07/26 14:02:55
@Author  :   Federica Gaspari 
@Version :   1.0
@Contact :   federica.gaspari@polimi.it, federica.gaspari@live.it
@License :   (C)Copyright 2022, Federica Gaspari
@Desc    :   Script for computing point positions along a line at given distances based on given line attribute values.
'''
#Define input line layer
line_lyr = QgsProject.instance().mapLayersByName("line_layer")[0]
#Define here the desired name for the output point layer
name_layer = ""
#Execute the processing of the native algorithm and change the expression definition according to the field name
process = processing.run("native:pointsalonglines", {'INPUT': line_lyr,'DISTANCE':QgsProperty.fromExpression('"scale_f" * 100'),'START_OFFSET':0,'END_OFFSET':0,'OUTPUT':'TEMPORARY_OUTPUT'})
#Isolate output of the operation
mem_layer0 = process['OUTPUT']
#Rename the resulting layer as previously defined
mem_layer0.setName(name_layer)
#Add the obtained layer to the map canvas
QgsProject.instance().addMapLayer(mem_layer0)