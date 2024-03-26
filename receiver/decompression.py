import json
import pywt
import numpy as np
import scipy.signal as signal
import json
import zlib

def process_compressed_data():
    # Load the compressed data from the JSON file
    compressed_file_path = "compressed_data.json"

    with open(compressed_file_path, 'r') as file:
        compressed_ascii = json.load(file)

    # print("Length of compressed data:", len(compressed_ascii))
    print(compressed_ascii)
    # Convert compressed ASCII back to bytes
    compressed_data = compressed_ascii.encode('latin-1')

    print("Compress data", compressed_data)
    # Decompress the compressed data
    decompressed_data = zlib.decompress(compressed_data)

    # Decode the decompressed bytes back to JSON string
    data_json_decompressed = decompressed_data.decode('utf-8')

    print("Length of decompressed data_json:", len(data_json_decompressed))

    # Convert JSON string back to Python dictionary
    data_decompressed = json.loads(data_json_decompressed)


    # Retrieve the compressed data
    comp_cA_ind = np.array(data_decompressed['comp_cA_ind'])
    comp_cA_val = np.array(data_decompressed['comp_cA_val'])
    row, col = data_decompressed['cA_thresholded_shape']
    Zxx_shape = data_decompressed['Zxx_shape']


    cA_thresholded_vec_rec = np.zeros(row*col)
    cA_thresholded_vec_rec[comp_cA_ind] = comp_cA_val
    cA_thresholded_mat_rec = np.reshape(cA_thresholded_vec_rec, (row, col))


    # coeffs_thresholded = (cA_thresholded, (cH_thresholded, cV_thresholded, cD_thresholded))
    cH_zero = np.zeros((row, col))
    cV_zero = np.zeros((row, col))
    cD_zero = np.zeros((row, col))
    cA_zero = np.zeros((row, col))

    # Reconstructed coefficients
    coeffs_thresholded = (cA_thresholded_mat_rec, (cH_zero, cV_zero, cD_zero))

    Zxx_compressed = pywt.idwt2(coeffs_thresholded, 'bior1.3')


    duration = 1
    re_fs = 3200
    temp_data = np.ones(int(re_fs*duration))


    ff, tt, temp_fft = signal.stft(temp_data, fs=3200, nperseg=512)
    # Get time and frequency grids
    T, F = np.meshgrid(tt, ff)

    Zxx_compressed_resized = Zxx_compressed[:Zxx_shape[0], :Zxx_shape[1]]
    
    # Calculate magnitude of Zxx_compressed
    magnitude_Zxx = np.abs(Zxx_compressed_resized)

    # Convert magnitude to decibels (dB)
    epsilon = 1e-10
    Zxx_dB = 20 * np.log10(magnitude_Zxx + epsilon) +208 -26

    return T, F, Zxx_dB
