import numpy as np
from src.rx.dec.sc import *

def dec_fastssc_r0(mem_beta_l, mem_beta_r, stage_depth, sch_dir):
    if sch_dir == 0:
        mem_beta_l[stage_depth][:, :] = 0
    else:
        mem_beta_r[stage_depth][:, :] = 0

def dec_fastssc_r1(mem_alpha, mem_beta_l, mem_beta_r, stage_depth, sch_dir):
    if sch_dir == 0:
        mem_beta_l[stage_depth][:, :] = np.where(mem_alpha[stage_depth][:, :] < 0, 1, 0)
    else:
        mem_beta_r[stage_depth][:, :] = np.where(mem_alpha[stage_depth][:, :] < 0, 1, 0)
        
def dec_fastssc_rep(mem_alpha, mem_beta_l, mem_beta_r, stage_depth, sch_dir):
    batch_size = mem_alpha[stage_depth].shape[0]

    for batch_idx in range(batch_size):
        rep_sum = np.sum(mem_alpha[stage_depth][batch_idx,:])
        rep_sgn = rep_sum < 0
        if sch_dir == 0:
            mem_beta_l[stage_depth][batch_idx,:] = rep_sgn
        else:
            mem_beta_r[stage_depth][batch_idx,:] = rep_sgn


def dec_fastssc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta_l, mem_beta_r, \
                  vec_dec_sch_size, vec_dec_sch_dir, vec_dec_sch_depth, vec_polar_isfrozen, \
                  qbits_enable, quant_intl_max, quant_intl_min):
    for i in range(len(vec_dec_sch)):
        if vec_dec_sch[i] == 'F':
            dec_sc_f(mem_alpha, vec_dec_sch_size[i], vec_dec_sch_depth[i], qbits_enable, quant_intl_max)
        elif vec_dec_sch[i] == 'G':
            dec_sc_g(mem_alpha, mem_beta_l, vec_dec_sch_size[i], vec_dec_sch_depth[i], qbits_enable, quant_intl_max, quant_intl_min)
        elif vec_dec_sch[i] == 'C':
            dec_sc_c(mem_beta_l, mem_beta_r, vec_dec_sch_size[i], vec_dec_sch_depth[i], vec_dec_sch_dir[i])
        elif vec_dec_sch[i] == 'R0':
            dec_fastssc_r0(mem_beta_l, mem_beta_r, vec_dec_sch_depth[i], vec_dec_sch_dir[i])
        elif vec_dec_sch[i] == 'R1':
            dec_fastssc_r1(mem_alpha, mem_beta_l, mem_beta_r, vec_dec_sch_depth[i], vec_dec_sch_dir[i])
        elif vec_dec_sch[i] == 'REP':
            dec_fastssc_rep(mem_alpha, mem_beta_l, mem_beta_r, vec_dec_sch_depth[i], vec_dec_sch_dir[i])