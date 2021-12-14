import rhinoscriptsyntax as rs
import math as m
import csv
from functions import module_data

data = module_data.module_data()
width = data[0]
dist = data[1]
am = data[2]
radi = data[3]
slope = data[4]
base_point = data[5]
head_point = data[6]

for i in range(6):
    dhz = 1-(i%3)
    end_point = (dist,0,((slope*dist)*dhz))
    if i//3 == 0:
        centerline = rs.AddLine(base_point, end_point)
        perimeterA = rs.OffsetCurve(centerline,[0,-1,0],width,(0,0,1))
        perimeterB = rs.OffsetCurve(centerline,[0,1,0],width,(0,0,1))
    if i//3 == 1:
        point0 = (0,radi,0)
        if point0:
            pp0 = rs.AddPoint(point0)
        point1 = (0, radi, (slope*dist))
        if point1:
            pp1 = rs.AddPoint(point1)
        pitch = ((slope*dist)*(360/am)*dhz)
        turns = (am/360)
        centerline = rs.RotateObject(rs.AddSpiral(point0, point1, pitch, turns, radi), point0, -90)
        perimeterA = rs.RotateObject(rs.AddSpiral(point0, point1, pitch, turns, radi-width), point0, -90)
        perimeterB = rs.RotateObject(rs.AddSpiral(point0, point1, pitch, turns, radi+width), point0, -90)
        rs.DeleteObject(pp0)
        rs.DeleteObject(pp1)

    o_point_find = rs.CurveStartPoint(centerline) #Find and add module origin point
    o_point = rs.AddPoint(o_point_find)

    pA0 = rs.CurveStartPoint(perimeterA)
    pB0 = rs.CurveStartPoint(perimeterB)
    pA1 = rs.CurveEndPoint(perimeterA)
    pB1 = rs.CurveEndPoint(perimeterB)

    l0 = rs.AddLine(pA0, pB0)
    l1 = rs.AddLine(pA1, pB1)

    base = rs.JoinCurves([perimeterA, perimeterB, l0, l1], True)
    volume = rs.ExtrudeCurveStraight(base, base_point, head_point)
#
    rs.DeleteObject(base)

    #Order by Layers
    rs.AddLayer("001_MODULES_Point", (255,255,0))
    rs.AddLayer("002_MODULES_Centerline", (255,0,0))
    rs.AddLayer("003_MODULES_Modtype-change", (255,0,255))
    rs.AddLayer("004_MODULES_Modslope-change", (0,255,255))
    rs.AddLayer("005_MODULES_Volume")
    rs.ObjectLayer(o_point, "001_MODULES_Point")
    rs.ObjectLayer(centerline, "002_MODULES_Centerline")
    rs.ObjectLayer(volume, "005_MODULES_Volume")

    block = rs.AddBlock([o_point, centerline, volume], base_point, "RN"+str(i), True)

with open('data.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(data[:5])
