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
                        t += tsteps
                        print(f't: {t} type: {segment["type"]} : {coords[i-1]}')
                    t = 0
                    for i in range(1, tsize):
                        t = i / tsize
                        coords.append((segment["cornerpoint"][0]+t*(segment["endpoint"][0]-segment["cornerpoint"][0]), segment["cornerpoint"][1]+t*(segment["endpoint"][1]-segment["cornerpoint"][1])))
                        t += tsteps
                        print(f't: {t} type: {segment["type"]} : {coords[i-1]}')
                #allcoords.append(coords)
            poly.write(f'{str(coords)}\n')
            allcoords.append(coords)

image = np.full((1200, 1200, 3), 255, dtype=np.uint8)

arr = np.array(allcoords[0], dtype=np.int32)

Start = tuple(map(int, map(round, allcoords[0][0])))
End = tuple(map(int, map(round, allcoords[0][-1])))

print(Start)
print(End)

print("a")
print(arr.shape)
print(arr.min(axis=0))
print(arr.max(axis=0))
print(arr[0])
print(arr[-1])

'''
for coord in allcoords:
    arr = np.array(coord, dtype=np.int32)
    #cv2.polylines(image, [arr], True, (255, 0, 0))
    cv2.fillPoly(image, [arr], (255, 0, 0))
'''
cv2.polylines(image, [arr], False, (0, 0, 0))
cv2.circle(image, Start, 6, (0, 0, 255), -1)
cv2.circle(image, End, 6, (0, 255, 0), -1)

lines = cv2.imwrite("lines.png", image)

cv2.fillPoly(image, [arr], (255, 0, 0))
    
save = cv2.imwrite("rasterized_ver1.png", image)
cv2.imshow("rasterized_ver.png", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

print("b")
print(image[500, 400])
print(cv2.boundingRect(arr))
mask = np.any(image != 255, axis=2)
ys, xs = np.where(mask)

print(xs.min(), xs.max(), ys.min(), ys.max())

print("arr:", arr.shape)
print("bbox:", cv2.boundingRect(arr))
print("outside:", image[500, 400])
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