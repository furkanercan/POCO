import datetime

def generate_sim_header():
    header_lines = [
        "##############################################################",
        "#                                                            #",
        "#  Author: Furkan Ercan                                      #",
        "#  Copyright (c) {} Furkan Ercan. All Rights Reserved.     #".format(datetime.datetime.now().year-1),
        "#                                                            #",
        "#  Successive Cancellation Decoder for Polar Codes           #",
        "#                                                            #",
        "#  Version: 1.0                                              #",
        "#                                                            #",
        "#  Licensed under the MIT License                            #",
        "#  See the LICENSE file for details.                         #",
        "#                                                            #",
        "##############################################################",
        ""
    ]

    header = "\n".join(header_lines)
    return header

def report_sim_stats(sim_snr_points, sim_bit_error, sim_frame_error, sim_frame_count, len_n, time_elapsed):
    ber = sim_bit_error/(sim_frame_count*len_n)
    bler = sim_frame_error/sim_frame_count
    iter = 1

    print(f"{sim_snr_points} {ber} {bler} {iter} {sim_frame_count} {sim_frame_error} {time_elapsed}")