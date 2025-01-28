from ApplyImageEnhancement import apply_image_enhancement
import json
import os
import cv2
import matplotlib.pyplot as plt
import time

"""
with open('best_params.json') as f:
    best_params = json.load(f)
"""



best_params = {
    "Saturation": 0.05079967757819648,
    "CLAHE_clipLimit_Value": 2.525144052221287,
    "CLAHE_clipLimit_BGR": 3.6481905337323903,
    "Retinex_gain": 1.1856138179236042,
    "Retinex_sigma1": 12.602866099185661,
    "Retinex_sigma2": 78.29144514892346,
    "Retinex_sigma3": 169.00897570787157,
    "Blend_ratio": 0.07407034069082408,
    "gamma": 1.3266392904177562,
    "brightness_boost": 22.896780890614952
}

url_header = os.path.dirname(__file__)
test_image_url = url_header + r"/Data/LowLight/18.png"
#test_image_url2 = url_header + r"\Data\LowLight\1.png"

print(test_image_url)

test_image1 = cv2.imread(test_image_url)
vclahe = cv2.createCLAHE(clipLimit = best_params["CLAHE_clipLimit_Value"], tileGridSize=(8, 8)) #Adjusted clipLimit
bgrclahe = cv2.createCLAHE(clipLimit = best_params["CLAHE_clipLimit_BGR"], tileGridSize=(8, 8))

t0 = time.time()
enhanced_image1 = apply_image_enhancement(test_image1,best_params, vclahe=vclahe, bgrclahe=bgrclahe)
t1 = time.time()

#test_image2 = cv2.imread(test_image_url2)
#enhanced_image2 = apply_image_enhancement(test_image2,best_params)

#fig, ax = plt.subplots(1,2)

"""ax[0,0].imshow(cv2.cvtColor(test_image1,cv2.COLOR_BGR2RGB))
ax[0,0].axis("off")
ax[0,1].imshow(cv2.cvtColor(enhanced_image1,cv2.COLOR_BGR2RGB))
ax[0,1].axis("off")"""

"""ax[0].imshow(cv2.cvtColor(test_image1,cv2.COLOR_BGR2RGB))
ax[0].axis("off")"""
plt.imshow(cv2.cvtColor(enhanced_image1,cv2.COLOR_BGR2RGB))
plt.axis("off")

"""ax[1,0].imshow(cv2.cvtColor(test_image2,cv2.COLOR_BGR2RGB))
ax[1,0].axis("off")
ax[1,1].imshow(cv2.cvtColor(enhanced_image2,cv2.COLOR_BGR2RGB))
ax[1,1].axis("off")

"""



total_time = t1-t0
print("Time:", total_time)

plt.tight_layout()
plt.show()