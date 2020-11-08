# FractalDimension
The FractalDimensionCalculation script is intended to calculate the transport provision of territories based on the fractal dimension of road networks.
The script has been tested for ArcGIS 10.5 and higher.

How it works: the territory is covered with a regular grid of hexagons, then the fractal dimension is calculated separately for the road network inside each hexagon. 
The level of transport provision is calculated as 1/2 of the value of the fractal dimension of the road network of each hexagon.

Input data type: ShapeFile's.
AreaShapefile - polygonal layer of the border of the study area;
RoadsShapefile - the linear layer of the road network for the study area;
Hexagon - area of the hexagon (you must specify the unit of measure for the area);
Directory - path to the folder where the calculation result will be saved.

Output Type: Hexagons.shp file.
The Hexagons.shp file will be located in the folder specified by the user when the script starts. 
The estimated value of transport provision for each hexagon will be saved in the TP field of the attribute table of the Hexagons.shp file.

To use the tool, save the ArcGIS Python tool FractalNet file, as well as FractalNet.pyt and FractalNet.Tool.pyt in your working directory. 
Using the Catalog window in ArcMap, copy the FractalNet.pyt tool into Toolboxes.
