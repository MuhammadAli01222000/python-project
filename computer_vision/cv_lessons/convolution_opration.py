import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv2
img=cv2.imread("computer_vision/assets/run.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

plt.show()