def get_data(feature_ext=None, **kwargs):
    storage = kwargs['storage']
    storage_type = kwargs['modify_storage_type']
    params = kwargs['params']
    channels = params['channels']
    data = storage[storage_type]

    if feature_ext is not None:
        data = data[feature_ext]

    if data is None:
        return data, True
    else:
        return data[channels] if len(channels) > 0 else data, False
