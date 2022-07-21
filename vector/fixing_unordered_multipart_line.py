#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   fixing_unordered_multipart_line.py
@Time    :   2022/07/21 10:57:38
@Author  :   Federica Gaspari 
@Version :   1.0
@Contact :   federica.gaspari@polimi.it, federica.gaspari@live.it
@License :   (C)Copyright 2022, Federica Gaspari
@Desc    :   Extracting vertices from a multipart line layer whose vertices are unordered.
'''

#Define line layer you want to process
layer_line = QgsProject.instance().mapLayersByName('line')[0]
#Split layer using "multiparts to single parts"
proc = processing.run("native:multiparttosingleparts",{'INPUT':layer_line, 'OUTPUT':'TEMPORARY_OUTPUT'})
singleparts = proc['OUTPUT']
#Load singleparts output
QgsProject.instance().addMapLayer(singleparts)
#Snap the ends of the lines to each other using the "snap geometries" function
proc1 = processing.run("native:snapgeometries", {'INPUT': singleparts, 'REFERENCE_LAYER': singleparts, 'TOLERANCE': 10, 'BEHAVIOR': 0, 'OUTPUT':'TEMPORARY_OUTPUT'})
snap = proc1['OUTPUT']
#Load snapped output
QgsProject.instance().addMapLayer(snap)
#Dissolve the snapped layer to get the single parts back to multiparts
proc2 = processing.run("native:dissolve", {'INPUT':snap,'FIELD':[],'OUTPUT':'TEMPORARY_OUTPUT'})
dissolve = proc2['OUTPUT']
#Load dissolved output
QgsProject.instance().addMapLayer(dissolve)
#Run "line merge" on the snapped, dissolved layer
proc3 = processing.run("native:mergelines", {'INPUT': dissolve, 'OUTPUT':'TEMPORARY_OUTPUT'})
merge = proc3['OUTPUT']
#Load merged output
QgsProject.instance().addMapLayer(merge)
#Extract ordered vertices
proc4 = processing.run("native:extractvertices", {'INPUT': merge, 'OUTPUT':'TEMPORARY_OUTPUT'})
vertices = proc4['OUTPUT']
QgsProject.instance().addMapLayer(vertices)