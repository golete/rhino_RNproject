import rhinoscriptsyntax as rs
import math as m
import csv

#import csv table file
path = rs.OpenFileName("Select .csv source file", "Comma separated values file (*.csv)|*.csv||", None, None, "*.csv")
csvfile = open(path)
tableraw = tuple(csv.reader(csvfile))
table = tableraw[1:]
plane = rs.WorldXYPlane()

#import data from MODULE_CREATOR.py
file = open('data.csv', 'r')
pre_data = list(csv.reader(file))
data = (pre_data[0])
data = [float(i) for i in data]
dist = data[1] #length of straight module (float, meters)
am = data[2] #angle of curve module (float, meters)
radi = data[3] #radius of curve module through centerline (float, meters)
slope = data[4] #percentage of maximum slope
height = slope*dist

#router
point_0 = rs.GetPoint("Select base point") #punto base de modulo
angle = rs.GetAngle(point_0) #direccion de ruta
md = 0
group = rs.AddGroup("Grupo")

dhz_last = 0
md_last = 0

for row in table:
    #MODULE DATA FROM TABLE
    md_s = row[0] #STRAIGHT (0) or CURVE (1)
    if md_s == "s":
        md = 0
    elif md_s == "c":
        md = 1
    rot = int(row[1]) #DIRECTION CCW (1) or CW (-1)
    dh = 1-int(row[2]) #UP FLAT DOWN
    dhz = (1-dh)*height
    mag = int(row[-1])

    #MODULE OR DIRECTION CHANGES NOTATION
    if dhz != dhz_last: #Add circle when vertical direction changes
        dhz_change = rs.AddCircle(point_0, 0.65)
        rs.ObjectLayer(dhz_change, "004_MODULES_Modslope-change")
        rs.AddObjectToGroup(dhz_change,group)
    if md != md_last: #Add circle when module type (straight/curve) changes
        md_change = rs.AddCircle(point_0, 0.5)
        rs.ObjectLayer(md_change, "003_MODULES_Modtype-change")
        rs.AddObjectToGroup(md_change,group)

    #Insert module array according to module data
    for i in range(mag):
        #INSERT BLOCK
        rs.InsertBlock("RN"+str((3*md)+dh),point_0,(1,rot,1),angle*rot,(0,0,1))
        #INSERTION POINT ADJUSTMENT
        if md == 0 :
            disp = rs.XformTranslation(((dist*m.cos(m.radians(angle))),(dist*m.sin(m.radians(angle))),dhz))
        elif md == 1 :
            cen = rs.XformTranslation(((radi*rot*m.cos(m.radians(angle+90))),(radi*rot*m.sin(m.radians(angle+90))),dhz)) #centro de rotacion de cambio de point_0
            cen_pt = rs.PointTransform(point_0, cen) #ubicacion de centro de rotacion del modulo desde point_0
            disp_xy = rs.XformRotation2(rot*am,(0,0,1),cen_pt) #cambio de rotacion de point_0
            disp_z = rs.XformTranslation([0,0,dhz])
            disp = rs.XformMultiply(disp_xy, disp_z)
        point_0 = rs.PointTransform(point_0, disp) #cambio de point_0 para siguiente modulo

        #DIRECTION/ANGLE ADJUSTMENT
        angle = (angle+(md*am*rot)) #ajuste de angulo de direccion de ruta

        #GROUPING
        block = rs.FirstObject()
        if block: rs.AddObjectToGroup(block,group)

    #SAVE Last module data to compare
    dhz_last = dhz
    md_last = md
