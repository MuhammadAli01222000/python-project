import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv2

A = np.array([[255, 250], [50, 255]], dtype=np.uint8)

B = np.array([[0, 50], [100, 255]], dtype=np.uint8)
img = np.array([[10, 20, 30, 40, 50, 100]], dtype=np.uint8)

A = np.zeros((300, 300), dtype=np.uint8)
B = np.zeros((300, 300), dtype=np.uint8)
R = 80
B = cv2.rectangle(B, (150 - R, 150 - R), (150 + R, 150 + R), 150, -1)
fig, ax = plt.subplots(1, 4)
A = cv2.circle(A, (150, 150), R + 15, 150 - 1)
ax[0].imshow(A, cmap="gray")
ax[1].imshow(B, cmap="gray")
ax[2].imshow(cv2.add(A, B), cmap="gray")


plt.show()
