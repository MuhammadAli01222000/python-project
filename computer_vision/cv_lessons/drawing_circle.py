import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
a=np.full((512,512,3),255,np.uint8)
#circle
#a=cv.circle(a,(200,200),50,(240,26,119),-1)
a=cv.rectangle(a,(100,100),(400,400),(240,26,199),10)
plt.imshow(a)
plt.show()