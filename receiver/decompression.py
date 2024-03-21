# import json
# import pywt
# import numpy as np
# import scipy.signal as signal
# import matplotlib.pyplot as plt
# import json
# import zlib

# # Load the compressed data from the JSON file
# compressed_file_path = "compressed_data.json"

# with open(compressed_file_path, 'r') as file:
#     compressed_ascii = json.load(file)

# print("Length of compressed data:", len(compressed_ascii))

# # Convert compressed ASCII back to bytes
# compressed_data = compressed_ascii.encode('latin-1')

# # Decompress the compressed data
# decompressed_data = zlib.decompress(compressed_data)

# # Decode the decompressed bytes back to JSON string
# data_json_decompressed = decompressed_data.decode('utf-8')

# print("Length of decompressed data_json:", len(data_json_decompressed))

# # Convert JSON string back to Python dictionary
# data_decompressed = json.loads(data_json_decompressed)




# # Retrieve the compressed data
# comp_cA_ind = np.array(data_decompressed['comp_cA_ind'])
# comp_cA_val = np.array(data_decompressed['comp_cA_val'])
# row,col = data_decompressed['cA_thresholded_shape']
# Zxx_shape = data_decompressed['Zxx_shape']


# cA_thresholded_vec_rec =np.zeros(row*col)
# cA_thresholded_vec_rec[comp_cA_ind]=comp_cA_val
# cA_thresholded_mat_rec=np.reshape(cA_thresholded_vec_rec,(row,col))


# # coeffs_thresholded = (cA_thresholded, (cH_thresholded, cV_thresholded, cD_thresholded))
# cH_zero = np.zeros((row,col))
# cV_zero = np.zeros((row,col))
# cD_zero = np.zeros((row,col))
# cA_zero = np.zeros((row,col))

# # Reconstructed coefficients
# coeffs_thresholded = (cA_thresholded_mat_rec, (cH_zero, cV_zero, cD_zero))

# Zxx_compressed = pywt.idwt2(coeffs_thresholded, 'bior1.3')


# duration=1
# re_fs = 3200
# temp_data=np.ones(int(re_fs*duration))


# ff, tt, temp_fft = signal.stft(temp_data, fs=3200, nperseg=512)
# # Get time and frequency grids
# T, F = np.meshgrid(tt, ff)

# Zxx_compressed_resized = Zxx_compressed[:Zxx_shape[0], :Zxx_shape[1]]

# # Plot the compressed STFT
# plt.figure(figsize=(10, 5))
# plt.pcolormesh(T, F, np.abs(Zxx_compressed_resized), shading='gouraud')
# plt.title('Reconstructed Signal from Compressed Coefficients')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.colorbar()
# plt.tight_layout()
# plt.show()


import zlib
import json
import numpy as np
from scipy import signal
import pywt

def process_compressed_data(data):
    # Convert compressed ASCII back to bytes
    compressed_data = data.encode('latin-1')

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

    cA_thresholded_vec_rec = np.zeros(row * col)
    cA_thresholded_vec_rec[comp_cA_ind] = comp_cA_val
    cA_thresholded_mat_rec = np.reshape(cA_thresholded_vec_rec, (row, col))

    # Construct zero arrays for other coefficients
    cH_zero = np.zeros((row, col))
    cV_zero = np.zeros((row, col))
    cD_zero = np.zeros((row, col))
    cA_zero = np.zeros((row, col))

    # Reconstruct coefficients
    coeffs_thresholded = (cA_thresholded_mat_rec, (cH_zero, cV_zero, cD_zero))

    # Perform inverse discrete wavelet transform
    Zxx_compressed = pywt.idwt2(coeffs_thresholded, 'bior1.3')

    # Define parameters for signal generation
    duration = 1
    re_fs = 3200
    temp_data = np.ones(int(re_fs * duration))

    # Perform Short-Time Fourier Transform (STFT)
    ff, tt, temp_fft = signal.stft(temp_data, fs=3200, nperseg=512)

    # Get time and frequency grids
    T, F = np.meshgrid(tt, ff)

    # Resize the decompressed data to match Zxx_shape
    Zxx_compressed_resized = Zxx_compressed[:Zxx_shape[0], :Zxx_shape[1]]

    return T, F, Zxx_compressed_resized

# Usage example:
# T, F, Zxx_compressed_resized = process_compressed_data(unescaped_data)
