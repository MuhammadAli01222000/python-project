from PIL  import Image
from PIL import features
import matplotlib.pyplot as plt
fname="computer_vision/assets/img.jpg"
img=Image.open(fname)

plt.imshow(img)
#img.save('1.png') # save
#print(img.filename) # name
#print(img.format) # format
#print(img.mode)
print(img.width)
# print(img.size) # size
#plt.show()