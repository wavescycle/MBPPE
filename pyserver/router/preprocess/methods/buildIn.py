import numpy as np
from scipy.signal import resample_poly, firwin, lfilter
from sklearn.decomposition import FastICA


def re_reference(data, mode='average', channel=None):
    """
      Re-reference

      Parameters:
      data: numpy array
          The EEG data.
      mode: str
          The mode of re-referencing, including 'average', 'channel', 'ear'.
      channel: int, list
          The specific channel to use for 'channel' mode.
    """
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
    """
    Resample

    Parameters:
    data: numpy array
        The EEG data.
    fs: int
        The original sample rate.
    new_fs: int
        The new sample rate.

    Returns:
    numpy array
        The resampled EEG data.
    """
    return resample_poly(data, new_fs, fs, axis=1)


# pass filter
def fir_filter(data, btype, low, high, numtaps=61, fs=200):
    """
       Filter the EEG data using FIR filter.

       Parameters:
       data: numpy array
           The EEG data.
       btype: str
           The type of the filter, including 'lowpass', 'highpass', 'bandpass'.
       low: int, float
           The low cutoff frequency.
       high: int, float
           The high cutoff frequency.
       numtaps: int
           The length of the filter.
       fs: int
           The sample rate.

       Returns:
       numpy array
           The filtered EEG data.
       """
    cutoff = list(filter(lambda it: it is not None, [low, high]))
    b = firwin(numtaps, cutoff, pass_zero=btype, fs=fs)
    return lfilter(b, [1.0], data)


def ica(data):
    """
       Apply Independent Component Analysis (ICA) to the EEG data.

       Parameters:
       data: numpy array
           The EEG data.

       Returns:
       numpy array
           The transformed EEG data after ICA.
       """
    return FastICA().fit_transform(data.T).T
