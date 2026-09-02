import cv2
import numpy
import matplotlib

tSize = int(input("t: "))

with open("potrace_curve1", "r") as pl:
    for bezier in pl:
        print(bezier)