#Importing Libraries
import arcpy
import os
import scipy
from scipy import optimize
import numpy
from numpy import *


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "FractalNet"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [FractalDimensionCalculation]


class FractalDimensionCalculation(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "FractalDimensionCalculation"
        self.description = "The script is designed to calculate the fractal dimension of the road network. The territory is covered by a regular grid of hexagons, then the fractal dimension of the roads is calculated separately for each hexagon. Source Data Type: ShapeFile's. The calculation result is entered in the FD field of the attribute table of the hexagons shapefile."
        self.canRunInBackground = True

    def getParameterInfo(self):
        param0 = arcpy.Parameter(
           displayName ='AreaShapefile',
           name ='in_area',
           datatype ="DEShapeFile",
           parameterType ='Required',
           direction ='Input')
        param1 = arcpy.Parameter(
           displayName='RoadsShapefile',
           name='in_roads',
           datatype='DEShapeFile',
           parameterType='Required',
           direction='Input')
        param2 = arcpy.Parameter(
           displayName ='Hexagon area',
           name ='in_arhex',
           datatype ="GPArealUnit",
           parameterType ='Required',
           direction ='Input')
        param3 = arcpy.Parameter(
           displayName ='Directory',
           name ='out_dir',
           datatype ="DEFolder",
           parameterType ='Required',
           direction ='Input')
        return [param0, param1, param2, param3]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        hexagonOutput = parameters[3].valueAsText + '/hexagons.shp'
        intersectOutput = parameters[3].valueAsText + '/hexagonsInt.shp'
        dissolveOutput = parameters[3].valueAsText + '/hexagonsDiss.shp'
        area = parameters[0].valueAsText
        roads = parameters[1].valueAsText
        size = parameters[2].valueAsText

        description = arcpy.Describe(area)
        extent = description.extent
        arcpy.GenerateTessellation_management(parameters[3].valueAsText + '/hex.shp', extent, "HEXAGON", size)
        arcpy.Clip_analysis(parameters[3].valueAsText + '/hex.shp', area, hexagonOutput)
        arcpy.CalculateField_management(hexagonOutput,"ID", "!FID!","PYTHON")
        arcpy.Delete_management(parameters[3].valueAsText + '/hex.shp')

        arcpy.Intersect_analysis([hexagonOutput, roads], intersectOutput)
        arcpy.Dissolve_management(intersectOutput, dissolveOutput, "ID")

        arcpy.AddField_management(hexagonOutput, "TP", "FLOAT")
        path = parameters[3].valueAsText +"/Result"
        os.mkdir(path)
       
        dissfile = "HexagonsDiss"
        hexfile = "Hexagons"
        arcpy.CopyFeatures_management(dissolveOutput, path + "/" + dissfile + ".shp")
        arcpy.CopyFeatures_management(hexagonOutput, path + "/" + hexfile + ".shp")
        arcpy.Delete_management(hexagonOutput)
        arcpy.Delete_management(dissolveOutput)
        arcpy.Delete_management(intersectOutput)

        fitfunc = lambda p, x: (p[0] + p[1] * x)
        errfunc = lambda p, x, y: (y - fitfunc(p, x))

        arcpy.MakeFeatureLayer_management(path + '/' + dissfile + '.shp', dissfile + '_lyr')
        arcpy.MakeFeatureLayer_management(path + '/' + hexfile + '.shp', hexfile + '_lyr')
        a = int(arcpy.GetCount_management(path + '/' + dissfile + '.shp').getOutput(0))
        rows = arcpy.SearchCursor(path + '/' + dissfile + '.shp')
        total = []
        for row in rows:
           value = row.getValue("ID")
           total.append(int(value))
        count = arcpy.GetCount_management(path + '/' + hexfile + '.shp')
        i = 0
        while i < count:
           print (i)
           arcpy.SelectLayerByAttribute_management(dissfile + '_lyr',"NEW_SELECTION", "FID = %s" % i)
           arcpy.SelectLayerByAttribute_management(hexfile + '_lyr', "NEW_SELECTION", "ID = %s" % (total[i]))
           rt = arcpy.FeatureClassToFeatureClass_conversion(hexfile + '_lyr',path, "one_hex.shp")
           aa = arcpy.Describe(path + '/one_hex.shp').extent
           xmin = aa.XMin
           ymin  = aa.YMin
           squares = [4,16,64,256]
           intersections = [1]
           for n in range(len(squares)):
               arcpy.CreateFishnet_management(path + '/fishnet' + '_' + str(squares[n]) + '.shp', str(xmin) + ' ' + str(ymin), str(xmin) + ' ' + str(ymin+1),"0","0",int((squares[n])**(0.5)),int((squares[n])**(0.5)),"#","NO_LABELS",path + '/one_hex.shp',"POLYGON")
               arcpy.Clip_analysis(path + '/fishnet' + '_' + str(squares[n]) + '.shp',path + '/one_hex.shp', path + '/fish_net_clip' + '_' + str(squares[n]) + '.shp')
               arcpy.Delete_management(path + '/fishnet' + '_' + str(squares[n]) + '.shp')
               arcpy.MakeFeatureLayer_management(path + '/fish_net_clip' + '_' + str(squares[n]) + '.shp', 'fish_net_clip' + '_' + str(squares[n]) + '_lyr')
               c = int(arcpy.GetCount_management(arcpy.SelectLayerByLocation_management('fish_net_clip' + '_' + str(squares[n]) + '_lyr',"INTERSECT", dissfile + '_lyr')).getOutput(0))
               intersections.append(c)
               arcpy.Delete_management('fish_net_clip' + '_' + str(squares[n]) + '_lyr')
               arcpy.Delete_management(path + '/fish_net_clip' + '_' + str(squares[n]) + '.shp')
           edge = [1,0.5,0.25,0.125,0.0625]
           logx = log(edge)
           logy = log(intersections)
           qout,success = optimize.leastsq(errfunc, [0,0],args=(logx, logy),maxfev=30000)
           arcpy.CalculateField_management(hexfile + '_lyr',"TP", int(qout[1]*100000),"PYTHON")
           arcpy.CalculateField_management(hexfile + '_lyr',"TP", "float(!TP!)/(-200000)","PYTHON")
           arcpy.Delete_management(path + '/one_hex.shp')
           i = i + 1
        return

