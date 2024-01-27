import numpy as np

def llr_quantizer(vec_llr, quant_step, quant_chnl_lower, quant_chnl_upper):
    
    vec_llr *= quant_step
    np.clip(vec_llr, quant_chnl_lower * quant_step, quant_chnl_upper * quant_step, out=vec_llr)
    np.round(vec_llr, out=vec_llr)
    vec_llr /= quant_step
