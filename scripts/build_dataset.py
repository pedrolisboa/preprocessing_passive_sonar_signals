import os
from poseidon.io.offline import load_raw_data

base_dir = os.getcwd()
database = '4classes'
username = os.environ['CLUSTER_USER']
raw_data_path = os.path.join(base_dir, 'data', 'raw', database)
raw_data = load_raw_data(raw_data_path, verbose=0)

raw_data.to_hdf5(os.path.join(raw_data_path, 'user.%s.dataset.raw.%s.acoustic.lane.fs_22050.b_8.pos_45m.hdf5' % (username, database)))


