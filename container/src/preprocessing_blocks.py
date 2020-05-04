import numpy as np

from scipy.signal import decimate
from poseidon.signal.lofar import tpsw

def rms(x):
    return np.sqrt((x**2).sum()/x.shape[0])

frequency_decimation_blocks = {
    'P1': lambda Sxx: decimate(decimate(Sxx, 
                                        2, 1, ftype='fir'), 
                               2, 1, ftype='fir'),
    'P2': lambda Sxx: decimate(Sxx, 2, 1, ftype='fir'),
    'P3': lambda Sxx: Sxx
}

background_noise_correction_blocks = {
    'T1': lambda Sxx: Sxx,
    'T2': lambda Sxx: Sxx - tpsw(Sxx),
    'T3': lambda Sxx: (Sxx - tpsw(Sxx))/tpsw(Sxx),
    'T4': lambda Sxx: Sxx/tpsw(Sxx),
    'T5': lambda Sxx: np.log10(Sxx/tpsw(Sxx)),
    'T6': lambda Sxx: np.log10(Sxx)
}

individual_spectrum_normalization_blocks = {
    'E1': lambda Sxx: Sxx,
    'E2': lambda Sxx: Sxx/Sxx.max(),
    'E3': lambda Sxx: Sxx/rms(Sxx),
    'E4': lambda Sxx: Sxx/Sxx.mean(),
}

frequency_bin_normalization_blocks = {
    'F1': lambda tst_bin, trn_bins: tst_bin,
    'F2': lambda tst_bin, trn_bins: tst_bin/trn_bins.mean(),
    'F3': lambda tst_bin, trn_bins: (tst_bin - trn_bins.mean())/trn_bins.mean(),
    'F4': lambda tst_bin, trn_bins: (tst_bin - trn_bins.mean())/rms(tst_bin - trn_bins.mean())
}
