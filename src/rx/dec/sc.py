import numpy as np

def dec_sc_f(mem_alpha, stage_size, stage_depth, is_quantized, max_value):
    batch_size = mem_alpha[0].shape[0]
    
    for b in range(batch_size):
        llr_a = mem_alpha[stage_depth][b, :stage_size // 2]
        llr_b = mem_alpha[stage_depth][b, stage_size // 2:]
        
        abs_llr = np.minimum(np.abs(llr_a), np.abs(llr_b))
        sign = np.sign(llr_a * llr_b)
        result = abs_llr * sign

        if is_quantized: #Only possible breach is when the result is 2^q and in 2s complement form.
            result = np.minimum(max_value, result)
        
        mem_alpha[stage_depth - 1][b, :stage_size // 2] = result

def dec_sc_g(mem_alpha, mem_beta, stage_size, stage_depth, is_quantized, max_value, min_value):
    batch_size = mem_alpha[0].shape[0]

    for b in range(batch_size):
        llr_a = mem_alpha[stage_depth][b, :stage_size // 2]
        llr_b = mem_alpha[stage_depth][b, stage_size // 2:]

        mem_beta_slice = mem_beta[stage_depth - 1][b, :stage_size // 2]
        mem_alpha_slice = np.where(mem_beta_slice == 0, llr_b + llr_a, llr_b - llr_a)        

        if is_quantized:
            mem_alpha_slice = np.clip(mem_alpha_slice, min_value, max_value)

        mem_alpha[stage_depth - 1][b, :stage_size // 2] = mem_alpha_slice

def dec_sc_c(mem_beta_l, mem_beta_r, stage_size, stage_depth, stage_dir):

    beta_src1 = mem_beta_l[stage_depth][:, :stage_size]
    beta_src2 = mem_beta_r[stage_depth][:, :stage_size]
    beta_src1_int = beta_src1.astype(int)
    beta_src2_int = beta_src2.astype(int)
    
    if(stage_dir == 0):
        mem_beta_l[stage_depth + 1][:, :stage_size] = np.bitwise_xor(beta_src1_int, beta_src2_int)
        mem_beta_l[stage_depth + 1][:, stage_size:] = beta_src2_int
    else:
        mem_beta_r[stage_depth + 1][:, :stage_size] = np.bitwise_xor(beta_src1_int, beta_src2_int)
        mem_beta_r[stage_depth + 1][:, stage_size:] = beta_src2_int

def dec_sc_h(mem_beta_l, mem_beta_r, llr, stage_dir):
    batch_size = mem_beta_l[0].shape[0]
    if(stage_dir == 0):
        for b in range(batch_size):
            mem_beta_l[0][b, 0] = 1 if llr[b] < 0 else 0
    else:
        for b in range(batch_size):
            mem_beta_r[0][b, 0] = 1 if llr[b] < 0 else 0


def dec_sc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta_l, mem_beta_r, \
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
        elif vec_dec_sch[i] == 'H': #Frozen index hit
            if(vec_dec_sch_dir[i] == 0):
                mem_beta_l[0][:, 0] = 0
            else:
                mem_beta_r[0][:, 0] = 0
        elif vec_dec_sch[i] == 'I': #Info index hit
            dec_sc_h(mem_beta_l, mem_beta_r, mem_alpha[0][:, 0], vec_dec_sch_dir[i])
            if(vec_dec_sch_dir[i] == 0):
                vec_decoded[:,info_ctr] = mem_beta_l[0][:, 0]
            else:
                vec_decoded[:,info_ctr] = mem_beta_r[0][:, 0]
            info_ctr += 1