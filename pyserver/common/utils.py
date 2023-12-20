import numpy as np
import io
from scipy.io import savemat


def stream_data(data, axis=True, unit=1, file_type="npy"):
    """
    This function is used to convert data into a byte stream,
    which can be transmitted on the network.

    Parameters:
    data: The data to be converted, usually a numpy array.
    axis: Whether to add axis
    unit: The time unit of x-axis, default is 1.
    file_type: The file type of byte stream, npy/mat
    """
    if axis:
        xAxis = np.arange(0, data.shape[1]) / unit
        data = np.vstack([xAxis, data])
    bytestream = io.BytesIO()
    if file_type == 'mat':
        data = {'DATA': data}
        savemat(bytestream, data)
    else:
        np.save(bytestream, data)
    bytestream.seek(0)
    return bytestream


def get_data(feature_ext=None, **kwargs):
    """
    This function is used to retrieve data from a selected storage based on channels
    """
    storage = kwargs['storage']
    storage_type = kwargs['modify_storage_type']
    params = kwargs['params']
    channels = params['channels']
    storage_path = params.get('storage_path')
    if storage_path == 'Feature_Ext':
        feature_ext = params.get('feature_ext', None)
    data = storage[storage_type]

    if feature_ext is not None:
        data = data[feature_ext]

    if data is None:
        return data, True
    else:
        return data[channels] if len(channels) > 0 else data, False
