import cv2
import numpy as np
import matplotlib.pyplot as plt
path='computer_vision/assets/registan.png'
img=cv2.imread(path)
print(img.shape) # (335, 597, 3)
img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
img=cv2.resize(img,(245,100),interpolation=cv2.INTER_NEAREST)
plt.imshow(img)
plt.show()