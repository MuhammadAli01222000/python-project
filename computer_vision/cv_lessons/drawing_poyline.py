import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv2
img=np.full((512,512,3),255,np.uint8)
pts=np.array([
    [100,500],
    [300,100],
    [500,500]
])
img=cv2.fillPoly(img,[pts],True,(66,135,245),5)
plt.imshow(img)
plt.show()