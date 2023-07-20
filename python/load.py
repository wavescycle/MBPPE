import numpy as np
from scipy.io import loadmat
import pickle


def mat(file, mode='truncate'):
    data = loadmat(file)

    for e in ['__header__', '__version__', '__globals__']:
        del data[e]

    if mode == 'truncate':
        return truncate(data)
    else:
        return pad(data, mode)


def npz(file):
    return pickle.loads(file["data"]).values()


def xlsx(file):
    for table in file.sheet():
        nrows = table.nrows
        return np.array([x for j in range(nrows) for x in table.row_values(j)])


def truncate(data):
    min_len = np.min([v.shape[1] for v in data.values()])
    return np.hstack([v[:, :min_len] for v in data.values()])


def pad(data, mode):
    max_len = np.max([v.shape[1] for v in data.values()])
    padded = [np.pad(v, ((0, 0), (0, max_len - v.shape[1])), mode) for v in data.values()]
    return np.hstack(padded)
