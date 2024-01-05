import numpy as np
from scipy.signal import resample_poly, firwin, lfilter, butter, filtfilt
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


def resample(data, fs, new_fs, **kwargs):
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
    return resample_poly(data, new_fs, fs, axis=1, **kwargs)


# pass filter
def filters(data, btype, low, high, fs=200, filter_type='FIR', **kwargs):
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
           The length of the filter.
       fs: int
           The sample rate.

       Returns:
       numpy array
           The filtered EEG data.
       """
    default_params = {"numtaps": 61} if filter_type == 'FIR' else {"N": 6}
    default_params.update(kwargs)
    cutoff = list(filter(lambda it: it is not None, [low, high]))
    if filter_type == 'FIR':
        b = firwin(cutoff=cutoff, pass_zero=btype, fs=fs, **default_params)
        a = [1.0]
    else:
        cutoff = list(filter(lambda it: it is not None, [low, high]))
        b, a = butter(Wn=cutoff, btype=btype, fs=fs, **default_params)
    return filtfilt(b, a, data)


def ica(data, **kwargs):
    """
       Apply Independent Component Analysis (ICA) to the EEG data.

       Parameters:
       data: numpy array
           The EEG data.

       Returns:
       numpy array
           The transformed EEG data after ICA.
       """
    return FastICA(**kwargs).fit_transform(data.T).T
