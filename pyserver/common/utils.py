import numpy as np
import io
from scipy.io import savemat
from pyserver.common.constant import AUTH
import re


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


def auth(req_path, req_method, api_key):
    # Define the priority level for each HTTP method
    METHODS = {
        'GET': 1,
        'POST': 2,
        'DELETE': 2
    }
    # Check if the authentication is active
    if AUTH.get('active'):
        config = AUTH.get('config', {})
        priority = config.get(api_key)
        if not priority:
            return "access denied", 401
        method_priority = METHODS.get(req_method, 0)
        # check if the method's priority is higher than the api_key's
        if isinstance(priority, int):
            if method_priority > priority:
                return "access denied", 401
        # check each path and level in the auth dictionary
        elif isinstance(priority, dict):
            for p, level in priority.items():
                if re.match(p, req_path) and method_priority > level:
                    return "access denied", 401
            if method_priority > priority.get('default', 0):
                return "access denied", 401
