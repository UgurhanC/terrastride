### Now repeat for Low Light Dataset
import numpy as np
import cv2
import os
from Decomposition import decomposition
from scipy import stats
from tqdm import tqdm

url_header = os.path.dirname(__file__)
Ex_lowlight_url = url_header + r"\Data\LowLight\1.png"

lowlight_decomps_stats = [] #Will wind up a list of lists
#Order of decompositions is as follows:
# red_green, blue_yellow, value, gray, edges, gabor_response, saliency_map_fine, retinaOut_parvo, retinaOut_magno

# We don't need the decomposition images, we just need their statistics

#Running this algorithm on all 6000 images in the lowlight dataset would take 6 hours. Instead let's run it on a random selection of 300 images

for i in tqdm(np.random.randint(1,6000,size=300)):
    lowlight_numb = str(i+1)
    lowlight_url = url_header + rf"\Data\LowLight\{lowlight_numb}.png"
    lowlight_image = cv2.imread(lowlight_url)
    lowlight_decomposition = decomposition(lowlight_image)
    current_lowlight_stats = []
    for j in range(len(lowlight_decomposition)):
        #Calculate mean, standard_deviation, variance, skewness, and kurtosis for each decomposition
        decomp_stats = []
        current_decomp = lowlight_decomposition[j].flatten()

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

        current_lowlight_stats.append(decomp_stats)
    
    lowlight_decomps_stats.append(current_lowlight_stats)
lowlight_decomps_stats = np.array(lowlight_decomps_stats)

## This process should grant us a 9x5x885 tensor where the last rank indicates the cat, the first rank indicates the rank,
## and the second rank indicates the statistic in the order [mean, std, var, skew, kurt]
print(lowlight_decomps_stats.shape)

#From here we want to figure out the average statistics for each decomposition over the data
lowlight_averaged_statistics = np.mean(lowlight_decomps_stats, axis = 0)
print(lowlight_averaged_statistics)

filename = "lowlight_averaged_decomposition_statistics.csv"

# Save to CSV
np.savetxt(filename, lowlight_averaged_statistics, delimiter=",", fmt="%.5f")

print(f"Data saved to {filename}")

