import os
import pandas as pd
import numpy as np

from scipy.signal import decimate, spectrogram

from sklearn.model_selection import StratifiedKFold
from itertools import product

import lps_maestro as maestro

# base_dir = os.getcwd()
# print(os.listdir('configs'))
# configs_folder = os.listdir('configs')[1]
# config_folder = os.path.join('configs', configs_folder)
# mode_combinations = os.listdir(config_folder)
# # models_dir = os.path.join(base_dir, 'models')
# models_dir = 'models'

# dataset='4classes'
# # datapath = os.path.join(base_dir, 
# #                        'data', 'raw', dataset, 
# #                        '%s_acoustic_lane_fs_22050_b_8_pos_45m.hdf5' % dataset)
# datapath = os.path.join('data', 'raw', dataset, 
#                        '%s_acoustic_lane_fs_22050_b_8_pos_45m.hdf5' % dataset)


# for filename in mode_combinations:
#     # filepath = os.path.abspath(os.path.join(config_folder, filename))
#     filepath = os.path.join(config_folder, filename)
#     modelpath = os.path.join(models_dir, filename.replace('.json', ''))
#     # os.system("python3 ./container/create_job.py -c %s -o %s -d %s" % (filepath, modelpath, datapath))

username = 'plisboa'
taskname = 'user.plisboa.acoustic_lane.4classes.preprocessing_passive_sonar'
dataset = 'user.plisboa.4classes_acoustic_lane_fs_22050_b_8_pos_45m.hdf5'
configs = 'user.plisboa.acoustic_lane.4classes.preprocessing_passive_sonar.config'
container = 'pedrolisboa/theseus'


execCommand = 'python3 /create_job.py -c %IN -o %OUT -d %DATA'

print (maestro.task.create(taskname, dataset, configs, execCommand, container))