import random

def encode(code_n, code_k):
    # Generate code_k random binary values
    # random.seed(123)
    vec_k = [random.choice([0, 1]) for _ in range(code_k)]
    vec_n = [0] * code_n
    vec_n[:code_k] = vec_k
    return vec_n