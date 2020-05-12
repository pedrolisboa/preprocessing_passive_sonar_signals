import os
import json
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

base_dir = os.getcwd()
configs_dir = os.path.join(base_dir, 'configs')
configs_folder_content = list(filter(lambda x: x not in ['generator.py'], os.listdir('configs')))[0]
tasks_dir = 'tasks'
meta_dir = os.path.join(base_dir, 'metadata')
username = os.environ['CLUSTER_USER']

# TODO change offline interface to match maestro interface (wrapper around for loop)
if not args.useCluster:
    sys.path.append(args.jobfileFolder)
    import create_job

    config_folder = os.path.join('configs', configs_folder_content)
    mode_combinations = os.listdir(config_folder)

    dataset='4classes'
    datapath = os.path.join(
        'data', 'raw', 
        dataset, 'user.%s.dataset.raw.%s.acoustic.lane.fs_22050.b_8.pos_45m.hdf5' % (username, dataset))

    for filename in mode_combinations:
        filepath = os.path.abspath(os.path.join(config_folder, filename))
        modelpath = os.path.join(tasks_dir, config_folder, filename.replace('.json', ''))
        create_job.run_jobs(filepath, datapath, modelpath)
else:
    import lps_maestro as maestro

    container = '%s/theseus' % os.environ['DOCKERHUB']
    for metafile in os.listdir(meta_dir):
        # taskname = 'user.%s.acoustic_lane.4classes.preprocessing_passive_sonar' % username
        # dataset = 'user.%s.4classes_acoustic_lane_fs_22050_b_8_pos_45m.hdf5' % username
        # configs = 'user.%s.acoustic_lane.4classes.preprocessing_passive_sonar.config' % username
        metadata = json.load(open(os.path.join(meta_dir, metafile)))

        taskname = metadata['taskname']
        dataset  = metadata['dataset']
        configs  = metadata['configs']

        print('Preparing to send task %s' % taskname)
        print('Checking for dataset and config file on server...')
        uploaded_datasets = maestro.castor.list(username)

        # TODO define future handling of config files on local folder
        configs_name = configs.split('.')[:2]
        configs_name.append('configs')
        configs_name.extend(configs.split('.')[2:])
        configs_name = '.'.join(configs_name)
        if configs_name not in uploaded_datasets:
            print('Uploading %s config to cluster...' % configs_name)
            maestro.castor.upload(configs_name, os.path.join(configs_dir, configs))
            print('done')
        else:
            print('Config already on cluster')

        if dataset not in uploaded_datasets:
            datapath = os.path.join(base_dir, 'data', dataset.split('.')[3], dataset.split('.')[4])
            print('File location: %s' % datapath)
            print('Uploading %s dataset to cluster...' % dataset)
            maestro.castor.upload(dataset, os.path.join(datapath, dataset))
        else:
            print('Dataset already on cluster')

        execCommand = 'python3 /create_job.py -c %IN -o %OUT -d %DATA'

        print (maestro.task.create(taskname, dataset, configs_name, execCommand, container))
