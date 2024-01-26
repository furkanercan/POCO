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

import numpy as np
import math
import time
import json
import matplotlib.pyplot as plt
from src.tx.enc.encode import *
from src.rx.dec.sc import *
from src.rx.dec.fast_ssc import *
from src.lib.supp.modules import *
from src.lib.supp.readfile_polar_rel_idx import *
from src.lib.supp.create_decoding_schedule import *
from src.lib.supp.llr_quantizer import *
from src.lib.supp.create_terminal_output import *
from src.lib.supp.timekeeper import *

'''Sim initialization'''

np.random.seed(1564) # Set random seeds

with open('config.json', 'r') as f:
    config_params = json.load(f) # Read external configuration parameters

sim = create_sim_from_config(config_params)
sim.snr_points  = np.arange(sim.snr_start, sim.snr_end + sim.snr_step, sim.snr_step, dtype=float)

# Read the polar reliability index file
vec_polar_rel_idx  = readfile_polar_rel_idx(sim.filepath_polar_rel_idx)

batch_size      = 1
len_k           = sim.len_k
len_n           = len(vec_polar_rel_idx)
len_logn        = int(math.log2(len_n))
len_simpoints   = len(sim.snr_points)

sim.frame_count = np.zeros(len_simpoints, dtype=int)
sim.bit_error   = np.zeros(len_simpoints, dtype=int)
sim.frame_error = np.zeros(len_simpoints, dtype=int)
sim.ber         = np.zeros(len_simpoints, dtype=float)
sim.bler        = np.zeros(len_simpoints, dtype=float)

vec_info    = np.zeros((batch_size,len_k), dtype=int)
vec_encoded = np.zeros((batch_size,len_n), dtype=int)
vec_mod     = np.zeros((batch_size,len_n), dtype=int)
vec_awgn    = np.zeros((batch_size,len_n), dtype=float)
vec_llr     = np.zeros((batch_size,len_n), dtype=float)
vec_decoded = np.zeros((batch_size,len_k), dtype=int)

quant_step       = 2 ** sim.qbits_frac
quant_chnl_upper = (2 ** (sim.qbits_chnl -1) - 1)/quant_step
quant_chnl_lower = (-(2 ** (sim.qbits_chnl -1)))//quant_step
quant_intl_max = (2 ** (sim.qbits_intl -1) - 1)/quant_step
quant_intl_min = (-(2 ** (sim.qbits_intl -1)))//quant_step

'''One-time preparation for the simulation'''

# Generate the polar frozen/info indicators
vec_polar_info_indices, vec_polar_isfrozen = create_polar_indices(len_n, len_k, vec_polar_rel_idx)

# Generate the polar encoding matrix based on master code length
polar_enc_matrix_full, polar_enc_matrix = create_polar_enc_matrix(len_logn, vec_polar_info_indices)

# Create the decoding schedule and helper variables to create a decoding instruction LUT
vec_dec_sch, vec_dec_sch_size, vec_dec_sch_depth, vec_dec_sch_dir = create_decoding_schedule(vec_polar_isfrozen, len_logn)

with open('instr.txt', 'w') as file:
    for item1, item2, item3 in zip(vec_dec_sch, vec_dec_sch_depth, vec_dec_sch_dir):
        print(item1, item2, item3, file=file)

# Decoder-related vectors
mem_alpha =  [np.zeros((batch_size, 2**i)) for i in range(len_logn + 1)]
mem_beta_l = [np.zeros((batch_size, 2**i)) for i in range(len_logn + 1)]
mem_beta_r = [np.zeros((batch_size, 2**i)) for i in range(len_logn + 1)]

'''Begin simulation'''

print(generate_sim_header())
status_msg, prev_status_msg = [], []

for nsnr in range(0, len_simpoints):

  time_start = time.time()
  snr_linear = 10 ** (sim.snr_points[nsnr] / 10) 
  awgn_var = 1/snr_linear
  awgn_stdev = np.sqrt(awgn_var)

  while(sim.frame_count[nsnr] < sim.num_frames or sim.frame_error[nsnr] < sim.num_errors):# and sim_frame_count > sim_num_max_fr):
      
      vec_info = np.random.choice([0, 1], size=(batch_size, len_k))                  # Generate information
      vec_encoded = polar_encode(vec_info, polar_enc_matrix)                          # Encode information
      vec_mod = 1-2*vec_encoded                                                      # Apply BPSK modulation
      vec_awgn = np.random.normal(loc=0, scale=awgn_stdev, size=(batch_size, len_n)) # Generate noise
      vec_llr = 2 * (vec_mod + vec_awgn) / awgn_var                                  # Apply noise, obtain LLRs
      
      if(sim.qbits_enable):
        vec_llr = llr_quantizer(vec_llr, quant_step, quant_chnl_lower, quant_chnl_upper)

      mem_alpha[len_logn][:] = vec_llr
      # dec_sc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta_l, mem_beta_r, \
      #        vec_dec_sch_size,  vec_dec_sch_dir, vec_dec_sch_depth, vec_polar_isfrozen, \
      #        sim.qbits_enable, quant_intl_max, quant_intl_min)
      dec_fastssc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta_l, mem_beta_r, \
                  vec_dec_sch_size, vec_dec_sch_dir, vec_dec_sch_depth, vec_polar_isfrozen, \
                  sim.qbits_enable, quant_intl_max, quant_intl_min)
      vec_decoded = (mem_beta_l[len_logn] @ polar_enc_matrix_full  % 2)
      vec_decoded = vec_decoded[:,vec_polar_info_indices]

      #Update frame and error counts
      sim.frame_count[nsnr] += batch_size
      sim.bit_error[nsnr] += np.sum(vec_decoded != vec_info)
      sim.frame_error[nsnr] += np.sum(np.any(vec_decoded != vec_info, axis=1))

      if(sim.frame_count[nsnr] % 100 == 0):
        time_end = time.time()
        time_elapsed = time_end - time_start
        status_msg = report_sim_stats(sim.snr_points[nsnr], sim.bit_error[nsnr], sim.frame_error[nsnr], sim.frame_count[nsnr], len_k, format_time(time_elapsed), 1, status_msg, prev_status_msg)
        prev_status_msg = status_msg
  
  time_end = time.time()
  time_elapsed = time_end - time_start
  status_msg = report_sim_stats(sim.snr_points[nsnr], sim.bit_error[nsnr], sim.frame_error[nsnr], sim.frame_count[nsnr], len_k, format_time(time_elapsed), 0, status_msg, prev_status_msg)
  prev_status_msg = status_msg

if(sim.plot_enable):
    # Calculate BER/BLER and present in a semilogy plot
    sim.ber = np.divide(sim.bit_error, sim.frame_count * len_k)
    sim.bler = np.divide(sim.frame_error, sim.frame_count)
    plt.semilogy(sim.snr_points, sim.ber, 'b--', label='BER')
    plt.semilogy(sim.snr_points, sim.bler, 'b-', label='BLER')
    plt.xlabel('SNR (dB)')
    plt.ylabel('BER/BLER')
    plt.title('Error Correction Performance')
    plt.legend()
    plt.show()

'''End simulation'''

'''
TODO:
--> Insert fast nodes
--> Insert fast track: No bit flips, no decoding
--> Fast node parameters (currently fixed to values) to config file
--> Insert readme file
--> Structure input file
--> Create more stucts for parameters for portability
--> Create option to log sim outputs to a file
--> Work on GUI
--> Multi-threading option
--> Add information content on GUI, videos pictures, etc.
--> Assign ID to the run, save to database?
'''