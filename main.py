import random
import numpy as np
import math
from src.tx.enc.encode import encode
from src.lib.supp.readfile_polar_rel_idx import readfile_polar_rel_idx
from src.lib.supp.create_decoding_schedule import create_decoding_schedule

# Set random seed
np.random.seed(919) 
random.seed(918)

# Read the polar reliability index file
filepath_polar_rel_idx = "src/lib/ecc/polar/3gpp/n64_3gpp.pc"
vec_polar_rel_idx  = readfile_polar_rel_idx(filepath_polar_rel_idx)
print(f"polar reliability index is:")
for num in vec_polar_rel_idx:
    print(num, end='\t')
print("\n")

len_k = 32
len_n = len(vec_polar_rel_idx)
len_logn = int(math.log2(len_n))

vec_polar_frozen = [1] * len_n

# Generate the polar frozen indicators
for num, index in enumerate(vec_polar_rel_idx[:len_k], start=0):
    vec_polar_frozen[index] = 0

# Generate information bits, get vec_k
vec_info = [random.choice([0,1]) for _ in range(len_k)]

# Place the generated information bits into the codeword to be encoded
vec_uncoded = [0]*len_n

for i in range(len_k):
    vec_uncoded[vec_polar_rel_idx[i]] = vec_info[i]

# Encode the uncoded
polar_enc_matrix_core = [[1, 0], [1, 1]]
polar_enc_matrix = polar_enc_matrix_core  # Identity matrix as the initial value

for _ in range(len_logn-1):
    polar_enc_matrix = np.kron(polar_enc_matrix, polar_enc_matrix_core)
    
vec_encoded = (polar_enc_matrix @ vec_uncoded % 2)

# Modulate the encoded vector
vec_mod = 1-2*vec_encoded

print(f"Generated vector: {vec_mod}")

# Transmit modulated frame through the channel, receive the noisy frame
awgn_mean = 0
awgn_stdev = 0.5
awgn_var = np.power(awgn_stdev,2)

vec_awgn = [0] * len_n
vec_rx = [0] * len_n
vec_llr = [0] * len_n

vec_awgn = np.random.normal(awgn_mean, awgn_stdev, len_n) # Generate noise
vec_rx = vec_mod + vec_awgn                               # Apply noise
vec_llr = 2.0 * vec_rx / awgn_var                         # Get LLRs of the frame

# print(f"stdev and variance are: {awgn_stdev}, {awgn_var}")

# print(f"Generated vector: {vec_awgn}")

# print(f"Generated vector: {vec_rx}")

# print(f"Generated vector: {vec_llr}")


# Quantize the frame (optional)
# TBD


# Decode the frame (SC)

# Create a new vector using the recursive function
vec_dec_sch = create_decoding_schedule(len_logn)

print("Schedule:", vec_dec_sch)
print("length logn is ", len_logn)




# Compare the info bits, derive BER/FER

# Call the generate_binary_vector function
#vec_n = encode(len_n, len_k)

# Print the result
# print(f"Generated vector: {vec_n}")



# print(f"polar frozen indices are:")
# for num in vec_polar_frozen:
#     print(num, end=' ')
# print('\n')
