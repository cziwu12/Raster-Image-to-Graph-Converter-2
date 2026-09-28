import cv2
import numpy as np
from skan import Skeleton
from fitCurves.fitCurves import fitCurve
from pathlib import Path
from scipy.signal import savgol_filter

def resample_path(points, spacing=1.0):
    if len(points) < 2:
        return points

    delta = np.diff(points, axis=0)
    distances = np.linalg.norm(delta, axis=1)

    cumulative = np.concatenate(([0], np.cumsum(distances)))

    total_length = cumulative[-1]

    if total_length == 0:
        return points[:1]

    samples = np.arange(0, total_length, spacing)

    if len(samples) == 0 or samples[-1] < total_length:
        samples = np.append(samples, total_length)

    x = np.interp(samples, cumulative, points[:, 0])
    y = np.interp(samples, cumulative, points[:, 1])

    return np.column_stack((x, y))


def smooth_path(points, window=7, polyorder=2):
    if len(points) < window:
        return points

    if window % 2 == 0:
        window += 1

    x = savgol_filter(points[:, 0], window, polyorder)
    y = savgol_filter(points[:, 1], window, polyorder)

    return np.column_stack((x, y))

def main():
    yesOptions = ['yes', 'y']
    paths = []
    all_beziers = []

    output_dir = Path(r"C:\Users\notcz\repos\Raster-Image-to-Graph-Converter-2\outputs")
    
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

    skeleton = Skeleton(canny) 

    print(skeleton.n_paths)

    height = canny.shape[0]

    for path_id in range(skeleton.n_paths):
        row_col_points = skeleton.path_coordinates(path_id)
        points = np.column_stack((row_col_points[:, 1] + 0.5, height - row_col_points[:, 0] - 0.5 ))
        paths.append(points)

        points = resample_path(points, spacing=1.0)
        points = smooth_path(points, window=11, polyorder=2)

        if len(points) >= 2:
            bezier_curves = fitCurve(points, 1.7)
            all_beziers.append(bezier_curves)

    print(all_beziers[0][0])

    graph_dir = output_dir / "graph_skanny.txt"

    with open(graph_dir, "w") as graph:
        for segment in all_beziers:
            for bezier in segment:
                graph.write(f"((1-t)^3*{bezier[0][0]}+3*(1-t)^2*t*{bezier[1][0]}+3*(1-t)*t^2*{bezier[2][0]}+t^3*{bezier[3][0]},(1-t)^3*{bezier[0][1]}+3*(1-t)^2*t*{bezier[1][1]}+3*(1-t)*t^2*{bezier[2][1]}+t^3*{bezier[3][1]})\n")

if __name__ == '__main__':
    main()