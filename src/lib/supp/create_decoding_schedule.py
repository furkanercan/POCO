def call_decoding_schedule(target_vector, base_vector, limit):
    for i in range(len(base_vector)):
        if(base_vector[i] == 'H' and limit > 1):
            call_decoding_schedule(target_vector, base_vector, limit-1)
        else:
            target_vector.append(base_vector[i])


def create_decoding_schedule(sch_limit):
    vec_sch_init = ['F', 'H', 'G', 'H', 'C']
    vec_sch = []
    call_decoding_schedule(vec_sch, vec_sch_init, sch_limit)
    return vec_sch