import numpy as np
from scipy.signal import resample_poly, firwin, lfilter
from sklearn.decomposition import FastICA


def re_reference(data, mode='average', channel=None):
    if mode == 'average':
        average_reference = np.mean(data, axis=0)
        return data - average_reference
    elif mode == 'channel':
        if isinstance(channel, list):
            channel = channel[0]
        return data - data[channel]
    elif mode == 'ear':
        return data - np.mean(data[channel], axis=0)


def resample(data, fs, new_fs):
    return resample_poly(data, new_fs, fs, axis=1)


# pass filter
def fir_filter(data, btype, low, high, numtaps=61, fs=200):
    cutoff = list(filter(lambda it: it is not None, [low, high]))
    b = firwin(numtaps, cutoff, pass_zero=btype, fs=fs)
    return lfilter(b, [1.0], data)


def ica(data):
    return FastICA().fit_transform(data.T).T
