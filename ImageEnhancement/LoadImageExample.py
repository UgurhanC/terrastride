import cv2
import os
import matplotlib.pyplot as plt

img_url = "\Data\LowLight\18.png"
img_url = os.path.dirname(__file__) + img_url

img = cv2.imread(r"c:\Users\johne\Documents\terrastride\ImageEnhancement\Data\LowLight\18.png")
plt.imshow(img)
plt.show()

img2 = cv2.imread(r"c:\Users\johne\Documents\terrastride\ImageEnhancement\Data\NaturalImages\natural_images\cat\cat_0000.jpg")
plt.imshow(img2)
plt.show()