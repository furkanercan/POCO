"""
File: main.py
Author: Furkan Ercan
Date: January 6, 2024
Description: Main script to run SC decoding for Polar Codes

Usage:
  - python main.py

Requirements:
  - Python 3.11 or above

Notes:

License:
  This file is licensed under the MIT License.
  See the LICENSE file for details.
"""

import random
import numpy as np
import math
import time
# from src.tx.enc.encode import encode
from src.lib.supp.readfile_polar_rel_idx import *
from src.lib.supp.create_decoding_schedule import *
from src.lib.supp.llr_quantizer import *

'''Sim Initialization'''

# Set random seeds
np.random.seed(919) 
random.seed(918)

# Read the polar reliability index file
filepath_polar_rel_idx = "src/lib/ecc/polar/3gpp/n64_3gpp.pc"
vec_polar_rel_idx  = readfile_polar_rel_idx(filepath_polar_rel_idx)

sim_snr_start   = 1
sim_snr_end     = 4
sim_snr_step    = 0.5
sim_num_frames  = 1
sim_num_errors  = 1
sim_num_max_fr  = 1000000
sim_enable_quant = 1

sim_frame_count = 0
sim_frame_error = 0
sim_bit_error   = 0
len_k           = 32
len_n           = len(vec_polar_rel_idx)
len_logn        = int(math.log2(len_n))

sim_snr_points = np.arange(sim_snr_start, sim_snr_end + sim_snr_step, sim_snr_step, dtype=float)
len_simpoints = len(sim_snr_points)

print(f"len_simpoints {len_simpoints}")

# vec_ber
# vec_ser
# vec_bler
# vec_iter
vec_awgn = [0] * len_n
vec_rx = [0] * len_n
vec_llr = [0] * len_n

'''One-time preparation for the simulation'''



# Generate the polar frozen indicators
vec_polar_frozen = [1] * len_n
for num, index in enumerate(vec_polar_rel_idx[:len_k], start=0):
    vec_polar_frozen[index] = 0

# Generate the polar encoding matrix based on master code length
polar_enc_matrix_core = [[1, 0], [1, 1]]
polar_enc_matrix = polar_enc_matrix_core  # Core matrix as the initial value
for _ in range(len_logn-1):
    polar_enc_matrix = np.kron(polar_enc_matrix, polar_enc_matrix_core)

# Create the decoding schedule and helper variables to create a decoding instruction LUT
vec_dec_sch, vec_dec_sch_size, vec_dec_sch_dir = create_decoding_schedule(vec_polar_frozen, len_logn)


'''Begin simulation'''


for nsnr in range(1, len_simpoints):

  sim_frame_count = 0
  sim_frame_error = 0
  sim_bit_error   = 0

  awgn_mean = 0
  awgn_var = 1/np.power(10,sim_snr_points[nsnr]/10)
  awgn_stdev = np.sqrt(awgn_var)

  while(sim_frame_count < sim_num_frames or sim_frame_error < sim_num_errors):# and sim_frame_count > sim_num_max_fr):
      # Generate information bits, get vec_k
      vec_info = [random.choice([0,1]) for _ in range(len_k)]

      # Place the generated information bits into the codeword to be encoded
      vec_uncoded = [0]*len_n

      for i in range(len_k):
        vec_uncoded[vec_polar_rel_idx[i]] = vec_info[i]


      vec_encoded = (polar_enc_matrix @ vec_uncoded % 2) # Encode the uncoded vector
      vec_mod = 1-2*vec_encoded # Modulate the encoded vector

      # Transmit modulated frame through the channel, receive the noisy frame
      vec_awgn = np.random.normal(loc=awgn_mean, scale=awgn_stdev, size=len_n) # Generate noise
      vec_rx = vec_mod + vec_awgn                               # Apply noise
      vec_llr = 2.0 * vec_rx / awgn_var                         # Get LLRs of the frame
      
      # print(f"before quantization: {vec_llr}")

      if(sim_enable_quant):
        vec_llr = llr_quantizer(vec_llr, num_qbits=6, num_fbits=2)
      
      # print(f"after quantization: {vec_llr}")

      # HARD DECISION AND COMPARE FOR THE TIME BEING (UNCODED SCENARIO)
      vec_decoded = [1 if llr < 0 else 0 for llr in vec_llr]

      
      # print(f"NUMBER OF BIT ERRORS IS {sim_bit_error}")

      #Update frame and error counts
      sim_frame_count += 1
      sim_bit_error   += sum(1 for dec, unc in zip(vec_decoded, vec_uncoded) if dec != unc)
      sim_frame_error = sim_frame_error+1 if sim_bit_error > 0 else sim_frame_error

      if(sim_frame_count == 10000):
        print(f"Status: {sim_frame_count} frames, {sim_frame_error} errors, {sim_bit_error} bit errors")

# status_msg = "Hello and welcome to my simulation"
# print(status_msg, end='\r', flush=True)
# time.sleep(5)

# prev_status_msg = status_msg
# status_msg = "Today we will be simulating SC decoding"
# status_pad = ' ' * max(0, len(prev_status_msg) - len(status_msg))
# print(status_msg + status_pad, end='\r', flush=True)
# time.sleep(3)

# prev_status_msg = status_msg
# status_msg = "We start in 3..."
# status_pad = ' ' * max(0, len(prev_status_msg) - len(status_msg))
# print(status_msg + status_pad, end='\r', flush=True)
# time.sleep(1)

# prev_status_msg = status_msg
# status_msg = "We start in 2..."
# status_pad = ' ' * max(0, len(prev_status_msg) - len(status_msg))
# print(status_msg + status_pad, end='\r', flush=True)
# time.sleep(1)

# prev_status_msg = status_msg
# status_msg = "We start in 1..."
# status_pad = ' ' * max(0, len(prev_status_msg) - len(status_msg))
# print(status_msg + status_pad, end='\r', flush=True)
# time.sleep(1)

# prev_status_msg = status_msg
# status_msg = "GO!"
# status_pad = ' ' * max(0, len(prev_status_msg) - len(status_msg))
# print(status_msg + status_pad, end='\n', flush=True)

# Decode the frame (SC)


'''End simulation'''


# Compare the info bits, derive BER/FER

# Call the generate_binary_vector function
#vec_n = encode(len_n, len_k)

# Print the result
# print(f"Generated vector: {vec_n}")



# print(f"polar frozen indices are:")
# for num in vec_polar_frozen:
#     print(num, end=' ')
# print('\n')
