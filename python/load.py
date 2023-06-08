import numpy as np
import pickle


def mat(data):
    for e in ['__header__', '__version__', '__globals__']:
        del data[e]
    minLen = np.min([v.shape[1] for v in data.values()])
    return np.hstack([v[:, :minLen] for v in data.values()])


def npz(data):
    return pickle.loads(data["data"]).values()


def xlsx(data):
    for table in data.sheet():
        nrows = table.nrows
        return np.array([x for j in range(nrows) for x in table.row_values(j)])