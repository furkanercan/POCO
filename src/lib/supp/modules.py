class Sim:
    def __init__(self, filepath_polar_rel_idx, len_k, snr_start, snr_end, snr_step, num_frames, num_errors, num_max_fr, qbits_enable, qbits_chnl, qbits_intl, qbits_frac, plot_enable):
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


def create_sim_from_config(config_data):
    return Sim(
        filepath_polar_rel_idx = config_data.get("filepath_polar_rel_idx"),
        len_k = config_data.get("info_bit_length"),
        snr_start = config_data.get("snr_start"),
        snr_end = config_data.get("snr_end"),
        snr_step = config_data.get("snr_step"),
        num_frames = config_data.get("num_frames"),
        num_errors = config_data.get("num_errors"),
        num_max_fr = config_data.get("num_max_fr"),
        qbits_enable = config_data.get("qbits_enable"),
        qbits_chnl = config_data.get("qbits_chnl"),
        qbits_intl = config_data.get("qbits_intl"),
        qbits_frac = config_data.get("qbits_frac"),
        plot_enable = config_data.get("plot_enable")
    )