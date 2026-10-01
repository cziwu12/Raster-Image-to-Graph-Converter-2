import cv2
import numpy as np
from skan import Skeleton
from fitCurves.fitCurves import fitCurve
from pathlib import Path
from scipy.signal import savgol_filter
from time import perf_counter

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

    t_coordinates = 0
    t_resample = 0
    t_smooth = 0
    t_fit = 0
    
    IMG_PATH = input("image path: ").strip('"\'# ')
    img = cv2.imread(IMG_PATH)

    if img is None:
        print("Error: Could not load image.")
        exit()

    useResize = input("is resize needed? (Type yes if needed, else just enter any key):  ").lower() in yesOptions
    resizedImg = cv2.resize(img, None, fx=0.5, fy=0.5) if useResize else img

    gray = cv2.cvtColor(resizedImg, cv2.COLOR_BGR2GRAY)
    useBlur = input("is blur needed? (Type yes if needed, else just enter any key): ").lower() in yesOptions

    targetImg = (cv2.bilateralFilter(gray, d=4, sigmaColor=140, sigmaSpace=150) if useBlur else gray)
    #targetImg = (cv2.bilateralFilter(gray, d=4, sigmaColor=15, sigmaSpace=25) if useBlur else gray)

    canny = cv2.Canny(targetImg, 50, 150)

    cv2.imwrite("cannyresult.png", canny)

    skeleton = Skeleton(canny) 

    print(skeleton.n_paths)

    height = canny.shape[0]

    for path_id in range(skeleton.n_paths):
        t = perf_counter()
        row_col_points = skeleton.path_coordinates(path_id)
        points = np.column_stack((row_col_points[:, 1] + 0.5, height - row_col_points[:, 0] - 0.5 ))
        paths.append(points)
        t_coordinates += perf_counter() - t

        t = perf_counter()
        points = resample_path(points, spacing=1.0)
        t_resample += perf_counter() - t

        t = perf_counter()
        points = smooth_path(points, window=11, polyorder=2)
        t_smooth += perf_counter() - t

        if len(points) >= 2:
            t = perf_counter()
            bezier_curves = fitCurve(points, 1.7)
            all_beziers.append(bezier_curves)
            t_fit += perf_counter() - t

    print("coordinates:", t_coordinates)
    print("resample:    ", t_resample)
    print("smooth:      ", t_smooth)
    print("fitCurve:    ", t_fit)

    with open("graph_skanny.txt", "w") as graph:
        for segment in all_beziers:
            for bezier in segment:
                graph.write(f"((1-t)^3*{bezier[0][0]}+3*(1-t)^2*t*{bezier[1][0]}+3*(1-t)*t^2*{bezier[2][0]}+t^3*{bezier[3][0]},(1-t)^3*{bezier[0][1]}+3*(1-t)^2*t*{bezier[1][1]}+3*(1-t)*t^2*{bezier[2][1]}+t^3*{bezier[3][1]})\n")

if __name__ == '__main__':
    main()