import cv2

image = cv2.imread(input("image path: "), cv2.IMREAD_GRAYSCALE)

_, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
#canny = cv2.Canny(image, 50, 150)

#kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
#thick = cv2.dilate(canny, kernel)

#centerline = cv2.ximgproc.thinning(thick)
centerline = cv2.ximgproc.thinning(binary)
#centerline = cv2.ximgproc.thinning(canny)

#cv2.imwrite("canny.png", canny)
#cv2.imwrite("thick.png", thick)
cv2.imwrite("binary.png", binary)
cv2.imwrite("centerlines.png", centerline)
