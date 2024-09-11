import arcpy

def sanitize_name(name):
    for char in [" ", "-", "&", "/", "\\"]:
        name = name.replace(char, "_")
    if name[0].isdigit():
        name = "_" + name
    return name

#specifier of which map should be used 
aprx = arcpy.mp.ArcGISProject("CURRENT")
map = aprx.activeMap
local_gdb_path = aprx.defaultGeodatabase

# List to hold the web layers to be removed later
web_layers_to_remove = []

#loop trough all layers 
for layer in map.listLayers():
    if layer.isWebLayer:
        desc = arcpy.Describe(layer)
        if desc.dataType != "FeatureLayer":
            print(f"Skipping {layer.name} as it is not a Feature Layer.")
            continue  # Skip to the next iteration if the layer is not a Feature Layer
        
        local_layer_name = sanitize_name(layer.name) + "_local"
        local_layer_path = f"{local_gdb_path}/{local_layer_name}"
        
        arcpy.management.CopyFeatures(layer, local_layer_path)
        local_layer = map.addDataFromPath(local_layer_path)
        arcpy.management.ApplySymbologyFromLayer(local_layer, layer)
        
        # Add the web layer to the list to be removed later
        web_layers_to_remove.append(layer)

# Remove all web layers from the map
for web_layer in web_layers_to_remove:
    map.removeLayer(web_layer)

# Dictionary to keep track of layer names
layer_names = {}

# List to hold layers to be removed
layers_to_remove = []

# Check for duplicate layers
for layer in map.listLayers():
    if layer.name in layer_names:
        layers_to_remove.append(layer)  # Add duplicate layers to the list
    else:
        layer_names[layer.name] = 1  # Add new layer names to the dictionary

# Remove duplicate layers from the map
for layer in layers_to_remove:
    map.removeLayer(layer)

aprx.save()

