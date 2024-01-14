import numpy as np
import math

def call_decoding_schedule(target_sch, base_vector, limit):
    for i in range(len(base_vector)):
        if(base_vector[i] == 'H' and limit > 1):
            call_decoding_schedule(target_sch, base_vector, limit-1)
        else:
            target_sch.append(base_vector[i])


def create_decoding_stages(vec_sch, sch_limit):
    vec_stage = []
    vec_depth = []
    current_stagesize = np.power(2,sch_limit)
    for i in range(len(vec_sch)):
        if(vec_sch[i] == 'F'):
            vec_stage.append(int(current_stagesize))
            vec_depth.append(int(np.log2(current_stagesize)))
            current_stagesize /= 2
        elif(vec_sch[i] == 'G'):
            if(vec_sch[i-1] == 'C' or vec_sch[i-1] == 'H'):
                vec_stage.append(int(current_stagesize*2))
                vec_depth.append(int(np.log2(current_stagesize*2)))
            else:
                vec_stage.append(int(current_stagesize))
                vec_depth.append(int(np.log2(current_stagesize)))
                current_stagesize *= 2
        elif(vec_sch[i] == 'C'):
            vec_stage.append(int(current_stagesize))
            vec_depth.append(int(np.log2(current_stagesize)))
            current_stagesize *= 2
        else:
            vec_stage.append(int(current_stagesize))
            vec_depth.append(int(np.log2(current_stagesize)))
    return vec_stage, vec_depth



def create_decoding_direction(vec_sch, vec_stagesize, sch_limit):

    combine_ctr =  [0] * (sch_limit + 1)
    hard_dec_ctr = [0] * (sch_limit + 1)
    sc_direction = []

    for i in range(len(vec_sch)):
        if vec_sch[i] == 'C':
            sc_direction.append(combine_ctr[math.floor(math.log2(vec_stagesize[i]))] % 2)
            combine_ctr[math.floor(math.log2(vec_stagesize[i]))] += 1
        elif vec_sch[i] == 'H':
            sc_direction.append(hard_dec_ctr[math.floor(math.log2(vec_stagesize[i]))] % 2)
            hard_dec_ctr[math.floor(math.log2(vec_stagesize[i]))] += 1
        else:
            sc_direction.append(0)
    return sc_direction

def embed_frozen_nodes(vec_sch, vec_frozen):
    j = 0
    for i in range(len(vec_sch)):
        if(vec_sch[i] == 'H'):
            if(vec_frozen[j] == 0):
                vec_sch[i] = 'I' #I for info, H for frozen
            j+=1
    return vec_sch


def create_decoding_schedule(vec_frozen, sch_limit):
    vec_dec_sch_init = ['F', 'H', 'G', 'H', 'C']
    vec_dec_sch = []

    call_decoding_schedule(vec_dec_sch, vec_dec_sch_init, sch_limit)
    vec_dec_sch_size, vec_dec_sch_depth = create_decoding_stages(vec_dec_sch, sch_limit)
    vec_dec_sch_dir = create_decoding_direction(vec_dec_sch, vec_dec_sch_size, sch_limit)
    vec_dec_sch = embed_frozen_nodes(vec_dec_sch, vec_frozen)
    
    # print("Frozen Vector:", vec_frozen)
    # print("Decoding stage sizes:", vec_sch_size)
    # print("Decoding direction for B memory:", vec_sch_dir)
    # print("Decoding schedule with info indices:", vec_sch)
    
    return vec_dec_sch, vec_dec_sch_size, vec_dec_sch_depth, vec_dec_sch_dir