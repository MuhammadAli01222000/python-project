import cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt

path = "computer_vision/assets/registan.png"
imgpath = "computer_vision/assets/image.png"
mac='computer_vision/assets/mac.png'
cmap = "gray"
red = (252, 10, 26)
blue = (35, 35, 222)
yellow=(242, 226, 99)


def bounding_box1():
    img = np.full((600, 600, 3), 255, dtype=np.uint8)

    cv2.line(img, (100, 100), (140, 99), blue, 3)
    cv2.line(img, (100, 100), (99, 140), blue, 3)
    # top right
    cv2.line(img, (370, 101), (401, 101), blue, 3)
    cv2.line(img, (401, 101), (401, 141), blue, 3)
    # bottom left
    cv2.line(img, (99, 354), (101, 401), blue, 3)
    cv2.line(img, (101, 401), (141, 399), blue, 3)
    # bottom right
    cv2.line(img, (400, 350), (399, 399), blue, 3)
    cv2.line(img, (364, 400), (400, 399), blue, 3)
    # ruchnoy qilinghan hammasi
    plt.grid()
    plt.imshow(img, cmap=cmap)
    plt.show()


def bpunding_box2():
    img = np.full((800, 800, 3), 255, dtype=np.uint8)
    # 1
    cv2.line(img, (100, 100), (200, 100), red, 3)
    cv2.line(img, (100, 200), (200, 200), red, 3)
    cv2.line(img, (100, 200), (100, 100), red, 3)
    cv2.line(img, (200, 200), (200, 100), red, 3)
    # 1 line 1 - 2
    cv2.line(img, (150, 500), (150, 200), red, 3)
    # 2
    cv2.line(img, (700, 200), (700, 100), red, 3)
    cv2.line(img, (700, 100), (600, 100), red, 3)
    cv2.line(img, (600, 200), (600, 100), red, 3)
    cv2.line(img, (700, 200), (600, 200), red, 3)

    # 2 line 3 - 4
    cv2.line(img, (200, 550), (600, 550), red, 3)
    # 3
    cv2.line(img, (600, 600), (600, 500), red, 3)
    cv2.line(img, (700, 600), (600, 600), red, 3)
    cv2.line(img, (700, 500), (600, 500), red, 3)
    cv2.line(img, (700, 600), (700, 500), red, 3)

    # 3 line 5 - 6
    cv2.line(img, (650, 500), (650, 200), red, 3)

    # 4
    cv2.line(img, (200, 600), (100, 600), red, 3)
    cv2.line(img, (200, 600), (200, 500), red, 3)
    cv2.line(img, (100, 600), (100, 500), red, 3)
    cv2.line(img, (200, 500), (100, 500), red, 3)

    # 5 line 4 - 5
    cv2.line(img, (600, 150), (200, 150), red, 3)

    plt.grid()
    plt.imshow(img, cmap=cmap)
    plt.show()


def bounding_box3():
    img = cv2.imread(imgpath)
    # 1
    img = cv2.rectangle(img, (51, 45), (100, 100), red, -1)

    # 2
    img = cv2.rectangle(img, (401, 46), (350, 100), red, -1)

    # 3
    img = cv2.rectangle(img, (401, 399), (350, 350), red, -1)

    # 4
    img = cv2.rectangle(img, (50, 399), (100, 350), red, -1)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()


def bounding_box4():
    
    img = np.full((900, 900, 3), 255, dtype=np.uint8)
    # 1
    cv2.line(img, (200, 650), (200, 250), red, 3)
    cv2.circle(img, (200, 650), 28, red, -1)
    # 2
    cv2.line(img, (800, 650), (800, 250), red, 3)
    cv2.circle(img, (800, 650), 28, red, -1)

    # 3
    cv2.line(img, (800, 250), (200, 250), red, 3)
    cv2.circle(img, (800, 250), 28, red, -1)

    # 4
    cv2.line(img, (800, 650), (200, 650), red, 3)
    cv2.circle(img, (200, 250), 28, red, -1)


    plt.imshow(img, cmap=cmap)
    plt.show()

def draw_triangle():
    
    triangle=np.full((900,900,3),255,dtype=np.uint8)
    cv2.line(triangle,(800,800),(500,200),blue,5)
    cv2.line(triangle,(200,800),(500,200),blue,5)
    cv2.line(triangle,(800,800),(200,800),blue,5)


    plt.imshow(triangle)
    plt.show()

def draw_rhombus():
    a=np.full((900,900,3),255,dtype=np.uint8)
    cv2.line(a,(800,500),(500,200),blue,5)
    cv2.line(a,(800,500),(500,800),blue,5)
    cv2.line(a,(500,800),(200,500),blue,5)
    cv2.line(a,(200,500),(500,200),blue,5)



    plt.imshow(a)
    plt.show()

def windows_logo():
    img=np.full((900,900,3),255,dtype=np.uint8)
    cv2.rectangle(img,(0,0),(899,900),(52, 107, 235),-1)
    cv2.rectangle(img,(800,500),(500,200),(52, 235, 64),-1)
    cv2.rectangle(img,(200,200),(500,500),red,-1)
    cv2.rectangle(img,(800,800),(500,500),(235, 232, 52),-1) 
     # Padding: yuqori, pastki, chap, o'ng
    cv2.rectangle(img,(500,500),(200,800),blue,-1)
    plt.imshow(img)
    plt.show()

def bounding_box_glasses():
    path=cv2.imread(mac)
    img=np.array(path)
    cv2.rectangle(img,(1200,600),(990,400),blue,4)
    plt.imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    plt.show()