import os
import pandas as pd
import numpy as np
import json

from scipy.signal import decimate, spectrogram

from sklearn.model_selection import StratifiedKFold

from poseidon.signal.lofar import tpsw, lofar
from poseidon.io.offline import load_raw_data
from poseidon.signal.utils import resample

from itertools import product

from .preprocessing_blocks import (frequency_decimation_blocks, 
                                  background_noise_correction_blocks, 
                                  individual_spectrum_normalization_blocks,
                                  frequency_bin_normalization_blocks)


def cut_bins(sxx, spectrum_bins_left):
    return sxx[:, :spectrum_bins_left]

def preprocess_data(raw_data, p_mode, t_mode, e_mode, 
                    signal_proc_params, 
                    spectrogram_args):
    return (
        raw_data
            .apply(lambda rr: rr['signal'])
            .apply(decimate,
                   signal_proc_params['decimation_rate'], 8, 'fir', zero_phase=True)
            .apply(spectrogram,
                   **spectrogram_args)
            .apply(lambda x: np.transpose(x[2])) # remove time and freq info/transpose power spectrum
            .apply(cut_bins, signal_proc_params['spectrum_bins_left'])
            .apply(frequency_decimation_blocks[p_mode])
            .apply(background_noise_correction_blocks[t_mode])
            .apply(individual_spectrum_normalization_blocks[e_mode])
    )

def generate_data_trgt_pair(processed_data_dict, trgt_label_map=None):
    if trgt_label_map is None:
        trgt_label_map = {
            'ClassA': 0,
            'ClassB': 1,
            'ClassC': 2,
            'ClassD': 3
        }
    
    trgt = np.concatenate([trgt_label_map[cls_name]*np.ones(Sxx.shape[0]) 
                     for cls_name, run in processed_data_dict.items() 
                     for run_name, Sxx in run.items()])
    data = np.concatenate([Sxx
                     for cls_name, run in processed_data_dict.items() 
                     for run_name, Sxx in run.items()], axis=0)
    return data, trgt
