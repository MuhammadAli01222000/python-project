from PIL import Image
import matplotlib.pyplot as plt
fpath='computer_vision/assets/img.jpg'
registan='computer_vision/assets/registan.png'

img=Image.open(fpath)
img2=Image.open(registan)
#img2=img2.resize((500,390),box=(150, 120, 400, 200))
#img2=img2.crop((200,00,90,90))
#img=img.resize((1000,500),resample=Image.NEAREST)
#plt.savefig("resize_registan.png")
#img2=img2.transpose(Image.ROTATE_180)
#img2=img2.transpose(Image.ROTATE_90)
#img2=img2.transpose(Image.ROTATE_270)
gray=img2.convert("L")
plt.imshow(gray,cmap='gray')

plt.show()
