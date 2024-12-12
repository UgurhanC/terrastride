
# Define Image Processes

import numpy as np
import cv2
from skimage.measure import shannon_entropy

def single_scale_retinex(image, sigma):
    log_image = np.log1p(image.astype(np.float32))
    blurred_image = cv2.GaussianBlur(image.astype(np.float32), (0, 0), sigma)
    log_blurred = np.log1p(blurred_image)
    return log_image - log_blurred

def multi_scale_retinex(image, sigmas=[10, 50, 100], gain = 1.0):
    retinex = np.zeros_like(image, dtype=np.float32)
    for sigma in sigmas:
        retinex += single_scale_retinex(image, sigma)
    retinex /= len(sigmas)
    # Adjust scaling here to avoid over-darkening
    retinex = np.clip(retinex * gain, -1, 1)
    retinex = np.expm1(retinex) * 255
    return retinex


### Metrics

def colorfulness(image):
    (B, G, R) = cv2.split(image.astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)
    std_rg, mean_rg = np.std(rg), np.mean(rg)
    std_yb, mean_yb = np.std(yb), np.mean(yb)
    return np.sqrt(std_rg**2 + std_yb**2) + 0.3 * np.sqrt(mean_rg**2 + mean_yb**2)

def contrast(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[-1]
    min_intensity = np.min(gray)
    max_intensity = np.max(gray)
    return (max_intensity - min_intensity) / (max_intensity + min_intensity)

def entropy(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return shannon_entropy(gray)

def luminance_stats(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_luminance = np.mean(gray)
    std_luminance = np.std(gray)
    return mean_luminance, std_luminance

def entropy(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return shannon_entropy(gray)

def sharpness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()