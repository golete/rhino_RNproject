import rhinoscriptsyntax as rs
from round_to_divisor import round_to_divisor
import math as m

def module_data():
    plane = rs.WorldXYPlane()

    head = rs.GetReal("Module vertical clearance (2.5-5)", 3.0, 2.5, 5.0)
    width = rs.GetReal("Module standard width (2.5-10)", 3.5, 1.2, 10)/2
    slope = (rs.GetReal("Slope percentage (2.5-10%)", 8, 2.5, 10))/100#percentage of maximum slope

    dist = rs.GetReal("Straight module linear distance (2.5-10)", 2.5, 1.0, 10.0) #length of straight module (float, meters)
    radi = rs.GetReal("Curve module arc radius (2.5-125)", 12.5, 2.5, 125.0) #radius of curve module through centerline (float, meters)

    am0 = (360*dist)/(2*m.pi*radi)
    am1 = round_to_divisor(am0,360)
    am = rs.GetReal("Curve module arc angle (suggested)", am1, 0.5, 90.0) #angle of curve module (float, meters)

    base_point = (0,0,0)
    head_point = (0,0,head)

    data = [width, dist, am, radi, slope, base_point, head_point]
    return (data)
