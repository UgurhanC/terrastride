import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
from ImageEnhancement.ImageProcesses import *
#Function to apply the enhancement algorithm with given hyperparameters
def apply_image_enhancement(image, params):

    #print("Amogus")
    #print(image.shape)
    #print(params.items())
    ### Step 1: Dual-Channel Light Amplification in HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    s = (s*params["Saturation"]).astype(np.uint8)

    #Apply CLAHE to the VAlue channel with controlled limits
    #print(params["CLAHE_clipLimit_Value"])
    clahe = cv2.createCLAHE(clipLimit = params["CLAHE_clipLimit_Value"], tileGridSize=(8, 8)) #Adjusted clipLimit
    v_clahe = clahe.apply(v)

    # Merge back the channels and convert to BGR
    hsv_amplified = cv2.merge([h, s, v_clahe])
    amplified_image = cv2.cvtColor(hsv_amplified, cv2.COLOR_HSV2BGR)

    ### Step 2: Color Contrast Enhancement with CLAHE on Each Channel
    #Split the amplified image into BGR channels
    b, g, r = cv2.split(amplified_image)

    # Apply CLAHE to each channel with a controlled clip limit
    clahe = cv2.createCLAHE(clipLimit = params["CLAHE_clipLimit_BGR"], tileGridSize=(8, 8))
    b_clahe = clahe.apply(b)
    g_clahe = clahe.apply(g)
    r_clahe = clahe.apply(r)

    # Merge enhanced channels back
    contrast_enhanced_image = cv2.merge([b_clahe, g_clahe, r_clahe])

    ### Step 3: Multi-Scale Retinex for Signal Integration
    #Make sure the retinex functions are defined
    # Apply multi-scale retinex on each channel separately
    retinex_b = multi_scale_retinex(b_clahe, sigmas = [params["Retinex_sigma1"], params["Retinex_sigma2"], params["Retinex_sigma3"]], gain = params["Retinex_gain"])
    retinex_g = multi_scale_retinex(g_clahe, sigmas = [params["Retinex_sigma1"], params["Retinex_sigma2"], params["Retinex_sigma3"]], gain = params["Retinex_gain"])
    retinex_r = multi_scale_retinex(r_clahe, sigmas = [params["Retinex_sigma1"], params["Retinex_sigma2"], params["Retinex_sigma3"]], gain = params["Retinex_gain"])

    #Stack channels back together and clip values to the valid range
    retinex_image = cv2.merge([retinex_b, retinex_g, retinex_r])
    retinex_image = np.clip(retinex_image, 0, 255).astype(np.uint8)

    ### Step 4: Noise Reduction with Edge Preservation
    # Apply bilateral filter for noise reduction with edge preservation
    denoised_image = cv2.bilateralFilter(retinex_image, d=9, sigmaColor=10, sigmaSpace=10) #Potentially three more hyperparameters

    ### Step 5: Blend the Amplified and Original Image for a Natural Look
    alpha = params["Blend_ratio"] # Blend ratio; adjust for stronger or weaker enhancement
    final_image = cv2.addWeighted(denoised_image, alpha, image, 1-alpha, 0)

    final_image = cv2.bilateralFilter(final_image, d=5, sigmaColor=10, sigmaSpace=10)

    def adjust_gamma(image, gamma=1.2):
        invGamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** invGamma * 255 for i in np.arange(0,256)]).astype("uint8")
        return cv2.LUT(image, table)

    #Apply gamma correction to final image
    final_image = adjust_gamma(final_image, gamma = params["gamma"])
    
    #Increase brightness by adding a fixed value
    brightness_boost = params["brightness_boost"] #Adjust from between 20-40
    enhanced_image = cv2.convertScaleAbs(final_image, alpha=1, beta=brightness_boost)

    return enhanced_image