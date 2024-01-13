def polar_encode(vec_uncoded, polar_enc_matrix):
    return (vec_uncoded @ polar_enc_matrix  % 2)


# def polar_encode_legacy(frame_uncoded):
#     batch_size, N = frame_uncoded.shape
#     frame_encoded = frame_uncoded.copy()  
#     k = 1
#     while k < N:
#         for j in range(0, N, 2 * k):
#             for i in range(k):
#                 # print(f"i{i}  j{j}   k{k}")
#                 frame_encoded[:, j + i] ^= frame_encoded[:, k + j + i]
#         k *= 2

