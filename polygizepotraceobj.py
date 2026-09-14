import json
from matplotlib import pyplot as plt
import numpy as np
import cv2

tsize = 10 #int(input("tsteps: "))
tsteps = 1 / tsize

allcoords = []
plotpointx = []
plotpointy = []

with open("curve_data.json", "r") as file:
    with open("polypoints.txt", "w") as poly:
        data = json.load(file)
        for curve in data:
            coords = []
            for segment in curve:
                if segment["type"] == "cubic":
                    t = 0
                    for i in range(1, tsize):
                        t = i / tsize
                        coords.append(((1-t)**3*segment["startpoint"][0]+3*(1-t)**2*t*segment["c1"][0]+3*(1-t)*t**2*segment["c2"][0]+t**3*segment["endpoint"][0], (1-t)**3*segment["startpoint"][1]+3*(1-t)**2*t*segment["c1"][1]+3*(1-t)*t**2*segment["c2"][1]+t**3*segment["endpoint"][1]))
                        t += tsteps
                        print(f't: {t} type: {segment["type"]} : {coords[i-1]}')
                else:
                    t = 0
                    for i in range(1, tsize):
                        t = i / tsize
                        coords.append((segment["startpoint"][0]+t*(segment["cornerpoint"][0]-segment["startpoint"][0]), segment["startpoint"][1]+t*(segment["cornerpoint"][1]-segment["startpoint"][1])))
                        coords.append((segment["cornerpoint"][0]+t*(segment["endpoint"][0]-segment["cornerpoint"][0]), segment["cornerpoint"][1]+t*(segment["endpoint"][1]-segment["cornerpoint"][1])))
                        t += tsteps
                        print(f't: {t} type: {segment["type"]} : {coords[i-1]}')
                #allcoords.append(coords)
            poly.write(f'{str(coords)}\n')
            allcoords.append(coords)

image = np.full((1000, 800, 3), 255, dtype=np.uint8)

for coord in allcoords:
    arr = np.array(coord, dtype=np.int32)
    print(arr)
    cv2.fillPoly(image, arr, (255, 0, 0))

save = cv2.imwrite("rasterized_ver.png", image)
cv2.imshow("rasterized_ver.png", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

'''

for corrds in polygon_points:
    x, y = zip(*corrds)  
    x = list(x)
    y = list(y)
    plotpointx.append(x)
    plotpointy.append(y)

with open("john.txt", "w") as john:
    john.write(str(plotpointx))

for x, y in zip(plotpointx, plotpointy):
    plt.plot(x, y)

plt.show()
 

'''