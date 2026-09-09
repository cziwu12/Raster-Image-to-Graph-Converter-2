import cv2
import numpy
import matplotlib
import json

tsize = 10 #int(input("tsteps: "))
tsteps = 1 / tsize

all_polygon_points = []
polygon_points = []

with open("curve_data.json", "r") as file:
    data = json.load(file)
    for curve in data:
        for segment in curve:
            if segment["type"] == "cubic":
                t = 0
                coords = []
                for i in range(1, tsize):
                    coords.append(((1-t)**3*segment["startpoint"][0]+3*(1-t)**2*t*segment["c1"][0]+3*(1-t)*t**2*segment["c2"][0]+t**3*segment["endpoint"][0], (1-t)**3*segment["startpoint"][1]+3*(1-t)**2*t*segment["c1"][0]+3*(1-t)*t**2*segment["c2"][1]+t**3*segment["endpoint"][1]))
                    t += tsteps
                    print(coords[i-1])
            else:
                t = 0
                coords = []
                for i in range(1, tsize):
                    coords.append((segment["startpoint"][0]+t*(segment["cornerpoint"][0]-segment["startpoint"][0]), segment["startpoint"][1]+t*(segment["cornerpoint"][1]-segment["startpoint"][1])))
                    coords.append((segment["cornerpoint"][0]+t*(segment["endpoint"][0]-segment["cornerpoint"][0]), segment["cornerpoint"][1]+t*(segment["endpoint"][1]-segment["cornerpoint"][1])))
                    t += tsteps
                    print(coords[i-1])
            polygon_points.append(coords)
                    

'''
tSize = 1 / int(input("t: "))

with open("potrace_curve1", "r") as pl:
    for bezier in pl:
        insert t into bezier
        find coords
        store xy coords in np array
        t += tSize
            
            
'''
