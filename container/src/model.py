import os
import re
import numpy as np
import pandas as pd

from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import regularizers
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

from .preprocessing_blocks import frequency_bin_normalization_blocks

from sklearn.model_selection import train_test_split


def build_dense_net(input_shape, output_shape, hidden_neurons, n_activations=["tanh"]):
    model = Sequential()
    
    model.add(Dense(hidden_neurons[0],
                    activation=n_activations[0], input_shape=input_shape))
    for neurons, activation in zip(hidden_neurons[1:], n_activations[1:]):
        if neurons == 0:
            continue
        model.add(Dense(neurons, activation=activation))
        
    model.add(Dense(output_shape, activation='tanh'))
    model.compile(optimizer=Adam(), loss='mean_squared_error', metrics=['categorical_accuracy', 'acc'])
    
    return model

def getGradientWeights(y_train, mode='standard'):
        if y_train.ndim > 1:
            y_train = y_train.argmax(axis=1)

        cls_indices, event_count = np.unique(np.array(y_train), return_counts=True)
        min_class = min(event_count)

        return {cls_index: float(min_class) / cls_count
                for cls_index, cls_count in zip(cls_indices, event_count)}

def checkFileIntegrity(path, n_sorts):
    def extract_sort_number(files, preffix, suffix):
        return map(
            lambda x: int(x[0]),
            filter(
                lambda x: x is not None, 
                map(
                    lambda x: re.search('(?<=%s)[0-9]+(?=%s)' % (preffix, suffix),  x), 
                    files
                )
            )
        )

    def check_sort_count(sort_numbers):
        for i in range(len(sort_numbers)):
            if i != sort_numbers[i]:
                return False
        return True

    train_files = os.listdir(path)
    if len(train_files) == 0:
        return -1

    history_nrs = list(extract_sort_number(train_files, 'history_', ''))
    weights_data_nrs = list(extract_sort_number(train_files, 'weights_', '[.]data'))
    weights_index_nrs = list(extract_sort_number(train_files, 'weights_', '[.]index'))

    history_nrs.sort()
    weights_data_nrs.sort()
    weights_index_nrs.sort()

    isCorrupted = (
        (not check_sort_count(history_nrs)) or 
        (not check_sort_count(weights_data_nrs)) or 
        (not check_sort_count(weights_index_nrs))
    )
    if isCorrupted:
        print('Corrupted training. Missing files for old init')
        return -1 # purge folder and start over signal

    isSameLength = len(history_nrs) == len(weights_data_nrs) == len(weights_index_nrs)
    if not isSameLength:
        print('Mismatch between weights and history file counting')
        return -1 # purge folder and start over signal

    # Job interrupted error
    if not (history_nrs[-1] == n_sorts - 1):
        print('Training incomplete')
        return -1 # purge folder and start over signal

    # Checking for best weights and prediction files existence
    if not os.path.exists(os.path.join(path, 'weights.index')):
        print('Missing best weights file')
        return -1 # purge folder and start over signal
    if not os.path.exists(os.path.join(path, 'predictions.csv')):
        print('Missing predictions file')
        return -1 # purge folder and start over signal

    return 0 # finished job
    
    
def train_fold(data, trgt, i, train, test, f_mode, model_path, n_classes, model_params, train_params):
    np.random.shuffle(train)

    # Create paths
    if os.path.exists(model_path):
        code = checkFileIntegrity(model_path, train_params['n_inits'])
        if code == -1:
            print('Purging folder content and restarting fold training')
            for file in os.listdir(model_path): 
                os.remove(os.path.join(model_path, file)) 
        else:
            print('Already trained')
            return

    else:
        os.makedirs(model_path)

    X_train, X_test = data[train], data[test]
    y_train, _      = trgt[train], trgt[test]

    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, 
                                                     test_size=0.2, random_state=42,
                                                     stratify=y_train)

    # Frequency bin normalization using statistical information from training set
    bin_normalize = frequency_bin_normalization_blocks[f_mode]
    def vector_bin_normalize(x1, x2):
        for i_bin in range(x1.shape[1]):
            if bin_normalize(x1[:, i_bin], x2[:, i_bin]).max() == np.inf:
                # print(i_bin)
                # print(x2[:, i_bin].mean())
                raise ValueError
        return np.transpose( # as we are iterating over the second axis,
            np.array(        # transposition is required after processing
                [bin_normalize(x1[:, i_bin], x2[:, i_bin])
                 for i_bin in range(x1.shape[1])]
            )
        )

    X_val = vector_bin_normalize(X_val, X_train)
    X_test = vector_bin_normalize(X_test, X_train)
    X_train = vector_bin_normalize(X_train, X_train)

    # Class weight calculation and one hot encoding
    cls_weights = getGradientWeights(y_train)
    y_train = to_categorical(y_train, num_classes=n_classes)
    y_val = to_categorical(y_val, num_classes=n_classes)

    # Callback for selection of best model among all sorts
    print(os.path.join(model_path, 'weights'))
    mc = ModelCheckpoint(save_best_only=True, 
                         filepath=os.path.join(model_path, 'weights'),
                         save_weights_only=True)

    # Run n sorts for model
    hidden_neurons = model_params['hidden_neurons']
    for ik in range(train_params['n_inits']):
        run_sort(X_train, y_train, 
                 X_val, y_val,
                 cls_weights, ik, mc, n_classes, model_path,
                 model_params, train_params)
        
    # Generate model test data
    model = build_dense_net((X_train.shape[1],), n_classes, hidden_neurons)
    model.load_weights(os.path.join(model_path, 'weights'))
    y_pred = model.predict(X_test)
    pd.DataFrame(y_pred).to_csv(os.path.join(model_path, 'predictions.csv'))


def run_sort(X_train, y_train, 
             X_val, y_val,
             cls_weights, ik, 
             mc, n_classes, model_path, model_params, train_params):    

    hidden_neurons = model_params['hidden_neurons']
    model = build_dense_net((X_train.shape[1],), n_classes, hidden_neurons)
    
    # Checkpoint for init documentation 
    mc2 = ModelCheckpoint(save_best_only=True, 
                    filepath=os.path.join(model_path, 'weights_%i' % ik),
                    save_weights_only=True)
    es = EarlyStopping(patience=train_params['early_stopping_patience'])

    history = model.fit(X_train, y_train,
                        epochs=train_params['epochs'], batch_size=train_params['batch_size'], 
                        class_weight=cls_weights,
                        callbacks=[mc, es, mc2], verbose=1, 
                        shuffle=True, validation_data=(X_val, y_val))
                        
    pd.DataFrame(history.history).to_csv(os.path.join(model_path, 'history_%i.csv' % ik))
