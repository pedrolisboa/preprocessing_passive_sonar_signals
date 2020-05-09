import json
import os
import argparse
from itertools import product
from src.preprocessing_blocks import (frequency_decimation_blocks, 
                                  background_noise_correction_blocks, 
                                  individual_spectrum_normalization_blocks,
                                  frequency_bin_normalization_blocks)


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', action='store', dest='path',
                    required=False, default='.', 
                    help='Base path to store config folders. Defaults to current')
args = parser.parse_args()                

# Creating grid map from defined modes
base_config = {
    "database": "4classes",
    "signal_proc_params": {
        "decimation_rate": 3,
        "fs": 22050,
        "spectrum_bins_left": 800
    },
    "spectrogram_args": {
        "window": "hann",
        "fs": 7350,
        "nfft": 2048,
        "nperseg": 2048,
        "noverlap": 0,
        "detrend": False,
        "axis": 0,
        "scaling": "spectrum",
        "mode": "magnitude"
    },
    "training_params": {
        "n_splits": 10,
        "random_state": 42,
        "epochs": 1000,
        "batch_size": 128,
        "early_stopping_patience": 100,
        "n_inits": 10
    },
    "model_params": {
        "hidden_neurons": [6]
    }
}

p_modes = frequency_decimation_blocks.keys()
t_modes = background_noise_correction_blocks.keys()
e_modes = individual_spectrum_normalization_blocks.keys()
f_modes = frequency_bin_normalization_blocks.keys()

mode_combinations = list(product(p_modes, t_modes, e_modes, f_modes))

database = '4classes'
hidden_neurons = 6
for (p_mode, t_mode, e_mode, f_mode) in mode_combinations:
    preprocessing_config = {
        'p_mode': p_mode,
        't_mode': t_mode,
        'e_mode': e_mode,
        'f_mode': f_mode
    }
    base_config['preprocessing_config'] = preprocessing_config

    config_folder = os.path.join(args.path ,'user.%s.acoustic_lane.%s' % (os.environ['CLUSTER_USER'], database))
    config_name = 'user.%s.%s_p_%s_t_%s_e_%s_f_%s_neurons_%i.json' % (
        os.environ['CLUSTER_USER'],
        database, 
        p_mode, t_mode, e_mode, f_mode,
        hidden_neurons)

    os.makedirs(config_folder, exist_ok=True)
    json.dump(base_config, open(os.path.join(config_folder, config_name), 'w'))
