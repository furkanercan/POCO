"""
File: sim.py
Author: Furkan Ercan
Date: January 6, 2024
Description: Main script to run SC decoding for Polar Codes

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
from . import CONFIG

class Simulation:
    def __init__(self):
        # Access configuration using CONFIG
        code_config             = CONFIG.get('code', {})
        self.file_polar         = code_config.get('polar_file', "src/lib/ecc/polar/3gpp/n1024_3gpp.pc")
        self.vec_polar_rel_idx  = readfile_polar_rel_idx(self.file_polar)
        self.len_n              = len(self.vec_polar_rel_idx)
        self.len_k              = code_config.get('info_bit_length', 512)
        self.len_logn           = int(math.log2(self.len_n))
        
        snr_config              = CONFIG.get('snr', {})
        self.snr_start          = snr_config.get('start', 1)
        self.snr_end            = snr_config.get('end', 2)
        self.snr_step           = snr_config.get('step', 1)
        self.snr_points         = np.arange(self.snr_start, self.snr_end + self.snr_step, self.snr_step, dtype=float)
        self.len_simpoints      = len(self.snr_points)
        
        sim_config              = CONFIG.get('sim', {})
        self.num_frames         = sim_config.get('num_frames', 10000)
        self.num_errors         = sim_config.get('num_errors', 50)
        self.num_max_fr         = sim_config.get('num_max_fr', 1000000)
        
        quant_config            = CONFIG.get('quant', {})
        self.qbits_enable       = quant_config.get('enable', 0)
        self.qbits_chnl         = quant_config.get('bits_chnl', 5)
        self.qbits_intl         = quant_config.get('bits_intl', 6)
        self.qbits_frac         = quant_config.get('bits_frac', 1)
        self.quant_step         =    2 **  self.qbits_frac
        self.quant_chnl_upper   = (  2 ** (self.qbits_chnl -1) - 1)/self.quant_step
        self.quant_chnl_lower   = (-(2 ** (self.qbits_chnl -1)))//  self.quant_step
        self.quant_intl_max     = (  2 ** (self.qbits_intl -1) - 1)/self.quant_step
        self.quant_intl_min     = (-(2 ** (self.qbits_intl -1)))//  self.quant_step
        
        save_config             = CONFIG.get('plot_save', {})
        self.plot_enable        = save_config.get('plot_enable', 1)
        self.lutsim_enable      = save_config.get('lutsim_enable', 0)
        self.save_output        = save_config.get('save_output', 1)
        self.path_output        = f"SC_{os.path.splitext(os.path.basename(self.file_polar))[0]}_k{self.len_k}.out"
        self.path_fig_output    = f"SC_{os.path.splitext(os.path.basename(self.file_polar))[0]}_k{self.len_k}.png"
        
        fast_enable_config = CONFIG.get('fast_enable', {})
        self.en_r0         = fast_enable_config.get('r0', 1)
        self.en_r1         = fast_enable_config.get('r1', 1)
        self.en_rep        = fast_enable_config.get('rep', 1)
        self.en_spc        = fast_enable_config.get('spc', 1)
        self.en_0011       = fast_enable_config.get('0011', 1)
        self.en_0101       = fast_enable_config.get('0101', 1)
        
        fast_max_size_config = CONFIG.get('fast_max_size', {})
        self.r0_size         = fast_max_size_config.get('r0', 1024)
        self.r1_size         = fast_max_size_config.get('r1', 1024)
        self.rep_size        = fast_max_size_config.get('rep', 1024)
        self.spc_size        = fast_max_size_config.get('spc', 1024)

        self.frame_count        = np.zeros(len(self.snr_points), dtype=int)
        self.bit_error          = np.zeros(len(self.snr_points), dtype=int)
        self.frame_error        = np.zeros(len(self.snr_points), dtype=int)
        self.ber                = np.zeros(len(self.snr_points), dtype=float)
        self.bler               = np.zeros(len(self.snr_points), dtype=float)

    def run_simulation(self):
        
        np.random.seed(1564) # Set random seeds

        batch_size      = 100
        
        vec_info    = np.zeros((batch_size,self.len_k), dtype=int)
        vec_encoded = np.zeros((batch_size,self.len_n), dtype=int)
        vec_mod     = np.zeros((batch_size,self.len_n), dtype=int)
        vec_awgn    = np.zeros((batch_size,self.len_n), dtype=float)
        vec_comp    = np.zeros((batch_size,self.len_n), dtype=float)
        vec_llr     = np.zeros((batch_size,self.len_n), dtype=float)
        vec_decoded = np.zeros((batch_size,self.len_k), dtype=int)

        flag_bypass_decoder = 0
        '''One-time preparation for the simulation'''

        # Generate the polar frozen/info indicators
        vec_polar_info_indices, vec_polar_isfrozen = create_polar_indices(self.len_n, self.len_k, self.vec_polar_rel_idx)

        # Generate the polar encoding matrix based on master code length
        polar_enc_matrix_full, polar_enc_matrix = create_polar_enc_matrix(self.len_logn, vec_polar_info_indices)

        # Create the decoding schedule and helper variables to create a decoding instruction LUT
        vec_dec_sch, vec_dec_sch_size, vec_dec_sch_depth, vec_dec_sch_dir = create_decoding_schedule(self, vec_polar_isfrozen)

        with open('sc.instr', 'w') as file:
            for item1, item2, item3 in zip(vec_dec_sch, vec_dec_sch_depth, vec_dec_sch_dir):
                print(item1, item2, item3, file=file)

        # Decoder-related vectors
        mem_alpha =  [np.zeros((batch_size, 2**i)) for i in range(self.len_logn + 1)]
        mem_beta_l = [np.zeros((batch_size, 2**i)) for i in range(self.len_logn + 1)]
        mem_beta_r = [np.zeros((batch_size, 2**i)) for i in range(self.len_logn + 1)]

        '''Begin simulation'''

        print(generate_sim_header(self))
        status_msg, prev_status_msg = [], []

        for nsnr in range(0, self.len_simpoints):

            time_start = time.time()
            snr_linear = 10 ** (self.snr_points[nsnr] / 10) 
            awgn_var = 1/snr_linear
            awgn_stdev = np.sqrt(awgn_var)

            while(self.frame_count[nsnr] < self.num_frames or self.frame_error[nsnr] < self.num_errors):# and sim_frame_count > sim_num_max_fr):
            
                flag_bypass_decoder = 0
                vec_info = np.random.choice([0, 1], size=(batch_size, self.len_k))                  # Generate information
                vec_encoded = polar_encode(vec_info, polar_enc_matrix)                          # Encode information
                vec_mod = 1-2*vec_encoded                                                      # Apply BPSK modulation
                vec_awgn = np.random.normal(loc=0, scale=awgn_stdev, size=(batch_size, self.len_n)) # Generate noise
                vec_llr = 2 * (vec_mod + vec_awgn) / awgn_var                                  # Apply noise, obtain LLRs
                
                if(self.qbits_enable):
                    llr_quantizer(vec_llr, self.quant_step, self.quant_chnl_lower, self.quant_chnl_upper)

                mem_alpha[self.len_logn][:] = vec_llr
                if(self.lutsim_enable):
                    vec_comp = np.logical_and(vec_mod * vec_awgn < 0, np.abs(vec_awgn) > np.abs(vec_mod))
                    flag_bypass_decoder = not np.any(vec_comp)

                if not flag_bypass_decoder:
                    dec_fastssc(vec_dec_sch, mem_alpha, mem_beta_l, mem_beta_r, \
                                vec_dec_sch_size, vec_dec_sch_dir, vec_dec_sch_depth, \
                                self.qbits_enable, self.quant_intl_max, self.quant_intl_min)
                    vec_decoded = (mem_beta_l[self.len_logn] @ polar_enc_matrix_full  % 2)
                    vec_decoded = vec_decoded[:,vec_polar_info_indices]

                #Update frame and error counts
                self.frame_count[nsnr] += batch_size
                if not flag_bypass_decoder:
                    self.bit_error[nsnr] += np.sum(vec_decoded != vec_info)
                    self.frame_error[nsnr] += np.sum(np.any(vec_decoded != vec_info, axis=1))

                if(self.frame_count[nsnr] % 100 == 0):
                    time_end = time.time()
                    time_elapsed = time_end - time_start
                    status_msg = report_sim_stats(self, nsnr, format_time(time_elapsed), 1, status_msg, prev_status_msg)
                    prev_status_msg = status_msg
        
            time_end = time.time()
            time_elapsed = time_end - time_start
            status_msg = report_sim_stats(self, nsnr, format_time(time_elapsed), 0, status_msg, prev_status_msg)
            prev_status_msg = status_msg

        if(self.plot_enable):
            # Calculate BER/BLER and present in a semilogy plot
            self.ber = np.divide(self.bit_error, self.frame_count * self.len_k)
            self.bler = np.divide(self.frame_error, self.frame_count)
            plt.semilogy(self.snr_points, self.ber, 'b--', label='BER')
            plt.semilogy(self.snr_points, self.bler, 'b-', label='BLER')
            plt.xlabel('SNR (dB)')
            plt.ylabel('BER/BLER')
            plt.title('Error Correction Performance')
            plt.legend()
            # plt.show()
            if(self.save_output):
                plt.savefig(self.path_fig_output)

        '''End simulation'''