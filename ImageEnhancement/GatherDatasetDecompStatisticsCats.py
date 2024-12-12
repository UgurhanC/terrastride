
### The main point of this python file is to load images from both dataset, and use this to gather information on natural ranges
## of the decompositions seen in both datasets.

import numpy as np
import cv2
import os
from Decomposition import decomposition
from scipy import stats
from tqdm import tqdm

url_header = os.path.dirname(__file__)
Ex_cat_url = url_header + r"Data\NaturalImages\natural_images\cat\cat_0000.jpg"

Ex_lowlight_url = url_header + r"Data\LowLight\1.png"

#### Gather load images from natural light dataset for cat subset
cat_decomps_stats = [] #Will wind up a list of lists
#Order of decompositions is as follows:
# red_green, blue_yellow, value, gray, edges, gabor_response, saliency_map_fine, retinaOut_parvo, retinaOut_magno

# We don't need the decomposition images, we just need their statistics


for i in tqdm(range(885)):
    cat_numb = str(i).zfill(4)
    cat_url = url_header + rf"\Data\NaturalImages\natural_images\cat\cat_{cat_numb}.jpg"
    cat_image = cv2.imread(cat_url)
    cat_decomposition = decomposition(cat_image)
    current_cat_stats = []
    for j in range(len(cat_decomposition)):
        #Calculate mean, standard_deviation, variance, skewness, and kurtosis for each decomposition
        decomp_stats = []
        current_decomp = cat_decomposition[j].flatten()

        current_decomp_mean = np.mean(current_decomp)
        decomp_stats.append(current_decomp_mean)

        current_decomp_std = np.std(current_decomp)
        decomp_stats.append(current_decomp_std)

        current_decomp_var = current_decomp_std**2
        decomp_stats.append(current_decomp_var)

        current_decomp_skewness = stats.skew(current_decomp)
        decomp_stats.append(current_decomp_skewness)

        current_decomp_kurtosis = stats.kurtosis(current_decomp)
        decomp_stats.append(current_decomp_kurtosis)

        current_cat_stats.append(decomp_stats)
    
    cat_decomps_stats.append(current_cat_stats)
cat_decomps_stats = np.array(cat_decomps_stats)

## This process should grant us a 9x5x885 tensor where the last rank indicates the cat, the first rank indicates the rank,
## and the second rank indicates the statistic in the order [mean, std, var, skew, kurt]
print(cat_decomps_stats.shape)

#From here we want to figure out the average statistics for each decomposition over the data
cat_averaged_statistics = np.mean(cat_decomps_stats, axis = 0)
print(cat_averaged_statistics)

filename = "cat_averaged_decomposition_statistics.csv"

# Save to CSV
np.savetxt(filename, cat_averaged_statistics, delimiter=",", fmt="%.5f")

print(f"Data saved to {filename}")

