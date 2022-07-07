uri = "file:///C:/Users/Admin/Desktop/prova.csv?encoding=%s&delimiter=%s&xField=%s&yField=%s&crs=%s" % ("UTF-8",";", "x", "y","epsg:25832")
import os
import processing 

#Make a vector layer
csv_layer=QgsVectorLayer(uri,"prova","delimitedtext")

#Check if layer is valid
if not csv_layer.isValid():
    print ("Layer not loaded")

#Add CSV data    
QgsProject.instance().addMapLayer(csv_layer)

csv_layer.selectAll()

iface.copySelectionToClipboard(csv_layer)

csv_layer=QgsVectorLayer(uri,"prova","delimitedtext")

cartelli = QgsProject.instance().mapLayersByName("provacartelli")[0]

cartelli.startEditing()

iface.pasteFromClipboard(cartelli)

cartelli.commitChanges()
