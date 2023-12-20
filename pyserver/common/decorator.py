from marshmallow import EXCLUDE, Schema
from pyserver.common.constant import DATA_STORAGE, DATA_STORAGE_TEMPLATE
from flask import request
import copy


def init_data(schema=Schema, storage_type="Raw", storage_path='Pre_Process', source_path='Pre_Process'):
    def decorator(fuc):
        def wrapper(*args, **kwargs):
            temp_storage_type = storage_type
            temp_storage_path = storage_path
            temp_source_path = source_path
            if request.method == 'GET':
                params = request.args
            else:
                params = request.json

            try:
                if schema != Schema:
                    params = schema(unknown=EXCLUDE).load(params)
            except ValidationError as e:
                abort(400, str(e.messages))
            filename = kwargs['filename']
            DATA_STORAGE.setdefault(filename, copy.deepcopy(DATA_STORAGE_TEMPLATE))

            if params:
                print(params)
                pre_data = params.get('pre_data', 'Raw')
                temp_storage_path = params.get('storage_path', storage_path)
            else:
                pre_data = 'Raw'

            info = DATA_STORAGE[filename]['Info']
            print(temp_storage_path)
            storage = DATA_STORAGE[filename][temp_storage_path]
            source = DATA_STORAGE[filename][temp_source_path]

            if temp_storage_type == 'Plugin':
                temp_storage_path = params['plugin_type']
                temp_storage_type = kwargs['plugin']
                if params['plugin_type'] != 'Visualization':
                    storage = DATA_STORAGE[filename][temp_storage_path]

            modify_source_type = modify_storage_type = pre_data

            if request.method == 'POST' and temp_storage_path == 'Pre_Process':
                modify_storage_type = f"{pre_data}_{temp_storage_type}" if pre_data != 'Raw' else temp_storage_type

            if temp_storage_path == 'Feature_Ext':
                # modify_storage_type = pre_data
                storage.setdefault(modify_storage_type, {})
                storage[modify_storage_type].setdefault(temp_storage_type, None)
            else:
                # modify_storage_type = f"{pre_data}_{storage_type}" if pre_data != 'Raw' else storage_type
                storage.setdefault(modify_storage_type, None)

            source.setdefault(modify_source_type, None)

            return fuc(*args, info=info, storage=storage, modify_storage_type=modify_storage_type,
                       source=source[modify_source_type],
                       params=params, **kwargs)

        return wrapper

    return decorator


def init_channels(method):
    def decorator(func):
        def wrapper(*args, **kwargs):
            temp_method = method
            params = kwargs['params']
            filename = kwargs['filename']
            channels = params.get("channels")
            channel_path = DATA_STORAGE[filename]['Channels']
            if temp_method == 'Plugin':
                temp_method = kwargs['plugin']

            if request.method == 'POST' and channels is not None:
                storage_type = kwargs.get('modify_storage_type', 'Raw')
                channel_path.setdefault(storage_type, {})
                channel_path[storage_type][temp_method] = channels

            elif request.method == 'GET' and channels is not None:
                pre_data = params.get('pre_data', 'Raw')
                target = temp_method or pre_data

                try:
                    storage_channels = channel_path[pre_data][target]
                except KeyError:
                    storage_channels = channels

                try:
                    new_channels = [storage_channels.index(ch) for ch in channels]
                    params['channels'] = new_channels
                except ValueError as e:
                    abort(400, 'Includes unprocessed channels')

            return func(*args, **kwargs)

        return wrapper

    return decorator
