def dec_sc_f(mem_alpha, stage_size, stage_depth, mem_alpha_ptr, is_quantized, max_value, min_value):
    batch_size = mem_alpha.shape[0]
    
    for b in range(batch_size):
        for i in range(stage_size // 2):
            llr_a = mem_alpha[b, stage_depth, mem_alpha_ptr[stage_depth] + i]
            llr_b = mem_alpha[b, stage_depth, mem_alpha_ptr[stage_depth] + i + stage_size // 2]
            mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i] = min(llr_a, llr_b) * (1 if llr_a * llr_b >= 0 else -1)
            
            if is_quantized:
                mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i] = min(max_value, mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i])
                mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i] = max(min_value, mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i])


def dec_sc_g(mem_alpha, mem_beta, stage_size, stage_depth, mem_alpha_ptr, is_quantized, max_value, min_value):
    batch_size = mem_alpha.shape[0]

    for b in range(batch_size):
        for i in range(stage_size // 2):
            llr_a = mem_alpha[b, stage_depth, mem_alpha_ptr[stage_depth] + i]
            llr_b = mem_alpha[b, stage_depth, mem_alpha_ptr[stage_depth] + i + stage_size // 2]

            if mem_beta[b, stage_depth - 1, mem_alpha_ptr[stage_depth] + i] == 0:
                mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i] = llr_b + llr_a
            else:
                mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i] = llr_b - llr_a

            if is_quantized:
                mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i] = min(max_value, mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i])
                mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i] = max(min_value, mem_alpha[b, stage_depth - 1, mem_alpha_ptr[stage_depth - 1] + i])

def dec_sc_c(mem_beta, stage_size, stage_depth, mem_beta_ptr):
    batch_size = mem_beta.shape[0]
    for b in range(batch_size):
        for i in range(stage_size):
            mem_beta[b, stage_depth + 1, mem_beta_ptr[stage_depth + 1] + i]              = mem_beta[b, stage_depth, i + mem_beta_ptr[stage_depth + 1]] ^ mem_beta[b, stage_depth, i + stage_size + mem_beta_ptr[stage_depth + 1]]
            mem_beta[b, stage_depth + 1, mem_beta_ptr[stage_depth + 1] + i + stage_size] =                                                               mem_beta[b, stage_depth, i + stage_size + mem_beta_ptr[stage_depth + 1]]

def dec_sc_h(mem_beta, llr, is_frozen, mem_alpha_ptr):
    batch_size = mem_beta.shape[0]
    for b in range(batch_size):
        mem_beta[b, 0, mem_alpha_ptr[0]] = 0 if is_frozen else 1 if llr[b] < 0 else 0


def dec_sc(vec_decoded, vec_dec_sch, mem_alpha, mem_beta, mem_alpha_ptr, mem_beta_ptr, vec_dec_sch_size, vec_dec_sch_depth, vec_polar_isfrozen, qbits_enable, quant_intl_max, quant_intl_min):
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
        elif vec_dec_sch[i] == 'H': #Frozen index hit
            mem_beta[:, 0, mem_alpha_ptr[0]] = 0
            mem_alpha_ptr[0] += 1
        elif vec_dec_sch[i] == 'I': #Info index hit
            dec_sc_h(mem_beta, mem_alpha[:, 0, mem_alpha_ptr[0]], vec_polar_isfrozen[mem_alpha_ptr[0]], mem_alpha_ptr)
            vec_decoded[:,info_ctr] = mem_beta[:,0, mem_alpha_ptr[0]]
            info_ctr += 1
            mem_alpha_ptr[0] += 1