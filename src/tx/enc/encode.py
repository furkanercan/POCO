import numpy as np

def polar_encode(vec_uncoded, polar_enc_matrix):
    return (vec_uncoded @ polar_enc_matrix  % 2)

def create_polar_enc_matrix(len_logn, vec_polar_info_indices):
    polar_enc_matrix_core = [[1, 0], [1, 1]]
    polar_enc_matrix = polar_enc_matrix_core  # Core matrix as the initial value
    for _ in range(len_logn-1):
        polar_enc_matrix = np.kron(polar_enc_matrix, polar_enc_matrix_core)

    polar_enc_matrix_full = polar_enc_matrix
    polar_enc_matrix = polar_enc_matrix[vec_polar_info_indices]
    return polar_enc_matrix_full, polar_enc_matrix

def create_polar_indices(len_n, len_k, vec_polar_rel_idx):
    vec_polar_isfrozen = np.ones(len_n, dtype=int)
    vec_polar_info = np.ones(len_n, dtype=int)

    for num, index in enumerate(vec_polar_rel_idx[:len_k], start=0):
        vec_polar_isfrozen[index] = 0
    for num, index in enumerate(vec_polar_rel_idx[len_k:], start=len_k):
        vec_polar_info[index] = 0 

    vec_polar_info_indices = np.nonzero(vec_polar_info)[0]

    return vec_polar_info_indices, vec_polar_isfrozen