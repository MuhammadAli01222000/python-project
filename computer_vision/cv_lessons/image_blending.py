import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv2
hh='computer_vision/assets/img.jpg'
registan="computer_vision/assets/registan.png"
logo=cv2.imread(hh)
img=cv2.imread(registan)
#convert to rgb
logo=cv2.cvtColor(logo,cv2.COLOR_BGR2RGB)
img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
#logoni kicraytrsh va  tepaga kotarsh
logo = cv2.resize(logo, (512, 512))
img = cv2.resize(img, (512, 512))
res=logo[350:360,150:150]
print(res.shape)

plt.grid()
#dst=cv2.addWeighted(img,0.3,logo,0.5,0)
plt.imshow(res)
plt.show()