from scipy.signal import butter, filtfilt, welch, windows
from scipy.fft import rfft, rfftfreq
from sklearn.decomposition import FastICA
import numpy as np
import pywt


# pass filter
def butter_filter(data, btype, cutoff, order=6, fs=200):
    """
    order: Order of the filter
    fs: Sampling rate
    cutoff: Cut-off frequency
    btype: {'low','high','band'}
    """
    # cutoff = list(filter(lambda it:it is not None, [low,high]))
    b, a = butter(order, cutoff, btype, fs=fs)
    return filtfilt(b, a, data)


# power spectrum
def power_spectrum(data, fs=200):
    f, Pxx = welch(data, fs, nperseg=1024, detrend=False)
    return np.vstack([f, np.log10(Pxx)])


def de(data, fs=200, win=200):
    '''
    data: [n*m] n:channel m time sequence
    fs: sample rate
    win: window size
    return ndarray [n*(m//win)*5]
    '''
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
            e = np.sum(rfft_val[:, start:end]**2, axis=1) / (end - start + 1)
            de = np.log(e) / 2 + constant
            deArray[idx, :, i] = de
    return deArray


# def heatMap(data, start=0, during=1, fs=200):
#     axis = [[]]

#     windows = during * fs
#     start_time = start * 200
#     end_time = start_time + windows
#     temp = data[:, start_time:end_time]
#     temp = np.mean(temp, axis=1)


def frequence(data,
              channel,
              start=0,
              end=10,
              fs=200,
              wavename='db4',
              maxlevel=8):
    data = data[channel]
    wp = pywt.WaveletPacket(data=data,
                            wavelet=wavename,
                            mode='symmetric',
                            maxlevel=8)
    freqTree = [node.path for node in wp.get_level(maxlevel, 'freq')]
    freqBand = fs / (2**maxlevel)
    iter_freqs = [
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
    data_list = []
    for iter in range(len(iter_freqs)):
        new_wp = pywt.WaveletPacket(data=None,
                                    wavelet=wavename,
                                    mode='symmetric',
                                    maxlevel=maxlevel)
        for i in range(len(freqTree)):
            bandMin = i * freqBand
            bandMax = bandMin + freqBand
            if (iter_freqs[iter]['fmin'] <= bandMin
                    and iter_freqs[iter]['fmax'] >= bandMax):
                new_wp[freqTree[i]] = wp[freqTree[i]].data
        data_list.append(new_wp.reconstruct(update=True))
    return np.array(data_list)


def time_frequence(data,
                   channel,
                   start=0,
                   end=10,
                   fs=200,
                   scale=20,
                   wavename='cgau8'):
    fc = pywt.central_frequency(wavename)
    cparam = 2 * fc * scale
    scales = cparam / np.arange(scale, 0, -1)
    # scales = cparam / np.arange(scale, 1)
    cwtmatr, frequencies = pywt.cwt(data[channel][start * fs:end * fs], scales,
                                    wavename, 1 / fs)

    # reverse the cwt matrix
    frequencies = np.array(frequencies)[::-1]
    cwtmatr = abs(cwtmatr)[::-1].T
    maxValue = np.max(cwtmatr)
    # [time,frequence,data]
    return np.array([[x / 200 + start, frequencies[y], v]
                     for x, val in enumerate(cwtmatr)
                     for y, v in enumerate(val)],
                    dtype=np.float32), int(maxValue)


# ICA
def ica(data):
    ica = FastICA()
    return ica.fit_transform(data.T).T
