import cv2
import numpy as np
import matplotlib.pyplot as plt
path='computer_vision/assets/registan.png'
img=cv2.imread(path)
#img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
#cv2.imwrite(path,img) # save
plt.imshow(img)
plt.show()