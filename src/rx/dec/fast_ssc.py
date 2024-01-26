import numpy as np
from src.rx.dec.sc import *

def dec_fastssc_r0(mem_beta_l, mem_beta_r, stage_size, stage_depth, vec_dec_sch_dir):
        batch_size = mem_beta_l[0].shape[0]
        if(vec_dec_sch_dir == 0):
            for batch_idx in range(batch_size):
                # print("Shape of mem_beta_l[{}]: {}".format(batch_idx, mem_beta_l[batch_idx].shape))
                for stage_idx in range(stage_size):
                    mem_beta_l[stage_depth][batch_idx][stage_idx] = 0
            # mem_beta_l[stage_depth][:, :] = [0] * stage_size
        else:
             for batch_idx in range(batch_size):
                # print("Shape of mem_beta_r[{}]: {}".format(batch_idx, mem_beta_l[batch_idx].shape))
                for stage_idx in range(stage_size):
                    mem_beta_r[stage_depth][batch_idx][stage_idx] = 0

def dec_fastssc_r1(mem_alpha, mem_beta, stage_index):
        mem_beta[stage_index][:, :] = np.where(mem_alpha[stage_index][:, :] < 0, 1, 0)

def dec_fastssc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta_l, mem_beta_r, \
                  vec_dec_sch_size, vec_dec_sch_dir, vec_dec_sch_depth, vec_polar_isfrozen, \
                  qbits_enable, quant_intl_max, quant_intl_min):
    info_ctr = 0
    for i in range(len(vec_dec_sch)):
        if vec_dec_sch[i] == 'F':
            dec_sc_f(mem_alpha, vec_dec_sch_size[i], vec_dec_sch_depth[i], qbits_enable, quant_intl_max)
        elif vec_dec_sch[i] == 'G':
            dec_sc_g(mem_alpha, mem_beta_l, vec_dec_sch_size[i], vec_dec_sch_depth[i], qbits_enable, quant_intl_max, quant_intl_min)
        elif vec_dec_sch[i] == 'C':
            dec_sc_c(mem_beta_l, mem_beta_r, vec_dec_sch_size[i], vec_dec_sch_depth[i], vec_dec_sch_dir[i])
        elif vec_dec_sch[i] == 'R0':
            dec_fastssc_r0(mem_beta_l, mem_beta_r,  vec_dec_sch_size[i], vec_dec_sch_depth[i], vec_dec_sch_dir[i])
        elif vec_dec_sch[i] == 'R1':
            dec_sc_h(mem_beta_l, mem_beta_r, mem_alpha[0][:, 0], vec_dec_sch_dir[i])
            if(vec_dec_sch_dir[i] == 0):
                vec_decoded[:,info_ctr] = mem_beta_l[0][:, 0]
            else:
                vec_decoded[:,info_ctr] = mem_beta_r[0][:, 0]
            info_ctr += 1

        
        # elif vec_dec_sch[i] == 'R1':
        #     dec_fastssc_r1(mem_alpha, mem_beta, vec_dec_sch_depth)
        #     vec_decoded[:,info_ctr] = mem_beta[:,0, mem_alpha_ptr[0]]
        #     info_ctr += 1####################
            