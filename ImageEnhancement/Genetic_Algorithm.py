import numpy as np
import cv2
from ImageProcesses import *
import random
from tqdm import tqdm
import os
from Decomposition import decomposition
from scipy import stats

url_header = os.path.dirname(__file__)
biomimetic_statistics = np.loadtxt(url_header + r"\cat_averaged_decomposition_statistics.csv", delimiter=',', dtype=None)




#Define hyperparameters and their ranges
#Potential to add more retinex sigmas if necessary, maybe also a parameter to control how many sigmas are used.
param_ranges = {
    "Saturation": (0,1.0), #Initial saturation adjustment
    "CLAHE_clipLimit_Value": (1.0, 5.0), #Value CLAHE clip limit
    "CLAHE_clipLimit_BGR": (1.0, 5.0), #BGR CLAHE clip limit
    "Retinex_gain": (1.0, 3.0), #Retinex gain
    "Retinex_sigma1": (5,20),
    "Retinex_sigma2": (30,100),
    "Retinex_sigma3": (100, 250),
    "Blend_ratio": (0.0, 1.0),
    "gamma": (1.0, 1.5), #Gamma correction
    "brightness_boost": (20,40) #Brightness boost
    
}

def single_scale_retniex(image,sigma):
    log_image = np.log1p(image.astype(np.float32))
    blurred_image = cv2.GaussianBlur(image.astype(np.float32), (0,0), sigma)
    log_blurred = np.log1p(blurred_image)
    return log_image - log_blurred

def multi_scale_retinex(image, sigmas=[10, 50, 100], gain = 1.0):
    retinex = np.zeros_like(image, dtype=np.float32)
    for sigma in sigmas:
        retinex += single_scale_retinex(image, sigma)
    retinex /= len(sigmas)

    #Adjust scaling here to avoid over-darkening
    retinex = np.clip(retinex * gain, -1, 1)
    retinex = np.expm1(retinex) * 255
    return retinex

#Fitness function to evaluate the "naturalness" of an enhanced image
def fitness_function(params, original_image):
    #Apply image enhancement with params
    enhanced_image = apply_image_enhancement(original_image, params)

    #Calculate metrics for fitness evaluation (e.g., NIQE, sharpness, etc.)
    colorfulness_score = colorfulness(enhanced_image)
    sharpness_score = sharpness(enhanced_image)
    contrast_score = contrast(enhanced_image)
    entropy_score = entropy(enhanced_image)

    #Define target ranges for each metric (customizable)
    target_colorfulness = 30
    target_sharpness = 250
    target_contrast = 0.4
    target_entropy = 6


    #contrast_norm = (contrast_score - 0.2) / (0.8 - 0.2)
    contrast_norm = contrast_score
    colorfulness_norm = (colorfulness_score - 10) / (50 - 10)
    sharpness_norm = (sharpness_score - 100) / (1000 - 100)
    entropy_norm = (entropy_score - 5) / (7.5 - 5)

    #target_contrast_norm = (target_contrast - 0.2) / (0.8 - 0.2)
    target_contrast_norm = target_contrast
    target_colorfulness_norm = (target_colorfulness - 10) / (50 - 10)
    target_sharpness_norm = (target_sharpness - 100) / (1000 - 100)
    target_entropy_norm = (target_entropy - 5) / (7.5 - 5)


    #Calculate fitness score based on deviations from target values
    # maybe it would make more sense to replace with means squared instead of abs
    fitness = (
        abs(colorfulness_norm - target_colorfulness_norm) +
        abs(sharpness_norm - target_sharpness_norm) +
        abs(contrast_norm - target_contrast_norm) +
        abs(entropy_norm - target_entropy_norm)
    )

    original_image_decomp = decomposition(original_image)
    decomp_stats = []
    for j in range(len(original_image_decomp)):
        #Calculate mean, standard_deviation, variance, skewness, and kurtosis for each decomposition
        current_decomp = original_image_decomp[j].flatten()
        current_decomp_stats = []

        current_decomp_mean = np.mean(current_decomp)
        current_decomp_stats.append(current_decomp_mean)

        current_decomp_std = np.std(current_decomp)
        current_decomp_stats.append(current_decomp_std)

        current_decomp_var = current_decomp_std**2
        current_decomp_stats.append(current_decomp_var)

        current_decomp_skewness = stats.skew(current_decomp)
        current_decomp_stats.append(current_decomp_skewness)

        current_decomp_kurtosis = stats.kurtosis(current_decomp)
        current_decomp_stats.append(current_decomp_kurtosis)

        decomp_stats.append(current_decomp_stats)

    #Incoporate biomimetic statistics
    for i in range(biomimetic_statistics.shape[0]):
        for j in range(biomimetic_statistics.shape[1]):
           fitness += abs(decomp_stats[i][j] - biomimetic_statistics[i][j])
    
    return fitness


#Function to apply the enhancement algorithm with given hyperparameters
def apply_image_enhancement(image, params):
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

# Initialize population
def initialize_population(size):
    population = []
    for _ in range(size):
        individual = {key: random.uniform(*value) for key, value in param_ranges.items()}
        population.append(individual)
    return population

# Selection (select the top individuals based on fitness)
def selection(population, fitness_scores, num_parents):
    selected_parents = [population[i] for i in np.argsort(fitness_scores)[:num_parents]]
    return selected_parents

#Crossover (combine two parents to create an offspring)
def crossover(parent1, parent2):
    child = {}
    for key in parent1.keys():
        child[key] = parent1[key] if random.random() < 0.5 else parent2[key]
    return child

# Mutation (randomly change a parameter within its range)
def mutate(individual, mutation_rate=0.1):
    for key in individual.keys():
        if random.random() < mutation_rate:
            individual[key] = random.uniform(*param_ranges[key])
    return individual

#Main genetic algorithm
def genetic_algorithm(image, population_size=20, generations=10, num_parents=10, mutation_rate = 0.1):
    population = initialize_population(population_size)

    for generation in tqdm(range(generations)):
        #Evaluate fitness of each individual
        fitness_scores = [fitness_function(ind, image) for ind in population]

        #Selection: Select top individuals to be parents
        parents = selection(population, fitness_scores, num_parents)

        # Generate next generation
        new_population = []
        while len(new_population) < population_size:
            #Crossover
            parent1, parent2 = random.sample(parents,2)
            child = crossover(parent1, parent2)
            #Mutation
            child = mutate(child, mutation_rate)
            new_population.append(child)

        population = new_population

        #Print the best scores of the current generation
        best_score = min(fitness_scores)
        print(f"Generation {generation +1}: Best Fitness Score = {best_score}")

    # Return the best solution
    best_individual = population[np.argmin(fitness_scores)]
    return best_individual

if __name__ == "__main__":
    #Load original image
    no = 18
    url_header = os.path.dirname(__file__)
    original_image = cv2.imread(rf"{url_header}\Data\LowLight\{no}.png")

    population_size=20
    generations=10
    num_parents=10
    mutation_rate = 0.1

    #Run genetic algorithm
    best_params = genetic_algorithm(original_image, population_size, generations, num_parents, mutation_rate)
    print("Best Hyperparameters:", best_params)

    import json
    with open('best_params.json', 'w', encoding='utf-8') as f:
        json.dump(best_params, f, ensure_ascii=False, indent=4)