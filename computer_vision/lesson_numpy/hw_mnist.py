import numpy as np
import matplotlib.pyplot as plt

path="computer_vision/assets/mnist_test.csv" 
data=np.loadtxt(path,delimiter=',')
print(data.shape)
def label_1():
    x=data[2,1:]
    
    img=x.reshape((28,28))
    plt.title('1',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()


def label_7():
    x=data[0,1:]
    img=x.reshape((28,28))
    plt.title('7',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()

def label_2():
    x=data[1,1:]
    img=x.reshape((28,28))
    plt.title('2',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()

def label_3():
    x=data[18,1:]
    img=x.reshape((28,28))
   
    plt.title('3',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()

def label_9():
    x=data[16,1:]
    img=x.reshape((28,28))
   
    plt.title('9',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()


def label_5():
    x=data[15,1:]
    img=x.reshape((28,28))
   
    plt.title('5',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()


def label_0():
    x=data[13,1:]
    img=x.reshape((28,28))
   
    plt.title('0',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()



def label_6():
    x=data[11,1:]
    img=x.reshape((28,28))
    plt.title('6',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()


def label_4():
    x=data[19,1:]
    img=x.reshape((28,28))
    plt.title('4',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()



def label_5():
    x=data[6,1:]
    img=x.reshape((28,28))
    plt.title('5',pad=1)
    plt.imshow(img,cmap='gray')
    plt.show()