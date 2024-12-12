import os
from Decomposition import decomposition
import matplotlib.pyplot as plt
import numpy as np
import cv2

### The point of this python file is to test and compare the biomimetic decompositions on multiple instances of natural light vs low light images
## The comparison will also include comparison of distributions of decompositions

url_header = os.path.dirname(__file__)
#cat_url = r"\Data\NaturalImages\natural_images\cat\cat_0301.jpg"
cat_url = r"\Data\NaturalImages\natural_images\cat\cat_0001.jpg"
cat_url = url_header + cat_url
cat_image = cv2.imread(cat_url)

decompositions = decomposition(cat_image)
fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 6))
np.vectorize(lambda ax:ax.axis('off'))(ax)
k = 0
for i in range(3):
    for j in range(3):
        try:
            ax[i,j].imshow(decompositions[k])
        except:
            None
        #plt.axis("off")
        k += 1
fig.tight_layout()
plt.show()
print(["red_green, blue-yellow, value"])
print(["gray, edges, gabor_response"])

#plt.imshow(decompositions[-1])

#decompositions = decomposition(cat_url)
fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 6))
np.vectorize(lambda ax:ax.axis('off'))(ax)
k = 0
for i in range(3):
    for j in range(3):
        try:
            ax[i,j].hist(decompositions[k])
        except:
            None
        #plt.axis("off")
        k += 1
fig.tight_layout()
plt.show()
print(["red_green, blue-yellow, value"])
print(["gray, edges, gabor_response"])

#url_header = os.path.dirname(__file__)
#numb = 18
numb = 1
dark_url = rf"\Data\LowLight\{numb}.png"
dark_url = url_header + dark_url
dark_image = cv2.imread(dark_url)

decompositions = decomposition(dark_image)
fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 6))
np.vectorize(lambda ax:ax.axis('off'))(ax)
k = 0
for i in range(3):
    for j in range(3):
        try:
            ax[i,j].imshow(decompositions[k])
        except:
            None
        #plt.axis("off")
        k += 1
fig.tight_layout()
plt.show()
print(["red_green, blue-yellow, value"])
print(["gray, edges, gabor_response"])

fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(10, 6))
np.vectorize(lambda ax:ax.axis('off'))(ax)
k = 0
for i in range(3):
    for j in range(3):
        try:
            ax[i,j].hist(decompositions[k])
        except:
            None
        #plt.axis("off")
        k += 1
fig.tight_layout()
plt.show()
print(["red_green, blue-yellow, value"])
print(["gray, edges, gabor_response"])