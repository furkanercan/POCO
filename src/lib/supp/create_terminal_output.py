import datetime

def generate_sim_header():
    header_lines = [
        "#################################################################################",
        "#                                                                               #",
        "#  Successive Cancellation Decoder for Polar Codes            __                #",
        "#  Author: Furkan Ercan                               _(\    |@@|               #",
        "#                                                    (__/\__ \--/ __            #",
        "#  Copyright (c) {} Furkan Ercan.                     \___|----|  |   __      #".format(datetime.datetime.now().year),
        "#  All Rights Reserved.                                  \ }{ /\ )_ / _\ _\     #",
        "#                                                           /\__/\ \__O (__     #",
        "#  Version: 1.0                                            (--/\--)    \__/     #",
        "#                                                          _)(  )(_             #",
        "#  Licensed under the MIT License                         `---''---`            #",
        "#  See the LICENSE file for details.                                            #",
        "#                                                                               #",
        "#  ASCII Art Source: https://www.asciiart.eu/                                   #",
        "#                                                                               #",
        "#################################################################################",
        "",
        "SNR (dB)    BER           FER           ITER       Frames     Errors     Time",
    ]

    header = "\n".join(header_lines)
    return header

def report_sim_stats(sim_snr_points, sim_bit_error, sim_frame_error, sim_frame_count, len_k, time_elapsed, temp, status_msg, prev_status_msg):
    ber = sim_bit_error/(sim_frame_count*len_k)
    bler = sim_frame_error/sim_frame_count
    iter = 1

    prev_status_msg = status_msg
    status_msg = f"{sim_snr_points:.3e}   {ber:.5e}   {bler:.5e}   {iter:.2e}   {sim_frame_count:.2e}   {sim_frame_error:.2e}   {time_elapsed}"
    status_pad = ' ' * max(0, len(prev_status_msg) - len(status_msg))

    if(temp == 1):
        print(status_msg + status_pad, end='\r', flush=True)
    else:
        print(status_msg + status_pad, end='\n', flush=True)
    
    return status_msg
