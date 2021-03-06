import os
import json
import argparse

import numpy as np

from sklearn.model_selection import StratifiedKFold
from poseidon.io.offline import SonarDict
from src.feature_extraction import preprocess_data, generate_data_trgt_pair
from src.model import train_fold

import tensorflow.keras.backend as K

def run_jobs(configFile, dataFile, outputPath):
    # Load experiment configuration
    params = json.load(open(configFile, 'r'))

    database = params['database']
    signal_proc_params = params['signal_proc_params']
    spectrogram_args = params['spectrogram_args']
    model_params = params['model_params']
    training_params = params['training_params']
    preprocessing_config = params['preprocessing_config']

    p_mode = preprocessing_config['p_mode']
    t_mode = preprocessing_config['t_mode']
    e_mode = preprocessing_config['e_mode']
    f_mode = preprocessing_config['f_mode']

    # Loading data
    raw_data = SonarDict.from_hdf5(dataFile)

    # Raw data feature extraction and processing
    data, trgt = generate_data_trgt_pair(preprocess_data(
                raw_data,
                p_mode, t_mode, e_mode,
                signal_proc_params, spectrogram_args
                ))
    n_classes = np.unique(trgt).shape[0]

    skf = StratifiedKFold(n_splits=training_params['n_splits'], shuffle=True, random_state=42)
    cvo = skf.split(data, trgt)
    for i, (train, test) in enumerate(cvo):
        K.clear_session()
        model_path = os.path.join(outputPath, configFile.split('/')[-1], '%i_fold' % i)
        train_fold(
            data, trgt, i, train, test, f_mode, model_path,
            n_classes, model_params, training_params
        )

if __name__ == "__main__":
    # Arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--configFile', action='store',
            dest='configFile', required = True,
                help = "The job config file that will be used to configure the job (sort and init).")
    parser.add_argument('-o','--outputPath', action='store',
            dest='outputPath', required = True, default = None,
                help = "Model path")
    parser.add_argument('-d','--database', action='store',
            dest='dataFile', required = True, default = None,
                help = "The database to be used")
    args = parser.parse_args()

    # run
    run_jobs(args.configFile, args.dataFile, args.outputPath)
