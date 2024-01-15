import numpy as np

def llr_quantizer(vec_llr, quant_step, quant_chnl_lower, quant_chnl_upper):
    
    vec_llr_quantized = np.round(vec_llr * quant_step) / quant_step
    vec_llr_quantized = np.clip(vec_llr_quantized, quant_chnl_lower, quant_chnl_upper)

    return vec_llr_quantized
