import datetime

def generate_sim_header(sim):
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
    if sim.save_output == 1:
        with open(sim.path_output, 'w') as file_o:
            file_o.write(header + "\n")
    return header

def report_sim_stats(sim, nsnr, len_k, time_elapsed, temp, status_msg, prev_status_msg):
    ber =  sim.bit_error[nsnr]/(sim.frame_count[nsnr]*len_k)
    bler = sim.frame_error[nsnr]/sim.frame_count[nsnr]
    iter = 1

    prev_status_msg = status_msg
    status_msg = f"{sim.snr_points[nsnr]:.3e}   {ber:.5e}   {bler:.5e}   {iter:.2e}   {sim.frame_count[nsnr]:.2e}   {sim.frame_error[nsnr]:.2e}   {time_elapsed}"
    status_pad = ' ' * max(0, len(prev_status_msg) - len(status_msg))

    if(temp == 1):
        print(status_msg + status_pad, end='\r', flush=True)
    else:
        print(status_msg + status_pad, end='\n', flush=True)
        if sim.save_output == 1:
            with open(sim.path_output, 'a') as file_o:
                file_o.write(status_msg + "\n")
            
    return status_msg
