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
# import matplotlib.pyplot as plt
from src.tx.enc.encode import *
from src.lib.supp.readfile_polar_rel_idx import *
from src.lib.supp.create_decoding_schedule import *
from src.lib.supp.llr_quantizer import *
from src.lib.supp.create_terminal_output import *
from src.lib.supp.timekeeper import *
# from scipy.stats import norm
# from scipy.special import erfc


'''Sim Initialization'''

# Set random seeds
np.random.seed(919) 
random.seed(918)

# Read the polar reliability index file
filepath_polar_rel_idx = "src/lib/ecc/polar/3gpp/n1024_3gpp.pc"
vec_polar_rel_idx  = readfile_polar_rel_idx(filepath_polar_rel_idx)

sim_snr_start   = 4
sim_snr_end     = 4
sim_snr_step    = 1
sim_num_frames  = 3000
sim_num_errors  = 50
sim_num_max_fr  = 1000000

sim_qbits_enable = 1
sim_qbits_chnl = 5
sim_qbits_intl = 6
sim_qbits_frac = 1

len_k           = 512
len_n           = len(vec_polar_rel_idx)
len_logn        = int(math.log2(len_n))

sim_snr_points = np.arange(sim_snr_start, sim_snr_end + sim_snr_step, sim_snr_step, dtype=float)
len_simpoints = len(sim_snr_points)

sim_frame_count = np.zeros(len_simpoints, dtype=int)
sim_bit_error   = np.zeros(len_simpoints, dtype=int)
sim_frame_error = np.zeros(len_simpoints, dtype=int)
sim_ber         = np.zeros(len_simpoints, dtype=float)
sim_bler        = np.zeros(len_simpoints, dtype=float)

batch_size = 1

vec_info    = np.zeros((batch_size,len_k), dtype=int)
vec_uncoded = np.zeros((batch_size,len_n), dtype=int)
vec_encoded = np.zeros((batch_size,len_n), dtype=int)
vec_mod     = np.zeros((batch_size,len_n), dtype=int)
vec_awgn    = np.zeros((batch_size,len_n), dtype=float)
vec_rx      = np.zeros((batch_size,len_n), dtype=float)
vec_llr     = np.zeros((batch_size,len_n), dtype=float)

quant_step       = 2 ** sim_qbits_frac
quant_chnl_upper = (2 ** (sim_qbits_chnl -1) - 1)/quant_step
quant_chnl_lower = (-(2 ** (sim_qbits_chnl -1)))//quant_step
quant_intl_upper = (2 ** (sim_qbits_intl -1) - 1)/quant_step
quant_intl_lower = (-(2 ** (sim_qbits_intl -1)))//quant_step

'''One-time preparation for the simulation'''

# Generate the polar frozen/info indicators
vec_polar_frozen = np.ones(len_n, dtype=int)
vec_polar_info = np.ones(len_n, dtype=int)

for num, index in enumerate(vec_polar_rel_idx[:len_k], start=0):
    vec_polar_frozen[index] = 0
for num, index in enumerate(vec_polar_rel_idx[len_k:], start=len_k):
    vec_polar_info[index] = 0 

vec_polar_info_indices = np.nonzero(vec_polar_info)[0]

# Generate the polar encoding matrix based on master code length
polar_enc_matrix_core = [[1, 0], [1, 1]]
polar_enc_matrix = polar_enc_matrix_core  # Core matrix as the initial value
for _ in range(len_logn-1):
    polar_enc_matrix = np.kron(polar_enc_matrix, polar_enc_matrix_core)

polar_enc_matrix = polar_enc_matrix[vec_polar_info_indices]

# Create the decoding schedule and helper variables to create a decoding instruction LUT
vec_dec_sch, vec_dec_sch_size, vec_dec_sch_dir = create_decoding_schedule(vec_polar_frozen, len_logn)


'''Begin simulation'''

print(generate_sim_header())
status_msg = []
prev_status_msg = []

