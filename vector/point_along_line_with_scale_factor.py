#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   point_along_line_with_scale_factor.py
@Time    :   2022/07/04 14:45:55
@Author  :   Federica Gaspari 
@Version :   1.0
@Contact :   federica.gaspari@polimi.it, federica.gaspari@live.it
@License :   (C)Copyright 2022, Federica Gaspari
@Desc    :   pyQGIS script for computing points along line, reorder vertex on line and compute scale factor.
'''

# Define point layer to be used
pointlyr = QgsProject.instance().mapLayersByName(
    "points")[0]  # Change to match your layer name
#Define point layer to be used
linelyr = QgsProject.instance().mapLayersByName(
    "lines")[0]  # Change to match your layer name
# List all features in both layers
points = [f1 for f1 in pointlyr.getFeatures()]
lines = [f2 for f2 in linelyr.getFeatures()]
#Get fields from pointlyr
fields = pointlyr.fields()

#------
#Calculating points projected on given line

# List all vertices geometries before the projected ones
VertBefore = []
# List all vertices indexes before the projected ones
VertBeforeIx = []
# List all distances between prj points and previous closest vertex
distVertBefore = []
# List all points projected on line
pointsOnLine = []
# Iterate through points on list
for p in points:
    # Calculate distance, prj point, following vertes on line, position
    sqrdist, closest_pointxy, afterVertex, _ = min([line.geometry().closestSegmentWithContext(
        p.geometry().asPoint()) for line in lines], key=lambda x: x[0])
    # Calculate vertex before prj point
    vertex_beforeindex = afterVertex-1
    vertex_before = [v for v in lines[0].geometry().vertices()][afterVertex-1]
    # Compute distance between prj point e vertex before
    dist = QgsPoint(closest_pointxy).distance(vertex_before)
    # Update lists
    VertBefore.append(vertex_before)
    VertBeforeIx.append(vertex_beforeindex)
    distVertBefore.append(dist)
    pointsOnLine.append(closest_pointxy)

# -------------

# Compute list of line vertices
layer = QgsProject.instance().mapLayersByName("lines")[0]
iter = layer.getFeatures()
# List to be updated with vertex features
lineVert = []
for feature in iter:
    geom = feature.geometry()
    verts = geom.asMultiPolyline()  # use geom.asPolyline() for line geometry
    for vert in verts:
        for i in range(len(vert)):
            # Update list with retrieved data
            lineVert.append(QgsPoint(vert[i].x(), vert[i].y()))

# -------------

# Create updated and ordered list of line vertices
lineVert_new = []
k = 0
for item in lineVert:
    # List for storing point geometries and distancies when multiple point aftervertex are found
    pts_sameBVertex = []
    dist_sameBVertex = []
    for i in range(len(VertBeforeIx)):
        # Check if projected point are present immediately after the iterated vertex or not
        if VertBeforeIx[i]==k:
            print('Uguale')
            #Append point feature
            pts_sameBVertex.append(QgsPoint(pointsOnLine[i]))
            # Append point feature and its distance
            dist_sameBVertex.append(distVertBefore[i])                
        else:
            node = QgsPoint()
            node = item
    # Order point to be added based on their distances from common vertex before
    nodes = [x for _,x in sorted(zip(dist_sameBVertex,pts_sameBVertex))]
    # Append vertex before
    lineVert_new.append(node)
    # Check if there are other node to be added
    if len(nodes)> 0:
        lineVert_new.extend(nodes)    
    k = k+1

# --------------------
# Add new line computed with additional points to the QGIS map canvas
#Retrieve CRS info from input layer
epsg = pointlyr.crs().postgisSrid()
linea = iface.addVectorLayer("LineString?crs=epsg:"+str(epsg)+"&field=id:integer&index=yes","new_line","memory")
linea.startEditing()
feature = QgsFeature()
feature.setGeometry(QgsGeometry.fromPolyline(lineVert_new))
feature.setAttributes([1])
linea.addFeature(feature)
linea.commitChanges()
iface.zoomToActiveLayer()

# --------------------
# Split list into sublists based on corresponding indexes of projected points
#Convert list in QgsPoint list
new_pointsOnLine = []
for item in pointsOnLine:
    new_pointsOnLine.append(QgsPoint(item))
#Extract values of the new indexes for original points projected
new_indexes = []
for element in new_pointsOnLine:
    for item in lineVert_new:
        if element == item:
            position = lineVert_new.index(item)
            new_indexes.append(position)

#Define function for partitioning list depending on range defined by indices
def partition(alist, indices):
    copy_indices = []
    for e in indices:
        copy_indices.append(e+1)
    return [alist[i:j] for i, j in zip([0]+indices, copy_indices+[None])]

#Create sublists
prova_prova = partition(lineVert_new,new_indexes)

#----
#Create new vector layer with extracted segments
segments = QgsVectorLayer("LineString?crs=epsg:"+str(epsg)+"&field=id:integer&index=yes","segments","memory")
prov = segments.dataProvider()
feature1 = QgsFeature()
q=0
#Iterate in sublists and create polyline
for segment in prova_prova:
    feature1.setAttributes([q])
    feature1.setGeometry(QgsGeometry.fromPolyline(segment))
    q=q+1
    prov.addFeatures([feature1])

#-----
#Create new field and populate it with length values of the single segments
caps=prov.capabilities()
#Add length field
if caps & QgsVectorDataProvider.AddAttributes:
    lunghezza = prov.addAttributes([QgsField('length', QVariant.Double)])
    segments.updateFields()
#Define expression for field calculating
expression = QgsExpression('$length')
context = QgsExpressionContext()
context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(segments))
#Update features in layer with given expression
with edit(segments):
    for f0 in segments.getFeatures():
        context.setFeature(f0)
        f0['length']=expression.evaluate(context)
        segments.updateFeature(f0)
#Load segment layer with newly created features to the map canvas
QgsProject.instance().addMapLayer(segments)

