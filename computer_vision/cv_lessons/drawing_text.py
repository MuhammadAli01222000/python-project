import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv2
img=np.full((512,512,3),255,np.uint8)
#img=cv2.rectangle(img,(100,100),(400,400),(240,26,119),-1)
font=cv2.FONT_HERSHEY_SIMPLEX
img=cv2.putText(img,"TEXT",(100,300),font,5,(240,26,119))
plt.imshow(img)
plt.show()