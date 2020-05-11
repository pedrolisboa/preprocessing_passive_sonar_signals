import os
import json

base_dir = os.getcwd()
tasks_dir = os.path.join(base_dir, 'tasks')
meta_dir = os.path.join(base_dir, 'metadata')
configs_dir = os.path.join(base_dir, 'configs')
data_dir = os.path.join(base_dir, 'data')

configurations = filter(lambda x: not x in ['generator.py'], os.listdir(configs_dir))

valid_dataset_formats = ['csv', 'hdf5', 'npz']
tasks_dict = dict()
for configuration in configurations:
    taskname_list = configuration.split('.')[0:2]
    taskname_list.append('task')
    taskname_list.extend(configuration.split('.')[2:])
    taskname = '.'.join(taskname_list)

    datasets = list(
        filter(lambda x: x.split('.')[-1] in valid_dataset_formats,
               os.listdir(
                   os.path.join(data_dir, configuration.split('.')[2],
                                configuration.split('.')[3]))))

    if len(datasets) > 1:
        raise ValueError('Found more than one dataset file')
    config_dataset = datasets[0]
    tasks_dict[configuration] = {
        'taskname' : taskname,
        'dataset'  : config_dataset,
        'configs'   : configuration
    }

    json.dump(tasks_dict[configuration], open(os.path.join(meta_dir, configuration + '.json'), 'w'))

