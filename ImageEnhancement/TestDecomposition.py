import os
from Decomposition import decomposition
import matplotlib.pyplot as plt
import numpy as np


url_header = os.path.dirname(__file__)
cat_url = r"\Data\NaturalImages\natural_images\cat\cat_0301.jpg"
cat_url = url_header + cat_url

decompositions = decomposition(cat_url)
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

numb = 18
dark_url = r"\Data\LowLight\{numb}.png"
dark_url = url_header + dark_url

decompositions = decomposition(dark_url)
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