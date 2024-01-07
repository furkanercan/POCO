def call_decoding_schedule(target_sch, target_stage, base_vector, limit):
    for i in range(len(base_vector)):
        if(base_vector[i] == 'H' and limit > 1):
            call_decoding_schedule(target_sch, target_stage, base_vector, limit-1)
        else:
            target_sch.append(base_vector[i])
            target_stage.append(limit)


def create_decoding_schedule(sch_limit):
    vec_sch_init = ['F', 'H', 'G', 'H', 'C']
    vec_sch = []
    vec_stage = []
    call_decoding_schedule(vec_sch, vec_stage, vec_sch_init, sch_limit)
    
    return vec_sch, vec_stage