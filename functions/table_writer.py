import rhinoscriptsyntax as rs
import math as m
import csv
import re
import os
import doctime

def table_writer(route,filename):
    fname = re.sub('.3dm',"",filename)
    timestamp = doctime.doctime()
    dir = "./routes"
    if not os.path.exists(dir):
        os.mkdir(dir)
    path = "./routes/"+filename+"_"+timestamp+".csv"

    #import data from MODULE_CREATOR.py
    file = open('data.csv', 'r')
    pre_data = list(csv.reader(file))
    data = (pre_data[0])
    data = [float(i) for i in data]

    with open(path, 'wb') as csvfile:

        fieldnames = ["type of module", "xy direction", "z direction", "module dimension", "magnitude", "", "excess", "number of modules"]
        module_dims = [data[1], data[2]]
        module_type = ["s", "c"]
        dim_unit = ["meters", "degrees"]

        table = csv.DictWriter(csvfile, fieldnames=fieldnames)

        route = list(filter(lambda x : rs.IsBlockInstance(x),route))
        route.reverse()

        first_module = route[0]
        module_name_a = rs.BlockInstanceName(first_module)

        counter = 0
        i = 0
        table.writeheader()

        for block in route:
            if rs.IsBlockInstance(block):
                module_name = rs.BlockInstanceName(block)

                if block == route[-1]:
                    module_name = "last"
                    counter = counter + 1

                if module_name_a != module_name:
                    module_number = int(module_name_a.lstrip("RN"))
                    md = module_number//3
                    dhz = 1-(module_number%3)
                    md_disp = rs.BlockInstanceXform(route[i-1])

                    rot = int(((md_disp[0,1])//(md_disp[1,0]))*-1)

                    table.writerow({"type of module" : module_type[md], "xy direction" : rot, "z direction" : dhz, "module dimension" : module_dims[md], "magnitude" : (counter*module_dims[md]), "" : dim_unit[md], "number of modules" : counter})
                    counter = 0

                module_name_a = module_name
                counter = counter + 1
                i = i + 1

        csvfile.flush()
