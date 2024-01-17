import numpy as np

def dec_sc_f(mem_alpha, stage_size, stage_depth, mem_alpha_ptr, is_quantized, max_value, min_value):
    batch_size = mem_alpha.shape[0]
    
    for b in range(batch_size):
        llr_a = mem_alpha[b, stage_depth, mem_alpha_ptr[stage_depth]:(mem_alpha_ptr[stage_depth] + stage_size // 2)]
        llr_b = mem_alpha[b, stage_depth, (mem_alpha_ptr[stage_depth] + stage_size // 2):(mem_alpha_ptr[stage_depth] + stage_size)]
        
        abs_llr = np.minimum(np.abs(llr_a), np.abs(llr_b))
        sign = np.sign(llr_a * llr_b)
        result = abs_llr * sign

        if is_quantized: #Only possible breach is when the result is 2^q and in 2s complement form.
            result = np.minimum(max_value, result)
        
        mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1]:(mem_alpha_ptr[stage_depth - 1] + stage_size // 2)] = result

def dec_sc_g(mem_alpha, mem_beta, stage_size, stage_depth, mem_alpha_ptr, is_quantized, max_value, min_value):
    batch_size = mem_alpha.shape[0]

    for b in range(batch_size):
        llr_a = mem_alpha[b, stage_depth, mem_alpha_ptr[stage_depth]:(mem_alpha_ptr[stage_depth] + stage_size // 2)]
        llr_b = mem_alpha[b, stage_depth, (mem_alpha_ptr[stage_depth] + stage_size // 2):(mem_alpha_ptr[stage_depth] + stage_size)]

        mem_beta_slice = mem_beta[b, stage_depth - 1, mem_alpha_ptr[stage_depth]:(mem_alpha_ptr[stage_depth] + stage_size // 2)]
        mem_alpha_slice = np.where(mem_beta_slice == 0, llr_b + llr_a, llr_b - llr_a)        

        if is_quantized:
            mem_alpha_slice = np.clip(mem_alpha_slice, min_value, max_value)

        mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1]:(mem_alpha_ptr[stage_depth - 1] + stage_size // 2)] = mem_alpha_slice

def dec_sc_c(mem_beta, stage_size, stage_depth, mem_beta_ptr):

    beta_src1 = mem_beta[:, stage_depth, mem_beta_ptr[stage_depth + 1] : mem_beta_ptr[stage_depth + 1] + stage_size]
    beta_src2 = mem_beta[:, stage_depth, mem_beta_ptr[stage_depth + 1] + stage_size : mem_beta_ptr[stage_depth + 1] + 2*stage_size]

    mem_beta[:, stage_depth + 1, mem_beta_ptr[stage_depth + 1] : mem_beta_ptr[stage_depth + 1] + stage_size] = np.bitwise_xor(beta_src1, beta_src2)
    mem_beta[:, stage_depth + 1, mem_beta_ptr[stage_depth + 1] + stage_size : mem_beta_ptr[stage_depth + 1] + 2*stage_size] = beta_src2

def dec_sc_h(mem_beta, llr, is_frozen, mem_alpha_ptr):
    batch_size = mem_beta.shape[0]
    for b in range(batch_size):
        mem_beta[b, 0, mem_alpha_ptr[0]] = 0 if is_frozen else 1 if llr[b] < 0 else 0


def dec_sc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta_l, mem_beta_r, \
           vec_dec_sch_size, vec_dec_sch_depth, vec_polar_isfrozen, \
           qbits_enable, quant_intl_max, quant_intl_max):
    info_ctr = 0
    for i in range(len(vec_dec_sch)):
        if vec_dec_sch[i] == 'F':
            dec_sc_f(mem_alpha, vec_dec_sch_size[i], vec_dec_sch_depth[i], mem_alpha_ptr, qbits_enable, quant_intl_max, quant_intl_max)
        elif vec_dec_sch[i] == 'G':
            dec_sc_g(mem_alpha, mem_beta, vec_dec_sch_size[i], vec_dec_sch_depth[i], mem_alpha_ptr, qbits_enable, quant_intl_max, quant_intl_min)
            mem_alpha_ptr[vec_dec_sch_depth[i]] += vec_dec_sch_size[i]
        elif vec_dec_sch[i] == 'C':
            dec_sc_c(mem_beta, vec_dec_sch_size[i], vec_dec_sch_depth[i], mem_beta_ptr)
            mem_beta_ptr[vec_dec_sch_depth[i] + 1] += vec_dec_sch_size[i] * 2
        elif vec_dec_sch[i] == 'H': #Frozen index hit
            mem_beta[:, 0, mem_alpha_ptr[0]] = 0
            mem_alpha_ptr[0] += 1
        elif vec_dec_sch[i] == 'I': #Info index hit
            dec_sc_h(mem_beta, mem_alpha[:, 0, mem_alpha_ptr[0]], vec_polar_isfrozen[mem_alpha_ptr[0]], mem_alpha_ptr)
            vec_decoded[:,info_ctr] = mem_beta[:,0, mem_alpha_ptr[0]]
            info_ctr += 1
            mem_alpha_ptr[0] += 1