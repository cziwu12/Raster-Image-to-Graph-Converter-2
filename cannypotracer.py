import numpy as np 
from potrace import Bitmap, POTRACE_TURNPOLICY_MINORITY  
import cv2
import json
from pathlib import Path

def main():
    yesOptions = ['yes', 'y']
    curves = []
    
    IMG_PATH = input("image path: ").strip('"\'# ')
    img = cv2.imread(IMG_PATH)

    if img is None:
        print("Error: Could not load image.")
        exit()

    useResize = input("is resize needed? (Type yes if needed, else just enter any key):  ").lower() in yesOptions
    resizedImg = cv2.resize(img, None, fx=0.5, fy=0.5) if useResize else img

    gray = cv2.cvtColor(resizedImg, cv2.COLOR_BGR2GRAY)
    useBlur = input("is blur needed? (Type yes if needed, else just enter any key): ").lower() in yesOptions

    cv2.imshow('gray', gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    targetImg = (cv2.bilateralFilter(gray, d=4, sigmaColor=140, sigmaSpace=150) if useBlur else gray)
    #targetImg = (cv2.bilateralFilter(gray, d=4, sigmaColor=15, sigmaSpace=25) if useBlur else gray)

    if useBlur:
        cv2.imshow("resized win", targetImg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    canny = cv2.Canny(targetImg, 50, 150)

    output_dir = Path(r"C:\Users\notcz\repos\Raster-Image-to-Graph-Converter-2\outputs")
    canny_output_path = output_dir / "canny_array.npy"
    np.save(canny_output_path, canny)

    cv2.imwrite("cannyresult.png", canny)
    cv2.imshow("Canny (Enter any key to close)", canny)
    cv2.waitKey()
    cv2.destroyAllWindows()

    bm = Bitmap(canny, blacklevel=0.65)
    #bm.invert()
    plist = bm.trace(
        turdsize=2,
        turnpolicy=POTRACE_TURNPOLICY_MINORITY,
        alphamax=1,
        opticurve=True,
        opttolerance=0.2
    )

    height = img.shape[0]
    height_dir = output_dir / "imgheight.txt"
    with open(height_dir, "w") as high:
        high.write(str(height))

    graph_dir = output_dir / "graph.txt"
    with open(graph_dir, "w") as fp:
        for curve in plist:
            curve_ = []
            print(len(curve))
            fs = curve.start_point
            startpoint = fs

            for segment in curve.segments:
                if segment.is_corner:
                    end = segment.end_point
                    corner = segment.c

                    segment_ = {
                        "type": "corner",
                        "startpoint": (startpoint.x, height - startpoint.y),
                        "cornerpoint": (corner.x, height - corner.y),
                        "endpoint": (end.x, height - end.y)
                    }

                    fp.write("\n"f"({startpoint.x}+t*({corner.x}-{startpoint.x}), {height - startpoint.y}+t*({height - corner.y}-{height - startpoint.y}))")
                    fp.write("\n"f"({corner.x}+t*({end.x}-{corner.x}), {height - corner.y}+t*({height - end.y}-{height - corner.y}))")
                else:
                    a = segment.c1
                    b = segment.c2
                    c = segment.end_point

                    segment_ = {
                        "type": "cubic",
                        "startpoint": (startpoint.x, height - startpoint.y),
                        "c1": (a.x, height - a.y),
                        "c2": (b.x, height - b.y),
                        "endpoint": (c.x, height - c.y)
                    }

                    fp.write(f"((1-t)^3*{startpoint.x}+3*(1-t)^2*t*{a.x}+3*(1-t)*t^2*{b.x}+t^3*{c.x},(1-t)^3*{height - startpoint.y}+3*(1-t)^2*t*{height - a.y}+3*(1-t)*t^2*{height - b.y}+t^3*{height - c.y})\n")
                curve_.append(segment_)
                startpoint = segment.end_point
            curves.append(curve_)
        curve_data_dir = output_dir/ "curve_data.json"
        with open(curve_data_dir, "w") as cd:
            json.dump(curves, cd)

if __name__ == '__main__':
    main()

    #python actual_potrace.py john.png