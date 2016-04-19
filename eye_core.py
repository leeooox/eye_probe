from __future__ import division as _division, print_function as _print_function
import numpy as np
from brescount import bres_curve_count
#from scipy.signal import resample
seg_map_scope = dict(
        red = [
            (0.000000, 0.000000, 0.000000), 
            (1.00e-18, 0.000000, 0.196078),  
            (0.015625, 0.196078, 0.000000), 
            (0.031250, 0.000000, 0.984314), 
            (0.062500, 0.984314, 0.749020), 
            (0.125000, 0.749020, 1.000000),
            (0.250000, 1.000000, 0.898039), 
            (0.500000, 0.898039, 1.000000),
            (1.000000, 1.000000, 1.000000) 
        ],
        green = [
            (0.000000, 0.000000, 0.000000), 
            (1.00e-18, 0.000000, 0.749020),
            (0.015625, 0.749020, 0.098039), 
            (0.031250, 0.098039, 0.247059), 
            (0.062500, 0.247059, 0.074510), 
            (0.125000, 0.074510, 0.537255),
            (0.250000, 0.537255, 0.807843), 
            (0.500000, 0.807843, 1.000000),
            (1.000000, 1.000000, 1.000000) 
        ],
        blue = [
            (0.000000, 0.000000, 0.000000), 
            (1.00e-18, 0.000000, 0.184314),  
            (0.015625, 0.184314, 1.000000), 
            (0.031250, 1.000000, 1.000000), 
            (0.062500, 1.000000, 0.074510), 
            (0.125000, 0.074510, 0.000000),
            (0.250000, 0.000000, 0.000000), 
            (0.500000, 0.000000, 1.000000),
            (1.000000, 1.000000, 1.000000) 
        ]
    )




def calc_eye_heatmap(sig, samps_per_ui, ui ,clock_times=None, grid_size=(800,640)):
    height, width = grid_size

    dt = width / (samps_per_ui*2)

    counts = np.zeros((width,height), dtype=np.int32)
    
    sig_min = sig.min()
    sig_max = sig.max()

    sig_amp = sig_max - sig_min

    sig_min -= 0.05*sig_amp
    sig_max += 0.05*sig_amp

    xs = np.linspace(-ui * 1.e12, ui * 1.e12, width)
    ys = np.linspace(sig_min, sig_max, height)

    xx = (np.arange(2*samps_per_ui+1)*dt).astype(np.int32)
    if clock_times is not None:
        tsamp = ui / samps_per_ui

        for clock_time in clock_times:
            start_time = clock_time - ui
            stop_time  = clock_time + ui
            start_ix   = int(start_time // tsamp)
            if(start_ix + 2 * samps_per_ui + 1 > len(sig)):
                break
            elif start_ix <0:
                continue

            interp_fac = (start_time - start_ix * tsamp) / tsamp
            samp1 = sig[start_ix : start_ix + 2 * samps_per_ui+1]
            samp2 = sig[start_ix + 1 : start_ix + 2 + 2 * samps_per_ui]
            yy = samp1 + (samp2 - samp1) * interp_fac
            iyd = (height * (yy - sig_min)/(sig_max - sig_min)+0.5).astype(np.int32)
            bres_curve_count(xx, iyd, counts)     

    else:
        start_ix      = np.where(np.diff(np.sign(sig)))[0][0] + samps_per_ui // 2 
        last_start_ix = len(sig) - 2 * samps_per_ui
        while(start_ix < last_start_ix):
            yy = sig[start_ix : start_ix + 2 * samps_per_ui+1]
            iyd = (height * (yy - sig_min)/(sig_max - sig_min)+0.5).astype(np.int32)    
            bres_curve_count(xx, iyd, counts)
            start_ix += samps_per_ui

    return xs,ys,counts.T


def get_demo_data():
    sig = np.loadtxt("ctle_out.txt")[1000:]
    ui = 1/10E9
    samps_per_ui = 32

    return sig,samps_per_ui,ui
