import cv2
import numpy as np

image = cv2.imread("h1.jpg")
cv2.imshow("Image", image)
newimage = cv2.resize(image, (50,50))
cv2.imshow("new image is ", newimage)
colorChanged = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("colorChanged image is ", colorChanged)
cv2.imwrite("output.png",image)

if cv2.waitKey(0) == 27:    
    cv2.destroyAllWindows()


canvas = np.zeros((500, 500, 3), dtype="uint8")
cv2.rectangle(canvas, (50,50),(200,200),(25,234,35),5)
cv2.circle(canvas, (300,300),50,(255,0,35),5)
cv2.line(canvas, (50,50),(300,300),(255,0,35),5)
cv2.imwrite("shapes.jpg",canvas)
cv2.imshow("convas", canvas)

if cv2.waitKey(0) == 27:
    cv2.destroyAllWindows()