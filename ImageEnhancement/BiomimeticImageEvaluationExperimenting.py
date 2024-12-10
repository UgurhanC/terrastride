import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import math
import skimage.filters as filters
from skimage import io, color

# Load Dark Image
numb = 18
dark_image = cv2.imread(f"/kaggle/input/dark-face-dataset/image/{numb}.png")

#Load Light Image
natural_image = cv2.imread("/kaggle/input/natural-images/natural_images/cat/cat_0301.jpg")


### Saliency Experiment
saliency_detector = cv2.saliency.StaticSaliencySpectralResidual_create()

# Compute the saliency map
(success, saliency_map) = saliency_detector.computeSaliency(natural_image)

# Normalize the saliency map for better visualization
saliency_map = (saliency_map * 255).astype("uint8")

"""# Display the original image and saliency map
plt.figure(figsize=(12, 6))

# Original image
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(natural_image, cv2.COLOR_BGR2RGB))
plt.title("Original Image")
plt.axis("off")

# Saliency map
plt.subplot(1, 2, 2)
plt.imshow(saliency_map, cmap="gray")
plt.title("Saliency Map (Spectral Residual)")
plt.axis("off")

plt.tight_layout()
plt.show()"""


### Parvocellular & Magnocellular Experiment
retina = cv2.bioinspired.Retina.create((natural_image.shape[1], natural_image.shape[0]))
 
# the retina object is created with default parameters. If you want to read
# the parameters from an external XML file, uncomment the next line
#retina.setup('MyRetinaParameters.xml')
 
# feed the retina with several frames, in order to reach 'steady' state
for i in range(20):
    retina.run(natural_image)
 
# get our processed image :)
retinaOut_parvo = retina.getParvo()
 
"""# show both the original image and the processed one
#plt.imshow('image', natural_image)
plt.imshow(cv2.cvtColor(retinaOut_parvo, cv2.COLOR_BGR2RGB))
plt.title('retina parvo out')
 
# wait for a key to be pressed and exit
#cv2.waitKey(0)
#cv2.destroyAllWindows()
 
# write the output image on a file
#cv2.imwrite('checkershadow_parvo.png', retinaOut_parvo)"""

retinaOut_magno = retina.getMagno()
"""plt.imshow(retinaOut_magno)
plt.title("retina magno out")"""


#Static Saliency Experiment
# Static Saliency Fine Grained
saliency_detector_fine = cv2.saliency.StaticSaliencyFineGrained_create()

# Compute the saliency map
(success_fine, saliency_map_fine) = saliency_detector_fine.computeSaliency(natural_image)

# Normalize the saliency map
saliency_map_fine = (saliency_map_fine * 255).astype("uint8")
"""
# Display the fine-grained saliency map
plt.figure(figsize=(6, 6))
plt.imshow(saliency_map_fine, cmap="gray")
plt.title("Saliency Map (Fine Grained)")
plt.axis("off")
plt.show()"""


# Edges Experiment (Obsolete) #The current algorithm uses canny edge detection instead
nat_gray = cv2.cvtColor(natural_image, cv2.COLOR_BGR2GRAY)
nat_edges = cv2.Laplacian(nat_gray, cv2.CV_64F)
"""
plt.imshow(nat_edges)
plt.axis("off")
plt.show()"""


# Color Opponency Experiment
blue, green, red = cv2.split(natural_image)

red_green = red - green
blue_yellow = blue - (red + green) / 2
brightness = (red + green + blue) / 3
"""
plt.imshow(blue_yellow)"""


# Gabor Filter Experiment
gabor_response, _ = filters.gabor(nat_gray, frequency=0.6, theta=np.pi/4)
"""
plt.imshow(gabor_response)"""