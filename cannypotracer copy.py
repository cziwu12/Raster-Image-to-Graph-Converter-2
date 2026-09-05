from PIL import Image
from potrace import Bitmap, POTRACE_TURNPOLICY_MINORITY  
import cv2

def main():
    yesOptions = ['yes', 'y']
    p0 = []
    p1 = []
    p2 = []
    p3 = []
    c_p0 = []
    c_p1 = []
    c_p2 = []
    
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
    print(plist)

    height = img.shape[0]

    with open(f"graph.txt", "w") as fp:
        for curve in plist:
            fs = curve.start_point
            startpoint = fs
            print(f"{fs.x},{fs.y}")
            for segment in curve.segments:
                if segment.is_corner:
                    end = segment.end_point
                    corner = segment.c

                    c_p0.append((startpoint.x, height - startpoint.y))
                    c_p1.append((corner.x, height - corner.y))
                    c_p2.append((end.x, height - end.y))

                    fp.write("\n"f"({startpoint.x}+t*({corner.x}-{startpoint.x}), {height - startpoint.y}+t*({height - corner.y}-{height - startpoint.y}))")
                    fp.write("\n"f"({corner.x}+t*({end.x}-{corner.x}), {height - corner.y}+t*({height - end.y}-{height - corner.y}))")
                else:
                    a = segment.c1
                    b = segment.c2
                    c = segment.end_point

                    p0.append((startpoint.x, height - startpoint.y))
                    p1.append((a.x, height - a.y))
                    p2.append((b.x, height - b.y))
                    p3.append((c.x, height - c.y))

                    fp.write("\n"f"((1-t)^3*{startpoint.x}+3*(1-t)^2*t*{a.x}+3*(1-t)*t^2*{b.x}+t^3*{c.x},(1-t)^3*{height - startpoint.y}+3*(1-t)^2*t*{height - a.y}+3*(1-t)*t^2*{height - b.y}+t^3*{height - c.y})")
                startpoint = segment.end_point

        print(f'Cornerpoints: \nc_p0: {c_p0} \nc_p1: {c_p1} \nc_p2: {c_p2}')
        print(f'Cubic bezier points: \np0: {p0} \np1: {p1} \np2: {p2} \np3: {p3}')

if __name__ == '__main__':
    main()

    #python actual_potrace.py john.png