for nsnr in range(0, len_simpoints):

  snr_linear = 10 ** (sim_snr_points[nsnr] / 10) 
  awgn_var = 1/snr_linear
  awgn_stdev = np.sqrt(awgn_var)

  time_start = time.time()

  while(sim_frame_count[nsnr] < sim_num_frames or sim_frame_error[nsnr] < sim_num_errors):# and sim_frame_count > sim_num_max_fr):
      
      vec_info = np.random.choice([0, 1], size=(batch_size, len_k))
      # vec_uncoded = np.zeros((batch_size, len_n), dtype=int)

      # for i in range(len_k):
      #   vec_uncoded[:, vec_polar_rel_idx[i]] = vec_info[:, i]

      vec_encode = polar_encode(vec_info, polar_enc_matrix)
      # vec_encode = polar_encode_fast(vec_uncoded)
      # vec_encoded = (vec_uncoded @ polar_enc_matrix  % 2) # Encode the uncoded vector
      vec_mod = 1-2*vec_encoded # Modulate the encoded vector

      # Transmit modulated frame through the channel, receive the noisy frame
      vec_awgn = np.random.normal(loc=0, scale=awgn_stdev, size=(batch_size, len_n)) # Generate noise
      vec_rx = vec_mod + vec_awgn                                      # Apply noise
      vec_llr = 2.0 * vec_rx / awgn_var                                # Get LLRs of the frame
      
      # print(f"before quantization: {vec_llr}")
      if(sim_qbits_enable):
        vec_llr = llr_quantizer(vec_llr, quant_step, quant_chnl_lower, quant_chnl_upper)
      
      # print(f"after quantization: {vec_llr}")

      # HARD DECISION AND COMPARE FOR THE TIME BEING (UNCODED SCENARIO)
      vec_decoded = np.where(vec_llr < 0, 1, 0)

      # print(f"NUMBER OF BIT ERRORS IS {sim_bit_error}")

      #Update frame and error counts
      sim_frame_count[nsnr] += batch_size
      sim_bit_error[nsnr] += np.sum(vec_decoded != vec_encoded)
      sim_frame_error[nsnr] += np.sum(np.any(vec_decoded != vec_encoded, axis=1))

      # sim_frame_error[nsnr] += int(np.any(sim_bit_error[nsnr] > 0))


      # print(f"{sim_frame_count}   {sim_bit_error}   {sim_frame_error}")

      if(sim_frame_count[nsnr] % 1000 == 0):
        time_end = time.time()
        time_elapsed = time_end - time_start
        status_msg = report_sim_stats(sim_snr_points[nsnr], sim_bit_error[nsnr], sim_frame_error[nsnr], sim_frame_count[nsnr], len_n, format_time(time_elapsed), 1, status_msg, prev_status_msg)
        prev_status_msg = status_msg
  
  time_end = time.time()
  time_elapsed = time_end - time_start
  status_msg = report_sim_stats(sim_snr_points[nsnr], sim_bit_error[nsnr], sim_frame_error[nsnr], sim_frame_count[nsnr], len_n, format_time(time_elapsed), 0, status_msg, prev_status_msg)
  prev_status_msg = status_msg

# Create a semilogy plot
# for i in range (0,len_simpoints):
#   sim_ber[i]  = sim_bit_error[i]/(sim_frame_count[i]*len_n)
#   sim_bler[i] = sim_frame_error[i]/sim_frame_count[i]
# plt.semilogy(sim_snr_points, sim_ber, 'b--', label='Bit Error')
# plt.semilogy(sim_snr_points, sim_bler, 'b-', label='Frame Error')
# plt.xlabel('SNR Points')
# plt.ylabel('Error Rate')
# plt.title('Bit Error and Frame Error vs SNR')
# plt.legend()
# plt.show()

'''End simulation'''

'''
TODO:
--> Insert input file
--> Insert the decoder
--> Speed up decoding (IN PROGRESS)
--> Insert readme file
--> Create option to log sim outputs to a file
--> Work on GUI
--> Multi-threading option
'''