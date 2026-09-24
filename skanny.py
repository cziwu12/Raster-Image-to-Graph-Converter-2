import numpy as np
from skan import Skeleton
from fitCurves.fitCurves import fitCurve
from pathlib import Path

output_dir = Path(r"C:\Users\notcz\repos\Raster-Image-to-Graph-Converter-2\outputs")

height_dir = output_dir / "imgheight.txt"
with open(height_dir, "r") as heig:
    height = int(heig.read())
    print(height)

paths = []
all_beziers = []

canny_array_dir = output_dir / "canny_array.npy"
canny_array = np.load(canny_array_dir)

skeleton = Skeleton(canny_array)

print(skeleton.n_paths)

for path_id in range(skeleton.n_paths):
    row_col_points = skeleton.path_coordinates(path_id)
    points = np.column_stack((row_col_points[:, 1] + 0.5, height - row_col_points[:, 0] - 0.5 ))
    paths.append(points)

    if len(points) >= 2:
        bezier_curves = fitCurve(points, 0.5)
        all_beziers.append(bezier_curves)

print(all_beziers)