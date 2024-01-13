import numpy as np
import math

def llr_quantizer(vec_llr, num_qbits, num_fbits):
    # Calculate the quantization step
    quant_step = 2 ** num_fbits
    quant_upper = (2 ** (num_qbits -1) - 1)/quant_step
    quant_lower = (-(2 ** (num_qbits -1)))//quant_step

    # print(f"upper and lower quantizations are {quant_upper} and {quant_lower}")

    for i in range(len(vec_llr)):

        # Quantize the double variable
        vec_llr[i] = np.round(vec_llr[i] * quant_step)/quant_step

        if(vec_llr[i] < quant_lower):
            vec_llr[i] = quant_lower
        elif(vec_llr[i] > quant_upper):
            vec_llr[i] = quant_upper
    
    return vec_llr