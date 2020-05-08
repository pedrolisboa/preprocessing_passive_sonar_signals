import os
import pandas as pd
import numpy as np

from scipy.signal import decimate, spectrogram

from sklearn.model_selection import StratifiedKFold
from itertools import product
from subprocess import Popen

import argparse
import sys

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


# Arg parser
parser = argparse.ArgumentParser()
parser.add_argument('-c','--useCluster', action='store', type=str2bool,
        dest='useCluster', required = True, default=False,
            help = "Use lps cluster to run the config.")
parser.add_argument('-f','--jobfileFolder', action='store',
        dest='jobfileFolder', required = False, default='./container',
            help = "Point to where the job creation script is located. Only used in local mode")
args = parser.parse_args()

if not args.useCluster:
    sys.path.append(args.jobfileFolder)
    import create_job


    base_dir = os.getcwd()
    configs_folder = os.listdir('configs')[1]
    config_folder = os.path.join('configs', configs_folder)
    mode_combinations = os.listdir(config_folder)
    models_dir = 'models'


    dataset='4classes'
    datapath = os.path.join('data', 'raw', dataset, 
                           '%s_acoustic_lane_fs_22050_b_8_pos_45m.hdf5' % dataset)

    
    for filename in mode_combinations:
        filepath = os.path.abspath(os.path.join(config_folder, filename))
        modelpath = os.path.join(models_dir, filename.replace('.json', ''))
        # process = Popen("python3 %s -c %s -o %s -d %s" % (jobfile, filepath, modelpath, datapath), shell=True).wait()
        create_job.run_jobs(filepath, datapath, modelpath)
        # print(process)
else:
    import lps_maestro as maestro

    username = 'plisboa'
    taskname = 'user.plisboa.acoustic_lane.4classes.preprocessing_passive_sonar'
    dataset = 'user.plisboa.4classes_acoustic_lane_fs_22050_b_8_pos_45m.hdf5'
    configs = 'user.plisboa.acoustic_lane.4classes.preprocessing_passive_sonar.config'
    container = 'pedrolisboa/theseus'


    execCommand = 'python3 /create_job.py -c %IN -o %OUT -d %DATA'

    print (maestro.task.create(taskname, dataset, configs, execCommand, container))
