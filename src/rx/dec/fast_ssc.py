import numpy as np
from src.rx.dec.sc import *

def dec_fastssc_r0(mem_beta, stage_index):
        mem_beta[:, stage_index, :] = 0

def dec_fastssc_r1(mem_alpha, mem_beta, stage_index):
        mem_beta[:, stage_index, :] = np.where(mem_alpha[:, stage_index, :] < 0, 1, 0)

def dec_fastssc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta, mem_alpha_ptr, mem_beta_ptr, vec_dec_sch_size, vec_dec_sch_depth, vec_polar_isfrozen, qbits_enable, quant_intl_max, quant_intl_min):
    info_ctr = 0
    for i in range(len(vec_dec_sch)):
        if vec_dec_sch[i] == 'F':
            dec_sc_f(mem_alpha, vec_dec_sch_size[i], vec_dec_sch_depth[i], mem_alpha_ptr, qbits_enable, quant_intl_max, quant_intl_min)
        elif vec_dec_sch[i] == 'G':
            dec_sc_g(mem_alpha, mem_beta, vec_dec_sch_size[i], vec_dec_sch_depth[i], mem_alpha_ptr, qbits_enable, quant_intl_max, quant_intl_min)
            mem_alpha_ptr[vec_dec_sch_depth[i]] += vec_dec_sch_size[i]
        elif vec_dec_sch[i] == 'C':
            dec_sc_c(mem_beta, vec_dec_sch_size[i], vec_dec_sch_depth[i], mem_beta_ptr)
            mem_beta_ptr[vec_dec_sch_depth[i] + 1] += vec_dec_sch_size[i] * 2
        elif vec_dec_sch[i] == 'R0':
            dec_fastssc_r0(mem_beta, vec_dec_sch_depth)
            mem_alpha_ptr[0] += 1####################
        elif vec_dec_sch[i] == 'R1':
            dec_fastssc_r1(mem_alpha, mem_beta, vec_dec_sch_depth)
            vec_decoded[:,info_ctr] = mem_beta[:,0, mem_alpha_ptr[0]]
            info_ctr += 1####################
            mem_alpha_ptr[0] += 1####################
            