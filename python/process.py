from scipy.signal import butter, filtfilt, welch, windows, resample_poly
from scipy.fft import rfft, rfftfreq
from sklearn.decomposition import FastICA
import numpy as np
import pywt


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
def butter_filter(data, btype, low, high, order=6, fs=200):
    cutoff = list(filter(lambda it: it is not None, [low, high]))
    b, a = butter(order, cutoff, btype, fs=fs)
    return filtfilt(b, a, data)


# power spectrum
def power_spectrum(data, fs=200):
    f, Pxx = welch(data, fs, nperseg=1024, detrend=False)
    return np.vstack([f, np.log10(Pxx)])


def de(data, fs=200, win=200):
    """
    data: [n*m] n:channel m time sequence
    fs: sample rate
    win: window size
    return ndarray [n*(m//win)*5]
    """
    delta = [1, 4]
    theta = [4, 8]
    alpha = [8, 14]
    beta = [14, 31]
    gamma = [31, 50]
    constant = np.log(2 * np.pi * np.e / win) / 2
    deArray = np.zeros((data.shape[0], data.shape[1] // win, 5))
    for idx, val in enumerate(data):
        t = len(val) % win
        if t:
            val = val[:-t]
        val = val.reshape(-1, win)
        seg = val * windows.get_window('hann', win)
        rfft_val = abs(rfft(seg))
        rfft_freq = rfftfreq(seg.shape[1], 1 / fs)
        points_per_freq = len(rfft_freq) / (fs / 2)
        for i, v in enumerate([delta, theta, alpha, beta, gamma]):
            start = int(points_per_freq * v[0])
            end = int(points_per_freq * v[1])
            e = np.sum(rfft_val[:, start:end] ** 2, axis=1) / (end - start + 1)
            de = np.log(e) / 2 + constant
            deArray[idx, :, i] = de
    return deArray


def frequency(data, channel, fs=200, wavename='db4', maxlevel=8):
    all_data = []
    freq_band = fs / (2 ** maxlevel)
    iter_freq = [
        {
            'name': 'Delta',
            'fmin': 1,
            'fmax': 4
        },
        {
            'name': 'Theta',
            'fmin': 4,
            'fmax': 8
        },
        {
            'name': 'Alpha',
            'fmin': 8,
            'fmax': 13
        },
        {
            'name': 'Beta',
            'fmin': 13,
            'fmax': 31
        },
        {
            'name': 'Gamma',
            'fmin': 31,
            'fmax': 50
        },
    ]

    if channel is None:
        channel = range(data.shape[0])

    for ch in channel:
        wp = pywt.WaveletPacket(data=data[ch], wavelet=wavename, mode='symmetric', maxlevel=8)
        freq_tree = [node.path for node in wp.get_level(maxlevel, 'freq')]
        single_data = []
        for it in range(len(iter_freq)):
            new_wp = pywt.WaveletPacket(data=None, wavelet=wavename, mode='symmetric', maxlevel=maxlevel)
            for i in range(len(freq_tree)):
                band_min = i * freq_band
                band_max = band_min + freq_band
                if iter_freq[it]['fmin'] <= band_min and iter_freq[it]['fmax'] >= band_max:
                    new_wp[freq_tree[i]] = wp[freq_tree[i]].data
            single_data.append(new_wp.reconstruct(update=True))
        all_data.append(single_data)
    return np.array(all_data)


def time_frequency(data, channel, fs=200, scale=20, wavename='cgau8'):
    # pywt.cwt
    fc = pywt.central_frequency(wavename)
    cparam = 2 * fc * scale
    scales = cparam / np.arange(scale, 0, -1)
    cwtmatr, frequencies = pywt.cwt(data[channel], scales, wavename, 1 / fs)

    # reverse the cwt matrix
    frequencies = np.array(frequencies)[::-1]
    cwtmatr_abs = np.abs(cwtmatr)[::-1].transpose(1, 2, 0)  # Shape: (channel, sample, freq)

    # reshape
    num_samples = cwtmatr_abs.shape[1]
    sample_indices = np.arange(num_samples) / fs
    sample_grid, freq_grid = np.meshgrid(sample_indices, frequencies, indexing='ij')  # Shape: (sample, freq)
    expanded_sample_grid = np.expand_dims(sample_grid, axis=0)
    expanded_freq_grid = np.expand_dims(freq_grid, axis=0)
    repeated_sample_grid = np.repeat(expanded_sample_grid, repeats=cwtmatr_abs.shape[0],
                                     axis=0)
    repeated_freq_grid = np.repeat(expanded_freq_grid, repeats=cwtmatr_abs.shape[0],
                                   axis=0)

    # stack along the last dimension
    temp = np.stack((repeated_sample_grid, repeated_freq_grid, cwtmatr_abs), axis=-1).astype(
        np.float32)  # Shape: (channel, sample, freq, 3)

    # flatten the middle two dimensions
    final_shape = (temp.shape[0], np.prod(temp.shape[1:-1]), temp.shape[-1])
    #  (channel, sample*freq, 3)
    return temp.reshape(final_shape)


# ICA
def ica(data):
    ica = FastICA()
    return ica.fit_transform(data.T).T
