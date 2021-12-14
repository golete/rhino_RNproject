import rhinoscriptsyntax as rs
import math as m
import csv
from functions import table_writer

plane = rs.WorldXYPlane()

#DATA from MODULE_CREATOR.py
file = open('data.csv', 'r')
pre_data = list(csv.reader(file))
data = (pre_data[0])
data = [float(i) for i in data]
dist = data[1] #length of straight module (float, meters)
am = data[2] #angle of curve module (float, meters)
radi = data[3] #radius of curve module through centerline (float, meters)
slope = data[4] #percentage of maximum slope

items_A = "Straight","Curve"
items_B = "CCW","CW"
items_C = "UP","FLAT","DOWN"

dh = 1 #initial module DEFAULT direction (0 UP, 1 FLAT, 2 DOWN)
height = slope*dist
dhz = (1-dh)*height #change in height (UP 1, FLAT 0, DOWN -1)
angle = 0
cont = True
group = rs.AddGroup("group")

md_str = items_A[0]
rot_str = items_B[0]
dh_str = items_C[1]

md_cont = rs.GetObject("Select Last Module (if None press 'Enter')", 4096, True, True, False)
if md_cont:
    point_0 = rs.BlockInstanceInsertPoint(md_cont)
    md_disp = rs.BlockInstanceXform(md_cont)
    md_id = int((rs.BlockInstanceName(md_cont))[-1])
    angle = (m.degrees(m.atan2((md_disp[1,0]),(md_disp[0,0]))))
    md = md_id//3 #type of module (0 Straight, 1 Curve)
    md_str = items_A[md]
    dh = md_id%3
    dh_str = items_C[dh]
    dhz = (1-dh)*height #change in height (UP 1, FLAT 0, DOWN -1)
    rot = int((md_disp[0,1])/(md_disp[1,0])*-1)
    rot_str = items_B[rot]
else:
    point_0 = rs.GetPoint("Select base point") #First module insertion basepoint
    angle = rs.GetAngle(point_0, None, 0, "Route direction") #First module direction
    md_str = rs.GetString("Module type", md_str, items_A)
    if md_str is None: exit()
    md = items_A.index(md_str)
    rot = 1 #Mirror module (0 NO, 1 YES)
    if md == 1:
        rot_str = rs.GetString("Direction", rot_str, items_B)
        if rot_str is None: exit()
        rot = 1-(2*items_B.index(rot_str))
    rs.InsertBlock("RN"+str((3*md)+dh),point_0,(1,rot,1),angle*rot,(0,0,1)) #RN00 strup, 01 str, 02 strdown, 03 crvup, 04 crv, 05 crvdown
    block = rs.FirstObject()
    if block: rs.AddObjectToGroup(block,group)

while cont != None:
    #INSERTION POINT ADJUSTMENT
    if md == 0 :
        disp = rs.XformTranslation(((dist*m.cos(m.radians(angle))),(dist*m.sin(m.radians(angle))),dhz))
    elif md == 1 :
        cen = rs.XformTranslation(((radi*rot*m.cos(m.radians(angle+90))),(radi*rot*m.sin(m.radians(angle+90))),dhz)) #CENTER OF RADIUS
        cen_pt = rs.PointTransform(point_0, cen) #RADIUS FROM CENTER TO MODULE BASEPOINT
        disp_xy = rs.XformRotation2(rot*am,(0,0,1),cen_pt) #ROTATION OF POINT_0 FROM RADIUS CENTER
        disp_z = rs.XformTranslation([0,0,dhz])
        disp = rs.XformMultiply(disp_xy, disp_z)
    point_0 = rs.PointTransform(point_0, disp) #CHANGE point_0 FOR NEXT MODULE

    #SAVE Last module data to compare
    dhz_last = dhz
    md_last = md
    rot_last = rot

    #HEIGHT ADJUSTMENT
    dh_str = rs.GetString("Vertical direction", dh_str, items_C[(dh//2):(len(items_C)-(0**dh))])
    if dh_str is None: break
    dh = items_C.index(dh_str)
    dhz = (1-dh)*height
    #DIRECTION/ANGLE ADJUSTMENT
    angle = (angle+(md*am*rot))
    #NEXT MODULE TYPE
    md_str = rs.GetString("Module type", md_str, items_A)
    if md_str is None: break
    md = items_A.index(md_str)
    rot = 1
    if md == 1:
        rot_str = rs.GetString("Direction", rot_str, items_B)
        if rot_str is None: break
        rot = 1-(2*items_B.index(rot_str))
    #MODULE OR DIRECTION CHANGES NOTATION
    if dhz != dhz_last: #Add circle when vertical direction changes
        dhz_change = rs.AddCircle(point_0, 0.65)
        rs.ObjectLayer(dhz_change, "004_MODULES_Modslope-change")
        rs.AddObjectToGroup(dhz_change,group)
    if md != md_last: #Add circle when module type (straight/curve) changes
        md_change = rs.AddCircle(point_0, 0.5)
        rs.ObjectLayer(md_change, "003_MODULES_Modtype-change")
        rs.AddObjectToGroup(md_change,group)
    #INSERTION
    rs.InsertBlock("RN"+str((3*md)+dh),point_0,(1,rot,1),angle*rot,(0,0,1))
    #GROUPING
    block = rs.FirstObject()
    if block: rs.AddObjectToGroup(block,group)

group_objects = rs.ObjectsByGroup(group, True)
if group_objects:
    filename = rs.DocumentName() if rs.DocumentName() is not None else "innominado"
    table_writer.table_writer(group_objects, filename)
