import numpy as np
import math

def isLeaf(vec_sch):
    if (vec_sch == 'H' or \
        vec_sch == 'R0' or \
        vec_sch == 'R1' or \
        vec_sch == 'REP' or \
        vec_sch == 'SPC' or \
        vec_sch == 'ML_0011' or \
        vec_sch == 'ML_0101'):
        return 1
    else:
        return 0

def call_decoding_schedule(vec_dec_sch, base_vector, limit):
    for i in range(len(base_vector)):
        if(base_vector[i] == 'H' and limit > 1):
            call_decoding_schedule(vec_dec_sch, base_vector, limit-1)
        else:
            vec_dec_sch.append(base_vector[i])

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
            if(vec_sch[i-1] == 'C' or isLeaf(vec_sch[i-1])):
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
        elif (vec_sch[i] == 'R0' or vec_sch[i] == 'R1'):
            sc_direction.append(hard_dec_ctr[math.floor(math.log2(vec_stagesize[i]))] % 2)
            hard_dec_ctr[math.floor(math.log2(vec_stagesize[i]))] += 1
        else:
            sc_direction.append(0)
    return sc_direction

def create_decoding_direction_fast(vec_sch):
    
    sc_direction = []
    directionStack = [0]

    for iteration, item in enumerate(vec_sch):
        if item == "F":
            directionStack.append(0)
            sc_direction.append(0)
        elif item == "G":
            directionStack.append(1)
            sc_direction.append(1)
        elif isLeaf(item) or item == "C":
            sc_direction.append(directionStack.pop())
    
    return sc_direction


def embed_frozen_nodes(vec_sch, vec_frozen):
    j = 0
    for i in range(len(vec_sch)):
        if(vec_sch[i] == 'H'):
            if(vec_frozen[j] == 0):
                vec_sch[i] = 'R1' 
            else:
                vec_sch[i] = 'R0'
            j+=1
    return vec_sch

def create_key_special_nodes(vec_dec_sch, sim):
    i = 0
    vec_dec_sch_fast = []
    while i < len(vec_dec_sch):
        pattern = ''.join(vec_dec_sch[i:i+5])

        if (pattern == "FR0GR0C" and sim.en_r0):  
            vec_dec_sch_fast.append("R0")
            i += 4
        elif (pattern == "FR1GR1C" and sim.en_r1): 
            vec_dec_sch_fast.append("R1")
            i += 4
        elif (pattern == "FR0GR1C" and sim.en_rep): 
            vec_dec_sch_fast.append("REP")
            i += 4
        else:
            vec_dec_sch_fast.append(vec_dec_sch[i])
        i += 1
    return vec_dec_sch_fast

def create_special_nodes(vec_dec_sch_fast, vec_dec_sch_size, vec_dec_sch_depth, sim):
    iterator_schedule = list(vec_dec_sch_fast)
    vec_dec_sch_fast.clear()

    iterator_stagesize = list(vec_dec_sch_size)
    vec_dec_sch_size.clear()

    iterator_stageidx = list(vec_dec_sch_depth)
    vec_dec_sch_depth.clear()

    i = 0
    while i < len(iterator_schedule):
        pattern = ''.join(iterator_schedule[i:i+5])

        vec_dec_sch_size.append(iterator_stagesize[i])
        vec_dec_sch_depth.append(iterator_stageidx[i])

        if pattern == "FR0GREPC" and sim.rep_size >= 4 and sim.en_rep:
            vec_dec_sch_fast.append("REP")
            i += 4
        elif pattern == "FR0GR0C" and sim.r0_size >= 4 and sim.en_r0:
            vec_dec_sch_fast.append("R0")
            i += 4
        elif pattern == "FR1GR1C" and sim.r1_size >= 4 and sim.en_r1:
            vec_dec_sch_fast.append("R1")
            i += 4
        elif pattern == "FREPGR1C" and sim.spc_size >= 4 and sim.en_spc:
            vec_dec_sch_fast.append("SPC")
            i += 4
        elif pattern == "FR0GR1C" and sim.en_0011:
            vec_dec_sch_fast.append("ML_0011")
            i += 4
        elif pattern == "FREPGREPC" and sim.en_0101:
            vec_dec_sch_fast.append("ML_0101")
            i += 4
        else:
            vec_dec_sch_fast.append(iterator_schedule[i])

        i += 1

    there_is_still_hope = True

    while there_is_still_hope:
        istherehope = False

        iterator_schedule = list(vec_dec_sch_fast)
        vec_dec_sch_fast.clear()

        iterator_stagesize = list(vec_dec_sch_size)
        vec_dec_sch_size.clear()

        iterator_stageidx = list(vec_dec_sch_depth)
        vec_dec_sch_depth.clear()

        i = 0
        while i < len(iterator_schedule):
            pattern = ''.join(iterator_schedule[i:i+5])

            vec_dec_sch_size.append(iterator_stagesize[i])
            vec_dec_sch_depth.append(iterator_stageidx[i])

            if pattern == "FR0GREPC" and sim.rep_size >= iterator_stagesize[i]  and sim.en_rep:
                vec_dec_sch_fast.append("REP")
                i += 4
                istherehope = True
            elif pattern == "FR0GR0C" and sim.r0_size >= iterator_stagesize[i]  and sim.en_r0:
                vec_dec_sch_fast.append("R0")
                i += 4
                istherehope = True
            elif pattern == "FSPCGR1C" and sim.spc_size >= iterator_stagesize[i] and sim.en_spc:
                vec_dec_sch_fast.append("SPC")
                i += 4
                istherehope = True
            elif pattern == "FR1GR1C" and sim.r1_size >= iterator_stagesize[i] and sim.en_r1:
                vec_dec_sch_fast.append("R1")
                i += 4
                istherehope = True
            else:
                vec_dec_sch_fast.append(iterator_schedule[i])

            i += 1

        if not istherehope:
            there_is_still_hope = False


def create_decoding_schedule(sim, vec_frozen, sch_limit):
    dec_alg = "Fast-SSC"
    vec_dec_sch_init = ['F', 'H', 'G', 'H', 'C']
    vec_dec_sch = []
    call_decoding_schedule(vec_dec_sch, vec_dec_sch_init, sch_limit)
    vec_dec_sch = embed_frozen_nodes(vec_dec_sch, vec_frozen)
    if(dec_alg == "Fast-SSC"):
        vec_dec_sch_fast = create_key_special_nodes(vec_dec_sch, sim)
        vec_dec_sch_size, vec_dec_sch_depth = create_decoding_stages(vec_dec_sch_fast, sch_limit)
        create_special_nodes(vec_dec_sch_fast, vec_dec_sch_size, vec_dec_sch_depth, sim)
        vec_dec_sch_dir = create_decoding_direction_fast(vec_dec_sch_fast)
        vec_dec_sch = vec_dec_sch_fast
    else: #(dec_alg == "SC")
        vec_dec_sch_size, vec_dec_sch_depth = create_decoding_stages(vec_dec_sch, sch_limit)
        vec_dec_sch_dir = create_decoding_direction(vec_dec_sch, vec_dec_sch_size, sch_limit)
    
    return vec_dec_sch,vec_dec_sch_size, vec_dec_sch_depth, vec_dec_sch_dir