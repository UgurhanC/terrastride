import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import math
import skimage.filters as filters
from skimage import io, color


def decomposition(image_url):
    #Load Image
    image = cv2.imread(r"{url}".format(url = image_url))

    #Grayscale Image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    #Edge detect Image
    edges = cv2.Canny(image, 100, 200)

    #Color split
    blue, green, red = cv2.split(image)

    #Color Opponency
    red_green = red - green
    blue_yellow = blue - (red + green) / 2
    value = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:,:,-1]

    #Texture detection
    gabor_response, _ = filters.gabor(gray, frequency=0.6, theta=np.pi/4)

    #Saliency
    # Static Saliency Fine Grained
    saliency_detector_fine = cv2.saliency.StaticSaliencyFineGrained_create()
    
    # Compute the saliency map
    (success_fine, saliency_map_fine) = saliency_detector_fine.computeSaliency(image)
    
    # Normalize the saliency map
    saliency_map_fine = (saliency_map_fine * 255).astype("uint8")

    #Details and Motion: Parvocellular and Magnocellular pathways
    retina = cv2.bioinspired.Retina.create((image.shape[1], image.shape[0]))

    for i in range(20):
        retina.run(image)

    retinaOut_parvo = retina.getParvo()
    retinaOut_parvo = cv2.cvtColor(retinaOut_parvo, cv2.COLOR_BGR2RGB)
    retinaOut_magno = retina.getMagno()  
    

    return red_green, blue_yellow, value, gray, edges, gabor_response, saliency_map_fine, retinaOut_parvo, retinaOut_magno