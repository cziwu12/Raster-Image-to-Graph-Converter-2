from PIL import Image
from potrace import Bitmap, POTRACE_TURNPOLICY_MINORITY  
import cv2

def main():
    yesOptions = ['yes', 'y']
    
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
    print(plist)

    height = img.shape[0]

    with open(f"graph.txt", "w") as fp:
        potrace_curve1 = open("potrace_curve1", "w")
        startfirst = plist[1].start_point
        for segment1 in plist[1].segments:
            if segment1.is_corner:
                end1 = segment1.end_point
                potrace_curve1.write("\n"f"({startfirst.x}+t*({end1.x}-{startfirst.x}), {height - startfirst.y}+t*({height - end1.y}-{height - startfirst.y}))")
            else:
                q = segment1.c1
                w = segment1.c2
                e = segment1.end_point
                potrace_curve1.write("\n"f"((1-t)^3*{startfirst.x}+3*(1-t)^2*t*{q.x}+3*(1-t)*t^2*{w.x}+t^3*{e.x},(1-t)^3*{height - startfirst.y}+3*(1-t)^2*t*{height - q.y}+3*(1-t)*t^2*{height - w.y}+t^3*{height - e.y})")
            startfirst = segment1.end_point
        potrace_curve1.close
        for curve in plist:
            fs = curve.start_point
            startpoint = fs
            print(f"{fs.x},{fs.y}")
            for segment in curve.segments:
                if segment.is_corner:
                    end = segment.end_point
                    fp.write("\n"f"({startpoint.x}+t*({end.x}-{startpoint.x}), {height - startpoint.y}+t*({height - end.y}-{height - startpoint.y}))")
                else:
                    a = segment.c1
                    b = segment.c2
                    c = segment.end_point
                    fp.write("\n"f"((1-t)^3*{startpoint.x}+3*(1-t)^2*t*{a.x}+3*(1-t)*t^2*{b.x}+t^3*{c.x},(1-t)^3*{height - startpoint.y}+3*(1-t)^2*t*{height - a.y}+3*(1-t)*t^2*{height - b.y}+t^3*{height - c.y})")
                startpoint = segment.end_point

if __name__ == '__main__':
    main()

    #python actual_potrace.py john.png