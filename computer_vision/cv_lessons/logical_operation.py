import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv2
import requests as rq
import json

url = "https://raw.githubusercontent.com/Naxalov/ComputerVision/master/ROAD/road_signs/bus_stop/COCO.json"

hh = "computer_vision/assets/img.jpg"
registan = "computer_vision/assets/registan.png"

def get_points():
    response = rq.get(url)
    print(response.raise_for_status())
    data = response.json()
    res = data["annotations"]
    a = res[0]
    segmentation = a["segmentation"]
    result=np.array(segmentation).reshape(8,2)
    print(result.shape)
    plt.imshow(result,cmap='gray')
    plt.show()


a = get_points()


"""

img = np.array(
    [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ],
    dtype=np.uint8,
)

img2 = np.array(
    [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ],
    dtype=np.uint8,
)
dst=cv2.bitwise_and(img,img2)
print(dst)
fig,ax=plt.subplots(1,2)
#ax[0].imshow(img,cmap='gray')
#ax[1].imshow(img2,cmap="gray")
A=np.zeros((300,300),dtype=np.uint8)
R=80
X=300//2
Y=300//2
A=cv2.circle(A,(X,Y),R,200,-1)
B=np.zeros((300,300),dtype=np.uint8)
R-=15
B=cv2.rectangle(B,(X-R,Y-R),(X+R,Y+R),200,-1)
fig,ax=plt.subplots(1,3)
#ax[0].imshow(A,cmap='gray')
#ax[1].imshow(B,cmap='gray')
#ax[2].imshow(cv2.bitwise_and(A,B),cmap='gray')


img_h=cv2.imread(hh)
img_h=cv2.cvtColor(img_h,cv2.COLOR_BGR2RGB)
img_r=cv2.imread(registan)
img_r=cv2.cvtColor(img_r,cv2.COLOR_BGR2RGB)
mask=np.zeros((820,820,3),dtype=np.uint8)
plt.imshow(img_r)


"""
