class Sim:
    def __init__(self, filepath_polar_rel_idx, len_k, snr_start, snr_end, snr_step, \
                 num_frames, num_errors, num_max_fr, \
                 qbits_enable, qbits_chnl, qbits_intl, qbits_frac, \
                 plot_enable, lutsim_enable, \
                 en_r0, en_r1, en_rep, en_spc, en_0011, en_0101, \
                 r0_size, r1_size, rep_size, spc_size):
        
        self.filepath_polar_rel_idx = filepath_polar_rel_idx
        self.len_k = len_k
        self.snr_start = snr_start
        self.snr_end = snr_end
        self.snr_step = snr_step
        self.num_frames = num_frames
        self.num_errors = num_errors
        self.num_max_fr = num_max_fr
        self.qbits_enable = qbits_enable
        self.qbits_chnl = qbits_chnl
        self.qbits_intl = qbits_intl
        self.qbits_frac = qbits_frac
        self.plot_enable = plot_enable
        self.lutsim_enable = lutsim_enable
        self.en_r0 = en_r0
        self.en_r1 = en_r1
        self.en_rep = en_rep
        self.en_spc = en_spc
        self.en_0011 = en_0011
        self.en_0101 = en_0101
        self.r0_size = r0_size
        self.r1_size = r1_size
        self.rep_size = rep_size
        self.spc_size = spc_size


def create_sim_from_config(config_data):
    return Sim(
        filepath_polar_rel_idx = config_data.get("filepath_polar_rel_idx"),
        len_k         = config_data.get("info_bit_length"),
        snr_start     = config_data.get("snr_start"),
        snr_end       = config_data.get("snr_end"),
        snr_step      = config_data.get("snr_step"),
        num_frames    = config_data.get("num_frames"),
        num_errors    = config_data.get("num_errors"),
        num_max_fr    = config_data.get("num_max_fr"),
        qbits_enable  = config_data.get("qbits_enable"),
        qbits_chnl    = config_data.get("qbits_chnl"),
        qbits_intl    = config_data.get("qbits_intl"),
        qbits_frac    = config_data.get("qbits_frac"),
        plot_enable   = config_data.get("plot_enable"),
        lutsim_enable = config_data.get("lutsim_enable"),
        en_r0         = config_data.get("fast_r0_enable"),
        en_r1         = config_data.get("fast_r1_enable"),
        en_rep        = config_data.get("fast_rep_enable"),
        en_spc        = config_data.get("fast_spc_enable"),
        en_0011       = config_data.get("fast_0011_enable"),
        en_0101       = config_data.get("fast_01011_enable"),
        r0_size       = config_data.get("fast_r0_max_size"),
        r1_size       = config_data.get("fast_r1_max_size"),
        rep_size      = config_data.get("fast_rep_max_size"),
        spc_size      = config_data.get("fast_spc_max_size")
    )