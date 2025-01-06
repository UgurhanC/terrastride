from ApplyImageEnhancement import apply_image_enhancement
import json
import os
import cv2
import matplotlib.pyplot as plt

with open('best_params.json') as f:
    best_params = json.load(f)

url_header = os.path.dirname(__file__)
test_image_url = url_header + r"\Data\LowLight\18.png"
#test_image_url2 = url_header + r"\Data\LowLight\1.png"

test_image1 = cv2.imread(test_image_url)
enhanced_image1 = apply_image_enhancement(test_image1,best_params)

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
plt.tight_layout()
plt.show()